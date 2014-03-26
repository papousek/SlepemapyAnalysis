# -*- coding: utf-8 -*-

from analysis import *
from kartograph import Kartograph
from drawer import Drawer

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
        self.k = Kartograph()

    def set_config(self,config):
        self.config = config

    def _generate_csv(self,data):
        with open(self.current_dir+'/base/style.css','w+') as csv:
            data.apply(lambda x: csv.write('.states[iso_a2='+self.codes[self.codes.id==x.country]['code'].values[0].upper()+'] {\n\tfill: '+x.colour+';\n}\n'),axis=1)
    
    @staticmethod
    def _get_classes(data,num):
        if num<=0:
            return []
        mean = data.mean()
        return [mean]+Map._get_classes(data[data<mean],num-1)+Map._get_classes(data[data>=mean],num-1)
    
    '''nested-mean classification
    '''
    @staticmethod
    def get_classes(data,num):
        breaks = [data.min()-1,data.max()+1]+Map._get_classes(data,np.log2(num))
        breaks.sort()
        return breaks
    ############################################################################
    
    def draw_map(self,data):
        data = self._number_of_answers(right)
        if not data.empty:
            colours = Drawer.colour_range_hsv(data)
            self._generate_csv(colours)
    
            with open(self.current_dir+'/base/style.css') as css:
                self.k.generate(self.config,outfile=self.current_dir+name,stylesheet=css.read())
            if draw_legend:
                self.draw_gradient_scale(data,self.current_dir+name)
                self.draw_title(self.current_dir+name,u'Počty otázok',400,410,20)        
    
    def number_of_answers(self,draw_legend=True,right=None,name='/maps/numberofanswers.svg'):
        data = self._number_of_answers(right)
        if not data.empty:
            colours = Drawer.colour_range_hsv(data)
            self._generate_csv(colours)
    
            with open(self.current_dir+'/base/style.css') as css:
                self.k.generate(self.config,outfile=self.current_dir+name,stylesheet=css.read())
            if draw_legend:
                self.draw_gradient_scale(data,self.current_dir+name)
                self.draw_title(self.current_dir+name,u'Počty otázok',400,410,20)
    
    def response_time(self,draw_legend=True,right=None,name='/maps/responsetime.svg'):
        data = self._response_time_place(right)
        if not data.empty:
            colours = Drawer.colour_range_hsv(data)
            self._generate_csv(colours)
    
            with open(self.current_dir+'/base/style.css') as css:
                self.k.generate(self.config,outfile=self.current_dir+name,stylesheet=css.read())
            if draw_legend:
                self.draw_title(self.current_dir+name,u'Rýchlosť odpovede',400,410,20)
                self.draw_gradient_scale(data,self.current_dir+name)
    
    def mistaken_countriesNEW(self,draw_legend=True,threshold=None,name='/maps/mistakencountries.svg'):
        data = self._mistaken_countries(threshold)
        if not data.empty:
            number_of_bins = 8
            
            bins = self.get_classes(data['counts'],number_of_bins)
            data['bin'] = pd.cut(data['counts'], bins=bins,labels=False)
            data['bin'] = data['bin'].fillna(number_of_bins).astype(np.int8) #
            bins[0]+=1
            bins[-1]-=1
            
            colours = Drawer.colour_range_bins(number_of_bins)
            colours.append(Drawer.colour_value_rgb_string(0,192,255)) #
            data['colour'] = data.bin.apply(lambda x: colours[x])            
            self._generate_csv(data[['country','colour']])
            
            colours.reverse()
            colours.append(Drawer.colour_value_rgb_string(255,255,255))
            colours = pd.DataFrame(colours,columns=['colour'])
            bins = [round(x,2) for x in bins]
            labels = ['('+str(bins[curr])+', '+str(bins[curr+1])+']' for curr in range(len(bins)-1)]
            labels.reverse()

            colours['label'] = ['Chosen country']+labels+['No data']

            with open(self.current_dir+'/base/style.css') as css:
                self.k.generate(self.config,outfile=self.current_dir+name,stylesheet=css.read())
            if draw_legend:
                self.draw_title(self.current_dir+name,u'Mistaken countries',400,410,20)
                self.draw_bins_naive(colours,self.current_dir+name,5,175)
        
    def mistaken_countries(self,draw_legend=True,threshold=10,name='/maps/mistakencountries.svg'):
        data = self._mistaken_countries(threshold)
        if not data.empty:
            colours = Drawer.colour_range_even(data)
            self._generate_csv(colours)
            
            colours['label'] = [self.get_country_name(country[1]) for country in colours.country.iteritems()]
                        
            with open(self.current_dir+'/base/style.css') as css:
                self.k.generate(self.config,outfile=self.current_dir+name,stylesheet=css.read())
            if draw_legend:
                self.draw_title(self.current_dir+name,u'Pomýlené krajiny',400,410,20)
                self.draw_bins_naive(colours,self.current_dir+name,5,175)

    def avg_success(self,draw_legend=True, threshold=0, name='/maps/avgsuccess.svg'):
        data = self._avg_success()['mean_success_rate']
        if not data.empty:
            colours = Drawer.colour_range_hsv(data)
            self._generate_csv(colours)
    
            with open(self.current_dir+'/base/style.css') as css:
                self.k.generate(self.config,outfile=self.current_dir+name,stylesheet=css.read())
            if draw_legend:
                self.draw_title(self.current_dir+name,u'Priemerná úspešnosť',400,410,20)
                self.draw_gradient_scale(data,self.current_dir+name)    

    def avg_success_by_session(self):
        data = Map(self.current_dir,codes=self.codes)
        maximum = max(self.frame.session_number)
        for i in range(0,maximum+1):
            data.set_frame(self.frame[self.frame.session_number<=i])
            filename = 'animations/map '+str(i+1)+' of '+str(maximum+1)+'.svg'
            data.avg_success(draw_legend=False,name=filename)