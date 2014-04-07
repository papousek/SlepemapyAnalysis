# -*- coding: utf-8 -*-

import analysis
import bin_operations
from drawable import *

from kartograph import Kartograph
from datetime import datetime
import codecs



class Map(Drawable):

    '''Draws world map by default. All other defaults are same as in Drawable.
    '''
    def __init__(self,path='',codes=None,df=None,user=None,place_asked=None,response_time_threshold=60000,lower_bound = 50,upper_bound = 236,session_duration= np.timedelta64(30, 'm'),add_session_numbers=False):
        Drawable.__init__(self,path,codes,df,user,place_asked,response_time_threshold,lower_bound,upper_bound,session_duration,add_session_numbers)

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
    
    
    '''Generates css for coloring in countries.
    
    data -- df with columns [country,r,g,b], where country is an ID and rgb are colour values
    path -- output directory
    optional_css -- append additional css at the end of the calculated css-- default is ''
    '''
    def generate_css(self,data,path,optional_css=''):
        with open(path,'w+') as css:
            if not data.empty: 
                data.apply(lambda x: css.write('.states[iso_a2='+self.codes[self.codes.id==x.country]['code'].values[0].upper()+'] {\n\tfill: '+bin_operations.colour_value_rgb_string(x.r,x.g,x.b)+';\n}\n'),axis=1)
            if optional_css:
                optional = open(optional_css,'r')
                css.write(optional.read())
   
   
    '''Draws bins into svg.
    
    data -- data with columns [label,r,g,b] where label is text next to the bin and rgb are colour values
    path -- path to svg
    x -- starting x position of the legend
    y -- starting y position of the legend
    bin_width -- width of each individual bin -- default is 15
    font_size -- font size of labels -- default is 12
    '''
    @staticmethod
    def draw_bins(data,path,x=5,y=175,bin_width=15,font_size=12):
        with codecs.open(path,'r+','utf-8') as svg:
            svg.seek(-6,2) #skip to the position right before </svg> tag
            svg.write('<g transform = \"translate('+str(x)+' '+str(y)+')\">\n') #group
            for i in range(len(data)):
                svg.write(  '<rect x=\"0\" y=\"'+str((i+1)*bin_width)+
                            '\" width=\"'+str(bin_width)+'\" height=\"'+str(bin_width)+
                            '" fill='+bin_operations.colour_value_rgb_string(data.r.values[i],data.g.values[i],data.b.values[i])+ '/>\n')
                svg.write(  '<text x=\"20\" y=\"'+str((i+1)*bin_width+11)+
                            '\" stroke=\"none\" fill=\"black\" font-size=\"'+str(font_size)+
                            '" font-family=\"sans-serif\">'+data.label.values[i]+'</text>\n')
            svg.write('</g>\n</svg>') #group
    
    
    '''Draws title into svg.
    
    path -- path to svg
    title -- text do input into picture
    x -- starting x position of the title
    y -- starting y position of the title
    font_size -- font size of labels -- default is 20
    colour -- title colour
    '''
    @staticmethod
    def draw_title(path,title='',x=400,y=410,font_size=20,colour='black'):
        with codecs.open(path,'r+','utf-8') as svg:
            svg.seek(-6,2)
            svg.write(  '<text x =\"'+str(x)+'\" y=\"'+str(y)+'\" stroke=\"none\" font-size=\"'+
                        str(font_size)+'\" fill=\"'+colour+'\" font-family=\"sans-serif\">'+
                        title+'</text>\n</svg>')
    
    
    '''General drawing method through kartograph. Looks for css in current_dir+'/base/style.css' for styling css.
    
    path -- output directory
    title -- name of map
    '''
    def draw_map(self,path,title='',colours=None):
        with open(self.current_dir+'/base/style.css') as css:
            self._k.generate(self.config,outfile=path,stylesheet=css.read())
        if colours is not None:
            self.draw_bins(colours,path) 
        if title:
            self.draw_title(path,title)
    ############################################################################
    
    
    ''' Draws map of most mistaken countries for this specific one
    
    binning_function -- which function to use for binning -- default is None (-> jenks_classification)
    path -- output directory -- default is '' (current dir)
    title -- name of the map -- default is 'Mistaken countries'
    number_of_bins -- how many bins to divide data into-- default is 6
    '''
    def mistaken_countries(self,binning_function=None,path='',title='Mistaken countries',number_of_bins=6):
        if not path:
            path = self.current_dir+'/maps/mistakencountries.svg'

        data = analysis.mistaken_countries(self.frame)
        colours = None
        if not (data.empty or self.place_asked is None):
            picked = bin_operations.colour_value_hsv(0.54)
            place = pd.DataFrame([[self.place_asked,picked[0],picked[1],picked[2]]],columns=['country','r','g','b'])
            (data,colours) = bin_operations.bin_data(data,binning_function,number_of_bins,additional_countries=place,additional_labels=[self.get_country_name(self.place_asked)])
            self.generate_css(data[['country','r','g','b']],path=self.current_dir+'/base/style.css')

        self.draw_map(path,title,colours)


    '''Draws map of total number of answers per country.
    
    binning_function -- which function to use for binning -- default is None (-> jenks_classification)
    path -- output directory -- default is '' (current dir)
    title -- name of the map -- default is 'Number of answers'
    number_of_bins -- how many bins to divide data into-- default is 6
    '''
    def number_of_answers(self,binning_function=None,path='',title='Number of answers',number_of_bins=6):
        if not path:
            path = self.current_dir+'/maps/numberofanswers.svg'

        data = analysis.number_of_answers(self.frame)
        colours = None
        if not data.empty:
            (data,colours) = bin_operations.bin_data(data,binning_function,number_of_bins)
            self.generate_css(data[['country','r','g','b']],path=self.current_dir+'/base/style.css')

        self.draw_map(path,title,colours)
    
    
    '''Draws map of mean response time per country.
    
    binning_function -- which function to use for binning -- default is None (-> jenks_classification)
    path -- output directory -- default is '' (current dir)
    title -- name of the map -- default is 'Response time'
    number_of_bins -- how many bins to divide data into-- default is 6
    '''
    def response_time(self,binning_function=None,path='',title='Response time',number_of_bins=6):
        if not path:
            path = self.current_dir+'/maps/responsetime.svg'

        data = analysis.response_time_place(self.frame)
        colours = None
        if not data.empty:
            (data,colours) = bin_operations.bin_data(data,binning_function,number_of_bins)
            self.generate_css(data[['country','r','g','b']],path=self.current_dir+'/base/style.css')

        self.draw_map(path,title,colours)


    '''Draws map of mean success rate per country.
    
    binning_function -- which function to use for binning -- default is None (-> jenks_classification)
    path -- output directory -- default is '' (current dir)
    title -- name of the map -- default is 'Average success rate'
    number_of_bins -- how many bins to divide data into-- default is 6
    '''
    def mean_success_rate(self,binning_function=None,path='',title='Average success rate',number_of_bins=6):
        if not path:
            path = self.current_dir+'/maps/avgsuccess.svg'
        data = analysis.mean_success_rate(self.frame)['mean_success_rate']

        colours = None
        if not data.empty:
            (data,colours) = bin_operations.bin_data(data,binning_function,number_of_bins)
            self.generate_css(data[['country','r','g','b']],path=self.current_dir+'/base/style.css')

        self.draw_map(path,title,colours)   