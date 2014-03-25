# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import colorsys
import codecs
#from xml.dom import minidom

class Drawer():
    
    ''' -path to current working directory
        -codes is df with country IDs and their respective ISO numbers+land areas in km squared
    '''
    def __init__(self,path,codes):
        self.current_dir = path
        self.codes = codes
    
    '''returns string in format 'rgb(r,g,b)'
    '''
    @staticmethod
    def colour_value_rgb(r,g,b):
        return '\'rgb('+str(int(r))+', '+str(int(g))+', '+str(int(b))+')\''
    
    @staticmethod
    def colour_value_hsv(h,s=1,v=1):
        colors = colorsys.hsv_to_rgb(h,s,v)
        return Drawer.colour_value_rgb(255*colors[0],255*colors[1],255*colors[2])
        
    '''generates evenly distributed colour scheme
    '''
    @staticmethod
    def colour_range_even(data):
        length = len(data)
        colors = [Drawer.colour_value_rgb(255,255*x/float(length),0) for x in range(length)]
        colors = pd.DataFrame(colors,data.country)
        colors = colors.reset_index() 
        colors.columns = ['country','colour']
        if pd.isnull(data[:1].counts).values[0]:
            colors[:1]['colour']=Drawer.colour_value_rgb(0,192,255)
        return colors
    
    @staticmethod
    def colour_range_hsv(data):
        maximum = max(data)
        coefficients = data.apply(lambda x: x/float(maximum) if pd.notnull(x) else None)
        coefficients = coefficients.apply(lambda y: Drawer.colour_value_rgb(0,192,255) if pd.isnull(y) else Drawer.colour_value_hsv(y*0.22))
        coefficients = coefficients.reset_index()
        coefficients.columns = ['country','colour']
        coefficients['country'] = coefficients['country'].astype(np.int64)
        return coefficients
        
    '''
    good colour schemes: (0,255-y*255,255)
                        (255,255-y*255,0)
                        (255-y*255,y*255,0)
    '''
    @staticmethod
    def colour_range_rgb(data):
        maximum = max(data)
        coefficients = data.apply(lambda x: x/float(maximum) if pd.notnull(x) else None)
        coefficients = coefficients.apply(lambda y: Drawer.colour_value_rgb(0,192,255) if pd.isnull(y) else Drawer.colour_value_rgb(255-y*71,y*255,0))
        coefficients = coefficients.reset_index()
        coefficients.columns = ['country','colour']
        coefficients['country'] = coefficients['country'].astype(np.int64)
        return coefficients
    
    '''@staticmethod
    def draw_bins_dom(data,kmap,x,y,bin_width=15,font_size=12):
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
            
            label = root.createElement(root.createTextNode(data.values[i][2])
            label.setAttribute('x','20')
            label.setAttribute('y',str((i+1)*bin_width+11))
            label.setAttribute('stroke','none')
            label.setAttribute('font-family','sans-serif')
            label.setAttribute('fill','black')
            label.setAttribute('font-size',str(font_size))
            group.appendChild(label)

        svg = root.getElementsByTagName('svg')[0]
        svg.appendChild(group)
        root.writexml(kmap)'''

    @staticmethod
    def draw_bins_naive(data,path,x,y,bin_width=15,font_size=12):
        with codecs.open(path,'r+','utf-8') as svg:
            svg.seek(-6,2) #skip to the position right before </svg> tag
            svg.write('<g transform = \"translate('+str(x)+' '+str(y)+')\">\n') #group
            for i in range(len(data)):
                svg.write(  '<rect x=\"0\" y=\"'+str((i+1)*bin_width)+
                            '\" width=\"'+str(bin_width)+'\" height=\"'+str(bin_width)+
                            '" fill='+data.values[i][1]+ '/>\n')
                svg.write(  '<text x=\"20\" y=\"'+str((i+1)*bin_width+11)+
                            '\" stroke=\"none\" fill=\"black\" font-size=\"'+str(font_size)+
                            '" font-family=\"sans-serif\">'+data.values[i][2]+'</text>\n')
            svg.write('</g>\n</svg>') #group
    
    @staticmethod
    def draw_gradient_scale(data,path,x=25,y=195,start_colour='rgb(255,0,0)',end_colour='rgb(184,255,0)'):
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
    def draw_title(path,title,x,y,font_size=12,color='black'):
        with codecs.open(path,'r+','utf-8') as svg:
            svg.seek(-6,2)
            svg.write(  '<text x =\"'+str(x)+'\" y=\"'+str(y)+'\" stroke=\"none\" font-size=\"'+
                        str(font_size)+'\" fill=\"'+color+'\" font-family=\"sans-serif\">'+
                        title+'</text>\n</svg>')
    
    def get_country_record(self,id):
        return self.codes[self.codes.id==id]
    
    def get_country_code(self,id):
        return self.get_country_record(id)['code'].values[0]

    def get_country_name(self,id):
        return self.get_country_record(id)['country'].values[0]
    
    def get_country_area(self,id):
        return self.get_country_record(id)['area'].values[0]