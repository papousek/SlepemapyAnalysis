# -*- coding: utf-8 -*-

from drawable import *
import analysis

import pandas as pd
from numpy import arange,log

import matplotlib.pyplot as plt
from matplotlib import interactive
from matplotlib.dates import date2num
from matplotlib.ticker import FuncFormatter 


class Graph(Drawable):

    def __init__(   self, path='', codes=None, difficulties=None, df=None, user=None, place_asked=None,
                    lower_bound = 50,upper_bound = 236, session_numbers=True):    
        """Sets matplotlib to be non-interactive. All other defaults are same as in Drawable.
        """

        Drawable.__init__(self, path, codes,difficulties, df,user,place_asked,lower_bound,upper_bound,session_numbers)
        interactive(False) #disable matplotlib interactivity


    def weekday_activity(self, path=''):
        """Draws number of questions asked per weekday.
        
        :param path: output directory -- default is '' (current dir)
        """

        if not path:
            path = self.current_dir+'/graphs/weekdayactivity.svg'
        data = analysis.weekdays(self.frame)
        if not data.empty:
            ind = arange(7)
            width = 0.4
            fig, ax = plt.subplots()
            bars = ax.bar(ind+width/2, data, width=width, color="cyan")
            ax.set_xticks(ind+width)
            
            ax.set_ylabel(u"Number of questions")
            ax.set_title(u"Number of questions per weekday")
            ax.set_xticklabels( (u"Monday", u"Tuesday", u"Wednesday", u"Thursday", u"Friday",u"Saturday",u"Sunday"))
    
            plt.savefig(path, bbox_inches='tight')
            plt.close()


    def hourly_activity(self, path=''):
        """Draws number of questions asked per hour.
        
        :param path: output directory -- default is '' (current dir)
        """

        if not path:
            path = self.current_dir+'/graphs/hourlyactivity.svg'
        data = analysis.hours(self.frame)
        if not data.empty:
            ind = arange(24)
            width = 0.4
            
            fig, ax = plt.subplots()
            bars = ax.bar(ind+width/2, data, width, color="cyan")
            ax.set_xticks(ind+width)
            
            ax.set_ylabel(u"Number of questions")
            ax.set_title(u"Number of questions per hour")
            ax.set_xticklabels(arange(24))
    
            plt.savefig(path, bbox_inches='tight')
            plt.close()
    
    
    def response_time_area(self,path='',plot_log=True,threshold=5):
        """Draws graph of lengths of sessions per session.
        
        :param path: -- default is '' (current_dir)
        :param plot_log: whether to draw normal land area or log of land area -- default is True
        :param threshold: how many top countries to annotate
        """

        if not path:
            path = self.current_dir+'/graphs/responsetimearea.svg'
        data = analysis.response_time_place(self.frame)

        if not data.empty:
            areas = []
            for i in data.iteritems():
                areas += [self.codes[self.codes.id==i[0]]['area'].values[0]]
    
            fig,ax = plt.subplots()
            ax.set_xlabel(u"Mean response time")
            if plot_log:
                ax.set_ylabel(u"Log of land area of a country [km*km]")
                ax.set_yscale('log')
                areas = log(areas)
            else:
                ax.set_ylabel(u"Land area of a country [km*km]")
            plt.plot(data.values,areas,marker="o",ls='',color="cyan")

            '''data = data.sort(ascending=False)
            for i in range(threshold):
                ax.annotate(self.get_country_name(data.index[i]),(data[i],areas[i]))
                ax.annotate(self.get_country_name(data.index[i]),(data[-i],areas[-i]))'''
            plt.savefig(path, bbox_inches='tight')  
            plt.close()  
    
    
    def lengths_of_sessions(self, path='',threshold=15):
        """Draws graph of lengths of sessions per session.
        
        :param threshold: how many sessions to plot (globally there are 50+ sessions, but most of the people stay for 10+-)
        :param path: -- default is '' (current_dir)
        """

        if not path:
            path = self.current_dir+'/graphs/lenghtsofsessions.svg'
        data = analysis.lengths_of_sessions(self.frame)
        if not data.empty:
            fig, ax = plt.subplots()
            ax.bar(data.index,data.values,width=0.4, color="cyan")
    
            ax.set_ylabel(u"Session length [seconds]")
            ax.set_xlabel(u"Session number")
            ax.set_title(u"Lengths of sessions over time")
            
            plt.savefig(path, bbox_inches='tight')
            plt.close()

    
    def number_of_answers(self, path='',threshold=15):
        """Draws graph of number of answers per session.
        
        :param threshold: how many sessions to plot (globally there are 50+ sessions, but most of the people stay for 10+-)
        :param path: -- default is '' (current_dir)
        """

        if not path:
            path = self.current_dir+'/graphs/numberofanswers.svg'
        data = analysis.number_of_answers_session(self.frame,threshold)
        if not data.empty:
            fig, ax = plt.subplots()
            ax.bar(data.index,data.values,width=0.4, color="cyan")
    
            ax.set_ylabel(u"Mean number of questions")
            ax.set_xlabel(u"Session number")
            ax.set_title(u"Number of questions over sessions")
            
            plt.savefig(path, bbox_inches='tight')
            plt.close()
    
    
    def _twin_response_time(self,data, ax1, path='', invert_response_time=True):
        ax2 = ax1.twinx()
        
        ax2.plot(data.index, data.values, 'red')
        ax2.set_ylabel('Mean response time', color='red')
        if invert_response_time:
            plt.gca().invert_yaxis()
        for tl in ax2.get_yticklabels():
            tl.set_color('red')
    
    
    def success_response(self,path='',plot_response_time=True,invert_response_time=True,threshold=15):
        """Draws graph of mean success and mean response per session.
        
        :param plot_response_time: whether to draw response time plot -- default is True
        :param invert_response_time: whether to invert plot of response time -- default is True
        :param threshold: how many sessions to draw -- default is 10
        :param path: output directory -- default is '' (current_dir)
        """

        if not path:
            path = self.current_dir+'/graphs/successresponse.svg'
        data = analysis.mean_success_session(self.frame,threshold)

        if not data.empty:
            #setup mean_success_rate first
            fig, ax = plt.subplots()
            
            ax.plot(data.index, data.values, 'green')
            
            ax.set_xlabel('Session number')
            ax.yaxis.set_major_formatter(FuncFormatter(lambda x,y: "%1.2f%%"%(100*x))) #sets y-axis to show percentages
            ax.set_ylabel('Mean success rate', color='green')
            ax.set_title(u"Progress of success rate and response time over time")
            for tl in ax.get_yticklabels():
                tl.set_color('green')
            
            #setup mean_response_time
            if plot_response_time:
                data = analysis.mean_response_session(self.frame,threshold)
                self._twin_response_time(data, ax, path, invert_response_time)

            plt.savefig(path, bbox_inches='tight') 
            plt.close()
    
    
    def learning(self, path='', plot_response_time=True, invert_response_time=True, threshold=15):
        """Draws graph of mean skill and mean response time per session.

        :param plot_response_time: whether to draw response time plot -- default is True
        :param invert_response_time: whether to invert plot of response time -- default is True
        :param threshold: how many sessions to draw -- default is 10
        :param path: output directory -- default is '' (current_dir)
        """

        if not path:
            path = self.current_dir+'/graphs/learning.svg'
        data = analysis.mean_user_skill(self.frame,self.difficulties,threshold)
        data = analysis.predict_success_user(data)

        if not data.empty:
            fig, ax = plt.subplots()
            ax.plot(data.index, data.values, 'green')
            
            ax.set_xlabel('Session number')
            ax.set_ylabel('User\'s skill',color='green')
            ax.yaxis.set_major_formatter(FuncFormatter(lambda x,y: "%1.2f%%"%(100*x))) #sets y-axis to show percentages
            ax.set_title(u"Progress of user's skill and response time over sessions")
            for tl in ax.get_yticklabels():
                tl.set_color('green')

            if plot_response_time:
                data = analysis.mean_response_session(self.frame,threshold)
                self._twin_response_time(data, ax, path, invert_response_time)
            plt.savefig(path, bbox_inches='tight') 
            plt.close()