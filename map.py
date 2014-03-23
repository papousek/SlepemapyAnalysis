# -*- coding: utf-8 -*-

from analysis import *
from kartograph import Kartograph
        
'''used for drawing maps
'''
class Map(Analysis):
    
    ''' -path to current working directory
        -codes is dataframe with country IDs and their respective ISO numbers+land areas in km squared
    '''
    def __init__(self,path,codes,df,user=None,place_asked=None,response_time_threshold=60000,lower_bound = 50,upper_bound = 236,session_duration= np.timedelta64(30, 'm')):
        Analysis.__init__(self,df,user,place_asked,response_time_threshold,lower_bound,upper_bound,session_duration)
        
        self.current_dir = path
        self.k = Kartograph()
        self.codes = codes
        self.config ={
            "layers": {
                "states": {    
                    "src": self.current_dir+"/base/ne_110m_admin_0_countries.shp",
                    "filter": ["continent", "in", ["Europe","Asia","Africa","South America","Oceania","North America"]],
                    "class": "states"
                    }
                }
            }

    '''data represents list with names, colourarray colours
    '''
    def _generate_csv(self,colours):
        with open(self.current_dir+'/base/style.css','w+') as csv:
            colours.apply(lambda x: csv.write('.states[iso_a2='+self.codes[self.codes.id==x.country]['code'].values[0].upper()+'] {\n\tfill: '+x.colour+'\n}\n'),axis=1)

    @staticmethod
    def _draw_gradient_scale(data,path,name=''):
        with open(path,'r+') as svg:
            minimum = min(data)
            maximum = max(data)
            onethird = (maximum-minimum)/3
            svg.seek(-6,2) #skip to the position right before </svg> tag
            svg.write('<defs>  <linearGradient id=\"grad2\" x1=\"0%\" y1=\"0%\" x2=\"100%\" y2=\"0%\">\n      <stop offset=\"0%\" style=\"stop-color:rgb(255,255,0);stop-opacity:1\" />\n      <stop offset=\"100%\" style=\"stop-color:rgb(255,0,0);stop-opacity:1\" />\n    </linearGradient>\n  </defs>\n  <rect x=\"610\" y=\"375\" height=\"25\" width=\"175\" fill=\"url(#grad2)\" />\n  \n<text x=\"610\" y=\"365\" font-family=\"sans-serif\" font-size=\"11\" fill=\"black\">' +str(int(minimum))+ '</text>\n  <line x1=\"613\" y1=\"368\" x2=\"613\" y2=\"388\"/>\n\n<text x=\"665\" y=\"365\" font-family=\"sans-serif\" font-size=\"11\" fill=\"black\">' +str(int(onethird))+ '</text>\n  <line x1=\"672\" y1=\"368\" x2=\"672\" y2=\"388\"/>\n\n  <text x=\"720\" y=\"365\" font-family=\"sans-serif\" font-size=\"11\" fill=\"black\">' +str(int(onethird*2))+ '</text>\n  <line x1=\"727\" y1=\"368\" x2=\"727\" y2=\"388\"/>\n\n<text x=\"775\" y=\"365\" font-family=\"sans-serif\" font-size=\"11\" fill=\"black\">' +str(int(maximum))+ '</text>\n  <line x1=\"782\" y1=\"368\" x2=\"782\" y2=\"388\"/>\n\n  <text x=\"610\" y=\"415\" font-family=\"sans-serif\" font-size=\"15\" fill=\"black\">' +name+'</text></svg>')
    
    def number_of_answers(self,draw_legend=True):
        data = self._number_of_answers()
        if not data.empty:
            colours = Analysis.colour_range(data)
            self._generate_csv(colours)
    
            with open(self.current_dir+'/base/style.css') as css:
                self.k.generate(self.config,outfile=self.current_dir+'/maps/numberofanswers.svg',stylesheet=css.read())
            if draw_legend:
                self._draw_gradient_scale(data,self.current_dir+'/maps/numberofanswers.svg',u'Pocty odpovedi')
    
    def response_time(self,draw_legend=True):
        data = self._response_time_place()
        if not data.empty:
            colours = Analysis.colour_range(data)
            self._generate_csv(colours)
    
            with open(self.current_dir+'/base/style.css') as css:
                self.k.generate(self.config,outfile=self.current_dir+'/maps/responsetime.svg',stylesheet=css.read())
            if draw_legend:
                self._draw_gradient_scale(data,self.current_dir+'/maps/responsetime.svg',u'Rychlost odpovede')