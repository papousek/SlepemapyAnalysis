# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import analysis


class Drawable():
    
    """Drawable object should have assigned path, codes and DataFrame. Can be created empty and then assigned by setters.
    
    path -- default output directory
    codes -- codes of countries defined by ISO_3166-1_alpha-2, also includes land area information -- default None
    df -- dataframe to save -- default None
    user -- filter by user id -- default None
    place_asked -- filter by place_asked -- default None
    response_time_threshold -- filter by response time less than threshold -- default 60000 (60 seconds)
    lower_bound, upper_bound -- filter by countries in range (lower,upper) -- default is (50,236)
    session_duration -- time difference between two answers in which the two are considered to be in the same session -- default 30 minutes
    add_session_numbers -- whether to add new column with session numbers
    """
    def __init__(self,path='',codes=None,df=None,user=None,place_asked=None,response_time_threshold=60000,lower_bound = 50,upper_bound = 236,session_duration= np.timedelta64(30, 'm'),add_session_numbers=True):
        self.current_dir = path
        self.codes = codes
        self.session_duration = session_duration
        self.frame = None
        
        if df is not None:            
            self.frame = df[(df.place_asked>lower_bound) & (df.place_asked<upper_bound)] #filter out only countries in range (lower_bound,upper_bound)
            
            if response_time_threshold is not None:
                print "Filtered dataframe for response_times <",response_time_threshold
                self.frame = self.frame[self.frame.response_time<response_time_threshold]
            if user is not None:
                print "Filtered dataframe for user",user
                self.frame = self.frame[self.frame.user==user]
            if place_asked is not None:
                print "Filtered dataframe for country",place_asked
                self.frame = self.frame[self.frame.place_asked==place_asked]
            if add_session_numbers:
                self.frame = self.frame.groupby('user').apply(lambda x: analysis.add_session_numbers(x,self.session_duration))
            
            self.place_asked = place_asked
            self.frame['response_time_log'] = np.log(self.frame.response_time)

    def get_country_record(self,id):
        return self.codes[self.codes.id==id]
    
    def get_country_code(self,id):
        return self.get_country_record(id)['code'].values[0]

    def get_country_name(self,id):
        return self.get_country_record(id)['country'].values[0]
    
    def get_country_area(self,id):
        return self.get_country_record(id)['area'].values[0]
    
    def get_frame(self):
        return self.frame
    
    def set_frame(self,frame):
        self.frame = frame
    
    def set_path(self,path):
        self.path = path
    
    def get_session_duration(self):
        return self.session_duration
    
    def set_session_duration(self,session_duration):
        self.session_duration = session_duration