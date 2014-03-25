# -*- coding: utf-8 -*-

from analysis import *
from kartograph import Kartograph
from drawer import Drawer
#from mystringio import MyStringIO

'''used for drawing maps
'''
class Map(Analysis,Drawer):

    def __init__(self,path,df=None,codes=None,user=None,place_asked=None,response_time_threshold=60000,lower_bound = 50,upper_bound = 236,session_duration= np.timedelta64(30, 'm')):
        Analysis.__init__(self,df,user,place_asked,response_time_threshold,lower_bound,upper_bound,session_duration)
        Drawer.__init__(self,path,codes)

        config ={
            "layers": {
                "states": {    
                    "src": self.current_dir+"/base/ne_110m_admin_0_countries.shp",
                    "filter": ["continent", "in", ["Europe","Asia","Africa","South America","Oceania","North America"]],
                    "class": "states"
                }
            }
        }
        self.set_config(config)
        self.k = Kartograph()

    def set_config(self,config):
        self.config = config

    def _generate_csv(self,data):
        with open(self.current_dir+'/base/style.css','w+') as csv:
            data.apply(lambda x: csv.write('.states[iso_a2='+self.codes[self.codes.id==x.country]['code'].values[0].upper()+'] {\n\tfill: '+x.colour+';\n}\n'),axis=1)
    
    ############################################################################

    def number_of_answers(self,draw_legend=True,right=None,name='numberofanswers'):
        data = self._number_of_answers(right)
        if not data.empty:
            colours = Drawer.colour_range_hsv(data)
            self._generate_csv(colours)
    
            with open(self.current_dir+'/base/style.css') as css:
                self.k.generate(self.config,outfile=self.current_dir+'/maps/'+name+'.svg',stylesheet=css.read())
            if draw_legend:
                self.draw_gradient_scale(data,self.current_dir+'/maps/numberofanswers.svg')
                self.draw_title(self.current_dir+'/maps/'+name+'.svg',u'Počty otázok',400,410,20)
    
    def response_time(self,draw_legend=True,right=None,name='responsetime'):
        data = self._response_time_place(right)
        if not data.empty:
            colours = Drawer.colour_range_hsv(data)
            self._generate_csv(colours)
    
            with open(self.current_dir+'/base/style.css') as css:
                self.k.generate(self.config,outfile=self.current_dir+'/maps/responsetime.svg',stylesheet=css.read())
            if draw_legend:
                self.draw_title(self.current_dir+'/maps/responsetime.svg',u'Rýchlosť odpovede',400,410,20)
                self.draw_gradient_scale(data,self.current_dir+'/maps/'+name+'.svg')

    def mistaken_countries(self,draw_legend=True,threshold=10,name='mistakencountries'):
        data = self._mistaken_countries(threshold)
        if not data.empty:
            colours = Drawer.colour_range_even(data)
            self._generate_csv(colours)
            
            colours['label'] = [self.get_country_name(country[1]) for country in colours.country.iteritems()]
                        
            with open(self.current_dir+'/base/style.css') as css:
                self.k.generate(self.config,outfile=self.current_dir+'/maps/mistakencountries.svg',stylesheet=css.read())
            if draw_legend:
                self.draw_title(self.current_dir+'/maps/mistakencountries.svg',u'Pomýlené krajiny',400,410,20)
                self.draw_bins_naive(colours,self.current_dir+'/maps/'+name+'.svg',5,175)

    def avg_success(self,draw_legend=True, threshold=0, name='avgsuccess'):
        data = self._avg_success()['mean_success_rate']
        if not data.empty:
            colours = Drawer.colour_range_hsv(data)
            self._generate_csv(colours)
    
            with open(self.current_dir+'/base/style.css') as css:
                self.k.generate(self.config,outfile=self.current_dir+'/maps/'+name+'.svg',stylesheet=css.read())
            if draw_legend:
                self.draw_title(self.current_dir+'/maps/avgsuccess.svg',u'Priemerná úspešnosť',400,410,20)
                self.draw_gradient_scale(data,self.current_dir+'/maps/'+name+'.svg')    

    def avg_success_by_session(self):
        data = Map(self.current_dir,codes=self.codes)
        maximum = max(self.frame.session_number)
        for i in range(0,maximum+1):
            data.set_frame(self.frame[self.frame.session_number<=i])
            filename = 'animation/map '+str(i+1)+' of '+str(maximum+1)
            data.avg_success(draw_legend=False,name=filename)