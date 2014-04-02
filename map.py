# -*- coding: utf-8 -*-

from analysis import *
from kartograph import Kartograph
from drawer import Drawer
from datetime import datetime
import sys

'''used for drawing maps
'''
class Map(Analysis,Drawer):

    def __init__(self,path,df=None,codes=None,user=None,place_asked=None,response_time_threshold=60000,lower_bound = 50,upper_bound = 236,session_duration= np.timedelta64(30, 'm')):
        Analysis.__init__(self,df,user,place_asked,response_time_threshold,lower_bound,upper_bound,session_duration)
        Drawer.__init__(self,path,codes)

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
    
    def generate_css(self,data,path='',optional_css=''):
        if not path:
            path = self.current_dir+'/base/style.css'
        with open(path,'w+') as css:
            if not data.empty: 
                data.apply(lambda x: css.write('.states[iso_a2='+self.codes[self.codes.id==x.country]['code'].values[0].upper()+'] {\n\tfill: '+Drawer.colour_value_rgb_string(x.r,x.g,x.b)+';\n}\n'),axis=1)
            if optional_css:
                optional = open(optional_css,'r')
                css.write(optional.read())

    @staticmethod
    def _create_labels(bins):
        bins[0]+=1 #corrections for bins
        bins[-1]-=1
        bins = [round(x,2) for x in bins]
        labels = ['('+str(bins[curr])+', '+str(bins[curr+1])+']' for curr in range(len(bins)-1)]
        labels.reverse()
        return labels

    @staticmethod
    def _nested_means_classification(data,num):
        if num<=0 or data.empty:
            return []
        mean = data.mean()
        return [mean]+Map._nested_means_classification(data[data<mean],num-1)+Map._nested_means_classification(data[data>=mean],num-1)
    
    '''nested-mean classification,classes should be a number that is power of 2
    '''
    @staticmethod
    def nested_means_classification(data,classes=4):
        if len(data)<classes:
            return [data.min()-1,data.max()+1]
        breaks = [data.min()-1,data.max()+1]+Map._nested_means_classification(data,np.log2(classes))
        breaks.sort()
        return breaks
    
    @staticmethod
    def equidistant_classification(data,classes=4):
        x = (data.max() - data.min())/classes
        breaks = [data.min()-1,data.max()+1]+[i*x for i in range(1,classes)]
        breaks.sort()
        return breaks
    
    @staticmethod
    def jenks_classification(data, classes=4) :
        input = data.copy()
        input.sort()
        input = input.tolist()
        length = len(data)
        
        #define initial values of the LC and OP 
        lower_class_limits = [[1 for x in range(0,classes+1)] if y==0 else [0 for x in range(0,classes+1)] for y in range(0,length+1)] #LC
        variance_combinations = [[0 for x in range(0,classes+1)] if y==0 else [sys.maxint for x in range(0,classes+1)] for y in range(0,length+1)] #OP
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

        breaks.sort()
        return breaks

    @staticmethod
    def bin_data(data,binning_function,number_of_bins=6,draw_legend=True,additional_countries=None,additional_labels=[]):
        binned = pd.DataFrame(data)
        binned = binned.reset_index()
        binned.columns=['country','counts']

        bins = binning_function(binned['counts'],number_of_bins)
        binned['bin'] = pd.cut(binned['counts'], bins=bins,labels=False)
        colours = Drawer.colour_range(len(bins)-1)
        binned['r'] = binned.bin.apply(lambda x: colours[x][0])
        binned['g'] = binned.bin.apply(lambda x: colours[x][1])
        binned['b'] = binned.bin.apply(lambda x: colours[x][2])
        binned = binned.append(additional_countries)

        if draw_legend:
            colours.reverse()
            colours = pd.DataFrame(colours)
            if additional_countries is not None:
                colours = colours.append([[additional_countries.r.values[0],additional_countries.g.values[0],additional_countries.b.values[0]]],ignore_index=True)         
            colours = colours.append([Drawer.colour_value_hsv(0,s=0)]) #special colour for No data bin
            colours.columns = ['r','g','b']
            colours['label'] = Map._create_labels(bins)+additional_labels+['No data']
        else:
            colours = None
        return (binned,colours)
        
    def draw_map(self,path,title='',colours=None):
        with open(self.current_dir+'/base/style.css') as css:
            self._k.generate(self.config,outfile=path,stylesheet=css.read())
        if colours is not None:
            self.draw_bins_naive(colours,path) 
        if title:
            self.draw_title(path,title)
    ############################################################################
    def mistaken_countries(self,binning_function=None,draw_legend=True,path='',title='Mistaken countries',number_of_bins=6):
        if not path:
            path = self.current_dir+'/maps/mistakencountries.svg'
        if not binning_function:
            binning_function = Map.jenks_classification

        data = self._mistaken_countries()
        colours = None
        if not (data.empty or self.place_asked is None):
            picked = Drawer.colour_value_hsv(0.54)
            place = pd.DataFrame([[self.place_asked,picked[0],picked[1],picked[2]]],columns=['country','r','g','b'])
            (data,colours) = Map.bin_data(data,binning_function,number_of_bins,draw_legend,additional_countries=place,additional_labels=[self.get_country_name(self.place_asked)])
            self.generate_css(data[['country','r','g','b']])

        self.draw_map(path,title,colours)

    def number_of_answers(self,binning_function=None,draw_legend=True,path='',title='Number of answers',number_of_bins=6):
        if not path:
            path = self.current_dir+'/maps/numberofanswers.svg'
        if not binning_function:
            binning_function = Map.jenks_classification

        data = self._number_of_answers()
        colours = None
        if not data.empty:
            (data,colours) = Map.bin_data(data,binning_function,number_of_bins,draw_legend)
            self.generate_css(data[['country','r','g','b']])

        self.draw_map(path,title,colours)
    
    def response_time(self,binning_function=None,draw_legend=True,path='',title='Response time',number_of_bins=6):
        if not path:
            path = self.current_dir+'/maps/responsetime.svg'
        if not binning_function:
            binning_function = Map.jenks_classification

        data = self._response_time_place()
        colours = None
        if not data.empty:
            (data,colours) = Map.bin_data(data,binning_function,number_of_bins,draw_legend)
            self.generate_css(data[['country','r','g','b']])

        self.draw_map(path,title,colours)

    def avg_success(self,binning_function=None,draw_legend=True,path='',title='Average success rate',number_of_bins=6):
        if not path:
            path = self.current_dir+'/maps/avgsuccess.svg'
        if not binning_function:
            binning_function = Map.jenks_classification
        data = self._avg_success_by_place()['mean_success_rate']

        colours = None
        if not data.empty:
            (data,colours) = Map.bin_data(data,binning_function,number_of_bins,draw_legend)
            self.generate_css(data[['country','r','g','b']])

        self.draw_map(path,title,colours)   
    
    def avg_success_by_session(self):
        data = Map(self.current_dir,codes=self.codes)
        maximum = self.frame.session_number.max()
        for i in range(0,maximum+1):
            data.set_frame(self.frame[self.frame.session_number<=i])
            filename = self.current_dir+'animations/map '+str(i+1)+' of '+str(maximum+1)+'.svg'
            data.avg_success(draw_legend=False,path=filename)