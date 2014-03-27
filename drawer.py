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
    def colour_value_rgb_string(r,g,b):
        return '\'rgb('+str(int(255*r))+', '+str(int(255*g))+', '+str(int(255*b))+')\''
    
    @staticmethod
    def colour_value_hsv(h,s=1,v=1):
        colours = colorsys.hsv_to_rgb(h,s,v)
        return [colours[0],colours[1],colours[2]]
    
    #0.35 is nice constant, for 4 bins you get green, yellow, orange and red, all easily distinguishable from each other
    @staticmethod
    def colour_range(length,hue_limit=0.35):
        colors = [Drawer.colour_value_hsv((hue_limit*x)/length) for x in range(length)]
        return colors
    
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
    def draw_bins_naive(data,path,x=5,y=175,bin_width=15,font_size=12):
        with codecs.open(path,'r+','utf-8') as svg:
            svg.seek(-6,2) #skip to the position right before </svg> tag
            svg.write('<g transform = \"translate('+str(x)+' '+str(y)+')\">\n') #group
            for i in range(len(data)):
                svg.write(  '<rect x=\"0\" y=\"'+str((i+1)*bin_width)+
                            '\" width=\"'+str(bin_width)+'\" height=\"'+str(bin_width)+
                            '" fill='+Drawer.colour_value_rgb_string(data.r.values[i],data.g.values[i],data.b.values[i])+ '/>\n')
                svg.write(  '<text x=\"20\" y=\"'+str((i+1)*bin_width+11)+
                            '\" stroke=\"none\" fill=\"black\" font-size=\"'+str(font_size)+
                           '" font-family=\"sans-serif\">'+data.label.values[i]+'</text>\n')
            svg.write('</g>\n</svg>') #group

    @staticmethod
    def draw_title(path,title='',x=400,y=410,font_size=20,color='black'):
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