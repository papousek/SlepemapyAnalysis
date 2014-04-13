# -*- coding: utf-8 -*-

from drawable import *
import analysis

import pandas as pd
import numpy as np

from sys import maxint
import colorbrewer
from codecs import open as copen
from kartograph import Kartograph


#Helper functions for bin classification

def _nested_means_classification(data,num):
    """recursive helper function of nested-means
    """

    if num<=0 or data.empty:
        return []
    breaks = [data.mean()]+_nested_means_classification(data[data<mean],num-1)+_nested_means_classification(data[data>=mean],num-1)
    breaks = list(set(breaks)) #drop duplicate bins
    breaks.sort()
    return breaks


def nested_means_classification(data,classes=8):
    """Data is divided by nested-means.

    :param data: values to bin
    :param classes: divide values into this many bins, should be a power of 2
    """

    if len(data)<classes:
        return [data.min()-1,data.max()+1]
    breaks = [data.min()-1,data.max()+1]+_nested_means_classification(data,np.log2(classes))
    breaks = list(set(breaks)) #drop duplicate bins
    breaks.sort()
    return breaks


def equidistant_classification(data,classes=8):
    """Data is divided by equally distant ranges.

    :param data: values to bin
    :param classes: divide values into this many bins
    """

    x = (data.max() - data.min())/classes
    breaks = [data.min()-1,data.max()+1]+[i*x for i in range(1,classes)]
    breaks = list(set(breaks)) #drop duplicate bins
    breaks.sort()
    return breaks


def jenks_classification(data, classes=8):
    """Port of original javascript implementation by Tom MacWright from https://gist.github.com/tmcw/4977508
    
    Data is divided by jenks algorithm.

    :param data: values to bin
    :param classes: divide values into this many bins
    """

    input = data.copy()
    input.sort()
    input = input.tolist()
    length = len(data)
    
    #define initial values of the LC and OP 
    lower_class_limits = [[1 for x in range(0,classes+1)] if y==0 else [0 for x in range(0,classes+1)] for y in range(0,length+1)] #LC
    variance_combinations = [[0 for x in range(0,classes+1)] if y==0 else [maxint for x in range(0,classes+1)] for y in range(0,length+1)] #OP
    variance = 0

    #calculate optimal LC
    for i in range(1,length):
        sum = 0 #SZ
        sum_squares = 0 #ZSQ
        counter = 0 #WT

        for j in range(0,i+1):
            i3 = i - j + 1 #III
            value = input[i3-1]
            counter+=1 #WT

            sum += value
            sum_squares += value * value
            variance = sum_squares - (sum * sum) / counter
            i4 = i3 - 1 #IV
            
            if (i4 != 0) :
                for k in range(0,classes+1):
                    #deciding whether an addition of this element will increase the class variance beyond the limit
                    #if it does, break the class
                    if (variance_combinations[i][k] >= (variance + variance_combinations[i4][k - 1])) :
                        lower_class_limits[i][k] = i3
                        variance_combinations[i][k] = variance + variance_combinations[i4][k - 1]
        lower_class_limits[i][1] = 1
        variance_combinations[i][1] = variance #we can use variance_combinations in calculations of goodness-of-fit, but we do not need it right now
    
    #create breaks
    length -= 1
    breaks = []
    breaks.append(input[0]-1) #append lower bound that was not found during calculations
    breaks.append(input[length]+1) #append upper bound that was not found during calculations
    while (classes > 1):
        breaks.append(input[lower_class_limits[length][classes] - 2])
        length = lower_class_limits[length][classes] -1
        classes-=1
    
    breaks = list(set(breaks)) #drop duplicate bins
    breaks.sort()
    return breaks


