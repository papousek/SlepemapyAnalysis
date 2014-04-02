# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import datetime

'''data analysis on dataframes
'''
class Analysis():
    
    '''lower_bound and upper_bound represent range of which entities(countries,regions etc) to consider in calculations
    names of entities are defined by standard ISO_3166-1_alpha-2 and they are also attached in the script folder \base\ as geography_place.csv
    default bounds are (50,236) and they represent indexes for countries only
    parameters user and place_asked are to be used for filtering for country/user specific analysis
    '''
    def __init__(self,df=None,user=None,place_asked=None,response_time_threshold=60000,lower_bound = 50,upper_bound = 236,session_duration= np.timedelta64(30, 'm')):
        pd.options.mode.chained_assignment = None #disabling useless warning from pandas
        self.session_duration = session_duration
        self.place_asked = place_asked
        if df is not None:            
            self.frame = df[(df.place_asked>lower_bound) & (df.place_asked<upper_bound)] #not sure about this operator, should filter out only countries
            
            if response_time_threshold is not None:
                print "Filtered dataframe for response_times <",response_time_threshold
                self.frame = self.frame[self.frame.response_time<response_time_threshold]
            if user is not None:
                print "Filtered dataframe for user",user
                self.frame = self.frame[self.frame.user==user]
            if place_asked is not None:
                print "Filtered dataframe for country",place_asked
                self.frame = self.frame[self.frame.place_asked==place_asked]
            
            self.frame['response_time_log'] = np.log(self.frame.response_time)
            self._add_session_numbers()
        else:
            self.frame = None
    
    def get_frame(self):
        return self.frame
    
    def set_frame(self,frame):
        self.frame = frame
    
    def get_session_duration(self):
        return self.session_duration
    
    def set_session_duration(self,session_duration):
        self.session_duration = session_duration

    def _add_session_numbers(self):
        self.frame = self.frame.sort(['inserted'])
        self.frame['session_number'] = (self.frame['inserted'] - self.frame['inserted'].shift(1) > self.session_duration).fillna(1).cumsum() #adds session numbers to every row
        
    def _sessions_start_end(self):
        result = pd.DataFrame()
        group = self.frame.groupby('session_number')
        result['start'] = group.first()['inserted']
        result['end'] = group.last()['inserted']
        return result
        
    def _first_questions(self):
        return self.frame.groupby('session_number').apply(lambda x: x.drop_duplicates(cols=['place_asked']))
    ############################################################################

    '''returns counts of weekdays (first value -Monday etc)
    '''
    def _weekdays(self):
        data = pd.DataFrame()
        data['weekday'] = pd.DatetimeIndex(self.frame.inserted).weekday
        counts = pd.DataFrame(np.arange(7)*0)
        return (counts[0]+data.weekday.value_counts()).fillna(0)

    def _hours(self):
        data = pd.DataFrame()
        data['hour'] = pd.DatetimeIndex(self.frame.inserted).hour
        counts = pd.DataFrame(np.arange(24)*0)
        return (counts[0]+data.hour.value_counts()).fillna(0)

    '''returns dictionary where key is country id and the value is amount of times this country was answered
    parameter right(True/False/None) is to filter only right/wrong/both answers
    '''
    def _number_of_answers(self,right=None):
        countries = self.frame
        if right:
            countries = self.frame[self.frame.place_asked==self.frame.place_answered]
        elif right==False:
            countries = self.frame[self.frame.place_asked!=self.frame.place_answered]
        return countries['place_asked'].value_counts()
    
    '''returns df of responseTime, place_answered]
    for right/wrong/both answers (rightOrWrong=True/False/None respectivelly)
    '''
    def _response_time_place(self,right=None):
        answers = self.frame
        if right:
            answers = answers[answers.place_asked==answers.place_answered]
        elif right == False:
            answers = answers[answers.place_asked!=answers.place_answered]
        answers = answers.groupby('place_asked')
        return answers['response_time'].mean()
    
    '''returns df of responseTime,insrted
    for right/wrong/both answers (rightOrWrong=True/False/None respectivelly)
    '''
    def _response_time_inserted(self,right=None,log=True):
        answers = self.frame
        if right:
            answers = answers[answers.place_asked==answers.place_answered]
        elif right == False:
            answers = answers[answers.place_asked!=answers.place_answered]
        if log:
            return answers[['inserted','response_time_log']]
        else:
            return answers[['inserted','response_time']]
    
    '''returns series of countries that are most mistaken
    '''
    def _mistaken_countries(self,threshold=None):
        wrong_answers = self.frame[self.frame.place_asked!=self.frame.place_answered]
        wrong_answers = wrong_answers['place_answered'].value_counts()
        return wrong_answers[:threshold]
    
    def _avg_success_by_place(self):
        result = pd.DataFrame()
        groups = self.frame.groupby('place_asked')
        result['mean_success_rate'] = groups.apply(lambda x: len(x[x.place_asked==x.place_answered])/float(len(x))*100)
        result['mean_response_time'] = groups.response_time.mean()
        return result.dropna()
    
    def _avg_success_combined(self):
        return (len(self.frame[self.frame.place_asked==self.frame.place_answered])/float(len(self.frame.place_asked))*100,self.frame.response_time.mean())
    
    def _learning(self):
        first_questions = self._first_questions()
        rates = []
        times = []
        limit = self.frame.session_number.max()+1

        for i in range(0,limit):
            temp = Analysis()
            temp.set_frame(first_questions[first_questions.session_number<=i])
            temp = temp._avg_success_combined()
            rates += [temp[0]]
            times += [temp[1]]

        result = pd.DataFrame()
        result['mean_success_rate'] = rates
        result['mean_response_time'] = times
        return result