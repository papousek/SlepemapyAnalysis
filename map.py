# -*- coding: utf-8 -*-

from analysis import *
from kartograph import Kartograph
from xml.dom import minidom
from mystringio import MyStringIO
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
        with open(path,'r+') as svg:
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
    def _draw_gradient_scale(data,path,name='',start_colour='rgb(255,0,0)',end_colour='rgb(184,255,0)'):
        with open(path,'r+') as svg:
            minimum = min(data)
            maximum = max(data)
            onethird = (maximum-minimum)/3
            svg.seek(-6,2) #skip to the position right before </svg> tag
            svg.write('<defs>  <linearGradient id=\"grad2\" x1=\"0%\" y1=\"0%\" x2=\"100%\" y2=\"0%\">\n      <stop offset=\"0%\" style=\"stop-color:'+start_colour+';stop-opacity:1\" />\n      <stop offset=\"100%\" style=\"stop-color:'+end_colour+';stop-opacity:1\" />\n    </linearGradient>\n  </defs>\n  <rect x=\"610\" y=\"375\" height=\"25\" width=\"175\" fill=\"url(#grad2)\" />\n  \n<text x=\"610\" y=\"365\" font-family=\"sans-serif\" font-size=\"11\" fill=\"black\">' +str(int(minimum))+ '</text>\n  <line x1=\"613\" y1=\"368\" x2=\"613\" y2=\"388\"/>\n\n<text x=\"665\" y=\"365\" font-family=\"sans-serif\" font-size=\"11\" fill=\"black\">' +str(int(onethird+minimum))+ '</text>\n  <line x1=\"672\" y1=\"368\" x2=\"672\" y2=\"388\"/>\n\n  <text x=\"720\" y=\"365\" font-family=\"sans-serif\" font-size=\"11\" fill=\"black\">' +str(int(onethird*2+minimum))+ '</text>\n  <line x1=\"727\" y1=\"368\" x2=\"727\" y2=\"388\"/>\n\n<text x=\"775\" y=\"365\" font-family=\"sans-serif\" font-size=\"11\" fill=\"black\">' +str(int(maximum))+ '</text>\n  <line x1=\"782\" y1=\"368\" x2=\"782\" y2=\"388\"/>\n\n  <text x=\"610\" y=\"415\" font-family=\"sans-serif\" font-size=\"15\" fill=\"black\">' +name+'</text></svg>')
    
    @staticmethod
    def _draw_title(path,title,x,y,font_size=12,color='black'):
        with open(path,'r+') as svg:
            svg.seek(-6,2)
            svg.write(  '<text x =\"'+str(x)+'\" y=\"'+str(y)+'\" stroke=\"none\" font-size=\"'+
                        str(font_size)+'\" fill=\"'+color+'\" font-family=\"sans-serif\">'+
                        title+'</text>\n</svg>')
    ############################################################################

    def number_of_answers(self,draw_legend=True,right=None):
        data = self._number_of_answers(right)
        if not data.empty:
            colours = Analysis.colour_range(data)
            self._generate_csv(colours)
    
            with open(self.current_dir+'/base/style.css') as css:
                self.k.generate(self.config,outfile=self.current_dir+'/maps/numberofanswers.svg',stylesheet=css.read())
            if draw_legend:
                Map._draw_gradient_scale(data,self.current_dir+'/maps/numberofanswers.svg')
                Map._draw_title(self.current_dir+'/maps/numberofanswers.svg','Pocty odpovedi',400,410,20,'rgb(255, 0, 0)')
    
    def response_time(self,draw_legend=True,right=None):
        data = self._response_time_place(right)
        if not data.empty:
            colours = Analysis.colour_range(data)
            self._generate_csv(colours)
    
            with open(self.current_dir+'/base/style.css') as css:
                self.k.generate(self.config,outfile=self.current_dir+'/maps/responsetime.svg',stylesheet=css.read())
            if draw_legend:
                Map._draw_title(self.current_dir+'/maps/responsetime.svg','Rychlost odpovede',400,410,20,'rgb(255, 0, 0)')
                Map._draw_gradient_scale(data,self.current_dir+'/maps/responsetime.svg')
    
    def avg_success(self,draw_legend=True, threshold=0):
        data = self._avg_success()
        if not data.empty:
            colours = Analysis.colour_range(data)
            self._generate_csv(colours)
    
            with open(self.current_dir+'/base/style.css') as css:
                self.k.generate(self.config,outfile=self.current_dir+'/maps/avgsuccess.svg',stylesheet=css.read())
            if draw_legend:
                Map._draw_title(self.current_dir+'/maps/avgsuccess.svg','Priemerna uspesnost',400,410,20,'rgb(255, 0, 0)')
                Map._draw_gradient_scale(data,self.current_dir+'/maps/avgsuccess.svg')
    
    def mistaken_countries(self,threshold=10,draw_legend=True):
        data = self._mistaken_countries(threshold)
        if not data.empty:
            colours = Analysis.colour_range_even(data)
            self._generate_csv(colours)
            colours['label'] = np.arange(len(data))
            colours['label'] = colours['label'].astype(object)
            colours['label'] = colours['label'].apply(lambda x: str(x)+'. mylena krajina')
            colours['label'][0] = 'Vybrana krajina'
                        
            with open(self.current_dir+'/base/style.css') as css:
                self.k.generate(self.config,outfile=self.current_dir+'/maps/mistakencountries.svg',stylesheet=css.read())
            if draw_legend:
                Map._draw_title(self.current_dir+'/maps/mistakencountries.svg','Pomylene krajiny',400,410,20,'rgb(255, 0, 0)')
                Map._draw_bins_naive(colours,self.current_dir+'/maps/mistakencountries.svg',5,175)