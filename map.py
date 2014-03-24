# -*- coding: utf-8 -*-

from analysis import *
from kartograph import Kartograph
from xml.dom import minidom
from mystringio import MyStringIO
import codecs

'''used for drawing maps
'''
class Map(Analysis):
    
    ''' -path to current working directory
        -codes is dataframe with country IDs and their respective ISO numbers+land areas in km squared
    '''
    def __init__(self,path,df=None,codes=None,user=None,place_asked=None,response_time_threshold=60000,lower_bound = 50,upper_bound = 236,session_duration= np.timedelta64(30, 'm')):
        Analysis.__init__(self,df,user,place_asked,response_time_threshold,lower_bound,upper_bound,session_duration)
        
        self.codes = codes
        self.current_dir = path
        self.k = Kartograph()
        self.config ={
            "layers": {
                "states": {    
                    "src": self.current_dir+"/base/ne_110m_admin_0_countries.shp",
                    "filter": ["continent", "in", ["Europe","Asia","Africa","South America","Oceania","North America"]],
                    "class": "states"
                }
            }
        }
    
    ############################################################################
    '''data is df with cols country,colour
    '''
    def _generate_csv(self,data):
        with open(self.current_dir+'/base/style.css','w+') as csv:
            data.apply(lambda x: csv.write('.states[iso_a2='+self.codes[self.codes.id==x.country]['code'].values[0].upper()+'] {\n\tfill: '+x.colour+'\n}\n'),axis=1)
    
    @staticmethod
    def _draw_bins_dom(data,kmap,x,y,bin_width=15,font_size=12):
        root = minidom.parseString(kmap.getvalue())
        group = root.createElement("g")
        group.setAttribute('transform','translate('+str(x)+' '+str(y)+')')

        for i in range(0,len(data)):
            rect = root.createElement("rect")
            rect.setAttribute('x','0')
            rect.setAttribute('y',str((i+1)*bin_width))
            rect.setAttribute('width',str(bin_width))
            rect.setAttribute('height',str(bin_width))
            rect.setAttribute('fill',data.values[i][1][1:-2])
            group.appendChild(rect)
            
            '''label = root.createElement(root.createTextNode(data.values[i][2])
            label.setAttribute('x','20')
            label.setAttribute('y',str((i+1)*bin_width+11))
            label.setAttribute('stroke','none')
            label.setAttribute('font-family','sans-serif')
            label.setAttribute('fill','black')
            label.setAttribute('font-size',str(font_size))
            group.appendChild(label)'''

        svg = root.getElementsByTagName('svg')[0]
        svg.appendChild(group)
        root.writexml(kmap)

    @staticmethod
    def _draw_bins_naive(data,path,x,y,bin_width=15,font_size=12):
        with codecs.open(path,'r+','utf-8') as svg:
            svg.seek(-6,2) #skip to the position right before </svg> tag
            svg.write('<g transform = \"translate('+str(x)+' '+str(y)+')\">\n') #group
            for i in range(0,len(data)):
                svg.write(  '<rect x=\"0\" y=\"'+str((i+1)*bin_width)+
                            '\" width=\"'+str(bin_width)+'\" height=\"'+str(bin_width)+
                            '" fill='+data.values[i][1][:-1]+ '/>\n')
                svg.write(  '<text x=\"20\" y=\"'+str((i+1)*bin_width+11)+
                            '\" stroke=\"none\" fill=\"black\" font-size=\"'+str(font_size)+
                            '" font-family=\"sans-serif\">'+data.values[i][2]+'</text>\n')
            svg.write('</g>\n</svg>') #group
    
    @staticmethod
    def _draw_gradient_scale(data,path,x=25,y=195,start_colour='rgb(255,0,0)',end_colour='rgb(184,255,0)'):
        with open(path,'r+') as svg:
            minimum = min(data)
            maximum = max(data)
            onethird = (maximum-minimum)/3
            svg.seek(-6,2) #skip to the position right before </svg> tag
            svg.write(  '<defs><linearGradient id=\"grad\" x1=\"0%\" y1=\"100%\" x2=\"0%\" y2=\"0%\">\n'+
                        '<stop offset=\"0%\" style=\"stop-color:'+start_colour+';stop-opacity:1\" />\n'+
                        '<stop offset=\"100%\" style=\"stop-color:'+end_colour+';stop-opacity:1\" /></linearGradient></defs>\n')

            svg.write(  '<g transform = \"translate('+str(x)+' '+str(y)+')\">\n'+
                        '<rect x=\"0\" y=\"0\" height=\"175\" width=\"25\" fill=\"url(#grad)\" />\n')

            svg.write(  '<text x=\"40\" y=\"10\" font-family=\"sans-serif\" stroke=\"none\" font-size=\"12\" fill=\"black\">'+str(maximum)+'</text>\n'+
                        '<text x=\"40\" y=\"63\" font-family=\"sans-serif\" font-size=\"12\" stroke=\"none\" fill=\"black\">'+str(minimum+onethird*2)+'</text>\n'+
                        '<text x=\"40\" y=\"121\" font-family=\"sans-serif\" font-size=\"12\" stroke=\"none\" fill=\"black\">'+str(minimum+onethird)+'</text>\n'+
                        '<text x=\"40\" y=\"175\" font-family=\"sans-serif\" font-size=\"12\" stroke=\"none\" fill=\"black\">'+str(minimum)+'</text>\n')

            svg.write(  '<line x1=\"35\" y1=\"5\" x2=\"25\" y2=\"5\"/>\n'+
                        '<line x1=\"35\" y1=\"58\" x2=\"25\" y2=\"58\"/>\n'+
                        '<line x1=\"35\" y1=\"116\" x2=\"25\" y2=\"116\"/>\n'+
                        '<line x1=\"35\" y1=\"170\" x2=\"25\" y2=\"170\"/>\n'+
                        '</g>\n</svg>')

    @staticmethod
    def _draw_title(path,title,x,y,font_size=12,color='black'):
        with codecs.open(path,'r+','utf-8') as svg:
        #with open(path,'r+') as svg:
            svg.seek(-6,2)
            svg.write(  '<text x =\"'+str(x)+'\" y=\"'+str(y)+'\" stroke=\"none\" font-size=\"'+
                        str(font_size)+'\" fill=\"'+color+'\" font-family=\"sans-serif\">'+
                        title+'</text>\n</svg>')
    ############################################################################

    def number_of_answers(self,draw_legend=True,right=None):
        data = self._number_of_answers(right)
        if not data.empty:
            colours = Analysis.colour_range_hsv(data)
            self._generate_csv(colours)
    
            with open(self.current_dir+'/base/style.css') as css:
                self.k.generate(self.config,outfile=self.current_dir+'/maps/numberofanswers.svg',stylesheet=css.read())
            if draw_legend:
                Map._draw_gradient_scale(data,self.current_dir+'/maps/numberofanswers.svg')
                Map._draw_title(self.current_dir+'/maps/numberofanswers.svg',u'Počty otázok',400,410,20)
    
    def response_time(self,draw_legend=True,right=None):
        data = self._response_time_place(right)
        if not data.empty:
            colours = Analysis.colour_range_hsv(data)
            self._generate_csv(colours)
    
            with open(self.current_dir+'/base/style.css') as css:
                self.k.generate(self.config,outfile=self.current_dir+'/maps/responsetime.svg',stylesheet=css.read())
            if draw_legend:
                Map._draw_title(self.current_dir+'/maps/responsetime.svg',u'Rýchlosť odpovede',400,410,20)
                Map._draw_gradient_scale(data,self.current_dir+'/maps/responsetime.svg')
    
    def avg_success(self,draw_legend=True, threshold=0):
        data = self._avg_success()['mean_success_rate']
        if not data.empty:
            colours = Analysis.colour_range_hsv(data)
            self._generate_csv(colours)
    
            with open(self.current_dir+'/base/style.css') as css:
                self.k.generate(self.config,outfile=self.current_dir+'/maps/avgsuccess.svg',stylesheet=css.read())
            if draw_legend:
                Map._draw_title(self.current_dir+'/maps/avgsuccess.svg',u'Priemerná úspešnosť',400,410,20)
                Map._draw_gradient_scale(data,self.current_dir+'/maps/avgsuccess.svg')
    
    def mistaken_countries(self,threshold=10,draw_legend=True):
        data = self._mistaken_countries(threshold)
        if not data.empty:
            colours = Analysis.colour_range_even(data)
            self._generate_csv(colours)
            colours['label'] = np.arange(len(data))
            colours['label'] = colours['label'].astype(object)
            colours['label'] = colours['label'].apply(lambda x: str(x)+u'. mýlená krajina')
            colours['label'][0] = u'Vybraná krajina'
                        
            with open(self.current_dir+'/base/style.css') as css:
                self.k.generate(self.config,outfile=self.current_dir+'/maps/mistakencountries.svg',stylesheet=css.read())
            if draw_legend:
                Map._draw_title(self.current_dir+'/maps/mistakencountries.svg',u'Pomýlené krajiny',400,410,20)
                Map._draw_bins_naive(colours,self.current_dir+'/maps/mistakencountries.svg',5,175)