class Map(Drawable):
    
    def __init__(   self, path='',codes=None, difficulties = None, df=None, user=None, place_asked=None,
                    lower_bound = 50, upper_bound = 236, session_numbers=True):
        """Draws world map by default. All other defaults are same as in Drawable.
        """

        Drawable.__init__(self,path,codes,difficulties,df,user,place_asked,lower_bound,upper_bound,session_numbers)

        config ={
            "layers": {
                "states": {    
                    "src": self.current_dir+"/base/ne_110m_admin_1_countries/ne_110m_admin_0_countries.shp",
                    "filter": ["continent", "in", ["Europe","Asia","Africa","South America","Oceania","North America"]],
                    "class": "states"
                }
            }
        }
        self.set_config(config)
        self._k = Kartograph()


    def set_config(self,config):
        self.config = config

    
    @staticmethod
    def bin_data(data,binning_function=None,number_of_bins=6,reverse_colours=False,additional_countries=None,additional_labels=[]):
        """Combines classification methods with colouring, returns binned data with assigned colours
    
        :param data: values to bin
        :param binning_function: which function to use for binning -- default is None (-> jenks_classification)
        :param number_of_bins: how many bins to divide data-- default is 6
        :param reverse_colours: whether to reverse generated color scheme
        :param additional_countries: whether to add additional countries AFTER binning -- default is None
        :param additional_labels: whether to add additional labels AFTER calculations -- default is []
        :param colours: use these colours instead of predefined ones

        """
    
        if binning_function is None:
            binning_function = jenks_classification
        binned = pd.DataFrame(data)
        binned = binned.reset_index()
        binned.columns=['country','counts']
    
        bins = binning_function(binned['counts'],number_of_bins)
        binned['bin'] = pd.cut(binned['counts'], bins=bins,labels=False)
        
        colours = colorbrewer.YlOrRd[len(bins)-1] #default color range from colorbrewer
        if reverse_colours:
            colours.reverse()
        binned['rgb'] = binned.bin.apply(lambda x: colours[x])

        binned = binned.append(additional_countries)
    
        colours.reverse()
        colours = pd.DataFrame(zip(colours))
        if additional_countries is not None:
            colours = colours.append([[additional_countries.rgb.values[0]]],ignore_index=True)         
        colours = colours.append([[(255,255,255)]],ignore_index=True) #white for No data bin
        colours.columns = ['rgb']
        colours['label'] = Map.bins_to_string(bins)+additional_labels+['No data']
        return (binned,colours)

    
    @staticmethod
    def bins_to_string(bins):
        """ Returns list of strings from the bins in the interval form: (lower,upper]
    
        :param bins: bins to get strings from
        """
    
        bins[0]+=1 #corrections for bins
        bins[-1]-=1
        bins = [round(x,2) for x in bins]
        labels = ['('+str(bins[curr])+', '+str(bins[curr+1])+']' for curr in range(len(bins)-1)]
        labels.reverse()
        return labels


    def generate_css(self,data,path,optional_css=''):
        """Generates css for coloring in countries.
    
        :param data: df with columns [country,rgb], where country is an ID and rgb are colour values
        :param path: output directory
        :param optional_css: append additional css at the end of the calculated css-- default is ''
        """

        with open(path,'w+') as css:
            if not data.empty: 
                data.apply(lambda x: 
                css.write('.states[iso_a2='+self.codes[self.codes.id==int(x.country)]['code'].values[0].upper()+']'+
                '{\n\tfill: '+self.colour_value_rgb_string(x.rgb[0],x.rgb[1],x.rgb[2])+';\n}\n'),axis=1)
            if optional_css:
                optional = open(optional_css,'r')
                css.write(optional.read())
   
   
    @staticmethod
    def colour_value_rgb_string(r,g,b):
        """Returns string in format 'rgb(r,g,b)'.
        """
    
        return '\'rgb('+str(int(r))+', '+str(int(g))+', '+str(int(b))+')\''    

    
    @staticmethod
    def draw_bins(data,path,x=5,y=175,bin_width=15,font_size=12):
        """Draws bins into svg.
    
        :param data: data with columns [label,r,g,b] where label is text next to the bin and rgb are colour values
        :param path: path to svg
        :param x: starting x position of the legend
        :param y: starting y position of the legend
        :param bin_width: width of each individual bin -- default is 15
        :param font_size: font size of labels -- default is 12
        """

        with copen(path,'r+','utf-8') as svg:
            svg.seek(-6,2) #skip to the position right before </svg> tag
            svg.write('\n<g transform = \"translate('+str(x)+' '+str(y)+')\">\n') #group
            for i in range(len(data)):
                svg.write(  '<rect x=\"0\" y=\"'+str((i+1)*bin_width)+
                            '\" width=\"'+str(bin_width)+'\" height=\"'+str(bin_width)+
                            '" fill='+Map.colour_value_rgb_string(data.rgb.values[i][0],data.rgb.values[i][1],data.rgb.values[i][2])+ '/>\n')
                svg.write(  '<text x=\"20\" y=\"'+str((i+1)*bin_width+11)+
                            '\" stroke=\"none\" fill=\"black\" font-size=\"'+str(font_size)+
                            '" font-family=\"sans-serif\">'+data.label.values[i]+'</text>\n')
            svg.write('</g>\n</svg>') #group
    
    
    @staticmethod
    def draw_title(path,title='',x=400,y=410,font_size=20,colour='black'):
        """Draws title into svg.
    
        :param path: path to svg
        :param title: text do input into picture
        :param x: starting x position of the title
        :param y: starting y position of the title
        :param font_size: font size of labels -- default is 20
        :param colour: title colour
        """

        with copen(path,'r+','utf-8') as svg:
            svg.seek(-6,2)
            svg.write(  '\n<text x =\"'+str(x)+'\" y=\"'+str(y)+'\" stroke=\"none\" font-size=\"'+
                        str(font_size)+'\" fill=\"'+colour+'\" font-family=\"sans-serif\">'+
                        title+'</text>\n</svg>')
    
    
    def draw_map(self,path,title='',colours=None):
        """General drawing method through kartograph. Looks for css in current_dir+'/base/style.css' for styling css.
    
        :param path: output directory
        :param title: name of map
        :param colours: dataframe with colours for bins -- default is None
        """

        with open(self.current_dir+'/base/style.css') as css:
            self._k.generate(self.config,outfile=path,stylesheet=css.read())
        if colours is not None:
            self.draw_bins(colours,path) 
        if title:
            self.draw_title(path,title)

    ############################################################################
    
    
    def mistaken_countries(self,binning_function=None,path='',number_of_bins=6):
        """ Draws map of most mistaken countries for this specific one
    
        :param binning_function: which function to use for binning -- default is None (-> jenks_classification)
        :param path: output directory -- default is '' (current dir)
        :param number_of_bins: how many bins to divide data into-- default is 6
        """

        if not path:
            path = self.current_dir+'/maps/mistakencountries.svg'

        data = analysis.mistaken_countries(self.frame)
        colours = None
        if not (data.empty or self.place_asked is None):
            place = pd.DataFrame([[self.place_asked,(0,255,255)]],columns=['country','rgb'])
            (data,colours) = self.bin_data(data,binning_function,number_of_bins,additional_countries=place,additional_labels=[self.get_country_name(self.place_asked)])
            self.generate_css(data[['country','rgb']],path=self.current_dir+'/base/style.css')

        self.draw_map(path,'Mistaken countries',colours)


    def predict_success(self,binning_function=None,path='',number_of_bins=6):
        """Draws map of total number of answers per country.
    
        :param binning_function: which function to use for binning -- default is None (-> jenks_classification)
        :param path: output directory -- default is '' (current dir)
        :param number_of_bins: how many bins to divide data into-- default is 6
        """

        if not path:
            path = self.current_dir+'/maps/predictsuccess.svg'
        data = analysis.predict_success_average(self.difficulties)
        colours = None

        if not data.empty:
            (data,colours) = self.bin_data(data,binning_function,number_of_bins,reverse_colours=True)
            self.generate_css(data[['country','rgb']],path=self.current_dir+'/base/style.css')

        self.draw_map(path,'Prediction of a success for average user',colours)


    def number_of_answers(self,binning_function=None,path='',number_of_bins=6):
        """Draws map of total number of answers per country.
    
        :param binning_function: which function to use for binning -- default is None (-> jenks_classification)
        :param path: output directory -- default is '' (current dir)
        :param number_of_bins: how many bins to divide data into-- default is 6
        """

        if not path:
            path = self.current_dir+'/maps/numberofanswers.svg'

        data = analysis.number_of_answers(self.frame)
        colours = None
        if not data.empty:
            (data,colours) = self.bin_data(data,binning_function,number_of_bins)
            self.generate_css(data[['country','rgb']],path=self.current_dir+'/base/style.css')

        self.draw_map(path,'Number of answers',colours)
    
    
    def response_time(self,binning_function=None,path='',number_of_bins=6):
        """Draws map of mean response time per country.
    
        :param binning_function: which function to use for binning -- default is None (-> jenks_classification)
        :param path: output directory -- default is '' (current dir)
        :param number_of_bins: how many bins to divide data into-- default is 6
        """

        if not path:
            path = self.current_dir+'/maps/responsetime.svg'

        data = analysis.response_time_place(self.frame)
        colours = None
        if not data.empty:
            (data,colours) = self.bin_data(data,binning_function,number_of_bins)
            self.generate_css(data[['country','rgb']],path=self.current_dir+'/base/style.css')

        self.draw_map(path,'Response time',colours)


    def mean_success(self,binning_function=None,path='',number_of_bins=6):
        """Draws map of mean success rate per country.
    
        :param binning_function: which function to use for binning -- default is None (-> jenks_classification)
        :param path: output directory -- default is '' (current dir)
        :param number_of_bins: how many bins to divide data into-- default is 6
        """

        if not path:
            path = self.current_dir+'/maps/meansuccess.svg'
        data = analysis.mean_success(self.frame)
        colours = None
        
        if not data.empty:
            (data,colours) = self.bin_data(data,binning_function,number_of_bins,reverse_colours=True)
            self.generate_css(data[['country','rgb']],path=self.current_dir+'/base/style.css')

        self.draw_map(path,'Mean success rate',colours)  