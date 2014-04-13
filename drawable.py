# -*- coding: utf-8 -*-

from analysis import add_session_numbers
from numpy import timedelta64,log

class Drawable():
    
    """Drawable object should have assigned path, codes and DataFrame. Can be created empty and then assigned by setters.
    
    :param path: default output directory
    :param codes: codes of countries defined by ISO_3166-1_alpha-2, also includes land area information -- default None
    :param df: dataframe to save -- default None
    :param user: filter by user id -- default None
    :param place_asked: filter by place_asked -- default None
    :param lower_bound, upper_bound: -- filter by countries in range (lower,upper) -- default is (50,236)
    :param add_session_numbers: whether to add new column with session numbers
    """

    def __init__(   self,path='',codes=None,difficulties=None,df=None,user=None,place_asked=None,
                    lower_bound = 50,upper_bound = 236, session_numbers=True):

        self.current_dir = path
        self.codes = codes
        self.difficulties = difficulties
        self.session_duration = timedelta64(30, 'm')
        self.frame = None
        
        if df is not None:            
            self.frame = df[(df.place_asked>lower_bound) & (df.place_asked<upper_bound)] #filter out only countries in range (lower_bound,upper_bound), there has to be a way to do this in a better way...
            self.frame = self.frame[self.frame.response_time<60000]
           
            if user is not None:
                print "Filtered dataframe for user.",user
                self.frame = self.frame[self.frame.user==user]
            if place_asked is not None:
                print "Filtered dataframe for country",place_asked
                self.frame = self.frame[self.frame.place_asked==place_asked]
            if session_numbers:
                print "Added session numbers to dataframe"
                self.frame = self.frame.groupby('user').apply(lambda x: add_session_numbers(x,self.session_duration))
            
            self.place_asked = place_asked
            self.frame['response_time_log'] = log(self.frame.response_time)

    def get_country_record(self,id):
        return self.codes[self.codes.id==id]
    
    def get_country_code(self,id):
        return self.get_country_record(id)['code'].values[0]

    def get_country_name(self,id):
        return self.get_country_record(id)['country'].values[0]
    
    def get_country_area(self,id):
        return self.get_country_record(id)['area'].values[0]
    
    def set_frame(self,frame):
        self.frame = frame
    
    def set_codes(self,codes):
        self.codes = codes
    
    def set_difficulties(self,difficulties):
        self.difficulties = difficulties
    
    def set_path(self,path):
        self.path = path
    
    def set_session_duration(self,session_duration):
        self.session_duration = session_duration