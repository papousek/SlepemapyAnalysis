# -*- coding: utf-8 -*-

import analysis
from drawable import *

import matplotlib.pyplot as plt
import matplotlib
from matplotlib.ticker import FuncFormatter 


class Graph(Drawable):

    def __init__(self,path='',codes=None,df=None,user=None,place_asked=None,response_time_threshold=60000,lower_bound = 50,upper_bound = 236,session_duration= np.timedelta64(30, 'm'),add_session_numbers=True):    
        """Sets matplotlib to be non-interactive and default font as Arial. All other defaults are same as in Drawable.
        """

        Drawable.__init__(self,path,codes,df,user,place_asked,response_time_threshold,lower_bound,upper_bound,session_duration,add_session_numbers)

        matplotlib.interactive(False)
        matplotlib.rc('font', **{'sans-serif' : 'Arial','family' : 'sans-serif'}) #nice font


    def weekday_activity(self, width = 0.35, colour = "b",path=''):
        """Draws number of questions asked per weekday.
        
        :param width: width of bars -- default is 0.35
        :param colour: colour of bars -- default is "b" (blue)
        :param path: output directory -- default is '' (current dir)
        """

        if not path:
            path = self.current_dir+'/graphs/weekdayactivity.svg'
        data = analysis.weekdays(self.frame)
        if not data.empty:
            ind = np.arange(7)
            
            fig, ax = plt.subplots()
            bars = ax.bar(ind+width/2, data, width, color=colour)
            ax.set_xticks(ind+width)
            
            ax.set_ylabel(u"Number of questions")
            ax.set_title(u"Number of questions per weekday")
            ax.set_xticklabels( (u"Monday", u"Tuesday", u"Wednesday", u"Thursday", u"Friday",u"Saturday",u"Sunday"))
    
            plt.savefig(path, bbox_inches='tight')
            plt.close()


    def hourly_activity(self, width = 0.35, colour = "b",path=''):
        """Draws number of questions asked per hour.
        
        :param width: width of bars -- default is 0.35
        :param colour: colour of bars -- default is "b" (blue)
        :param path: output directory -- default is '' (current dir)
        """

        if not path:
            path = self.current_dir+'/graphs/hourlyactivity.svg'
        data = analysis.hours(self.frame)
        if not data.empty:
            ind = np.arange(24)
            
            fig, ax = plt.subplots()
            bars = ax.bar(ind+width/2, data, width, color=colour)
            ax.set_xticks(ind+width)
            
            ax.set_ylabel(u"Number of questions")
            ax.set_title(u"Number of questions per hour")
            ax.set_xticklabels(np.arange(24))
    
            plt.savefig(path, bbox_inches='tight')
            plt.close()


    def response_time_inserted(self,log=True, right=None, colour1 = 'green',colour2 = 'red',path=''):
        """Draws graph of response time for time period.
        
        :param log: whether to draw normal response times or logarithmic response times -- default is True
        :param right: draw only right/wrong/both answers
        :type right: True/False/None -- default is None
        :param colour1: colour for right answers -- default is 'green'
        :param colour2: colour for wrong answers-- default is 'red'
        :param path: output directory -- default is '' (current dir)
        """

        if not path:
            path = self.current_dir+'/graphs/responsetimeinserted.svg'
        if right is None:
            input1 = analysis.response_time_inserted(self.frame,True,log)
        else:
            input1 = analysis.response_time_inserted(self.frame,right,log)
        if not input1.empty:
            fig,ax = plt.subplots()
            if log:
                ax.set_ylabel(u"Response time log")
                ax.set_yscale('log')
            else:
                ax.set_ylabel(u"Response time")
            ax.set_title(u"Response time for time period")
    
            input1['inserted'] = matplotlib.dates.date2num(input1['inserted'])
            if log:
                plt.plot_date(input1['inserted'],input1['response_time_log'],color = colour1,marker='o',ls='')
            else:
                plt.plot_date(input1['inserted'],input1['response_time'],color = colour1,marker='o',ls='')
            
            if right is None:
                input2 = analysis.response_time_inserted(self.frame,False,log)
                if not input2.empty:
                    input2['inserted'] = matplotlib.dates.date2num(input2['inserted'])
                    if log:
                        plt.plot_date(input2['inserted'],input2['response_time_log'],color = colour2,marker='o',ls='')
                    else:
                        plt.plot_date(input2['inserted'],input2['response_time'],color = colour2,marker='o',ls='')
            
            fig.autofmt_xdate()
            plt.savefig(path)
            plt.close()
    
    
    def lengths_of_sessions(self, width = 0.4, colour = "cyan",path=''):
        """Draws graph of lengths of sessions per session.
        
        :param width: width of bars -- default is 0.4
        :param colour: colour of bars -- default is "cyan"
        :param path: -- default is '' (current_dir)
        """

        if not path:
            path = self.current_dir+'/graphs/lenghtsofsessions.svg'
        data = analysis.lengths_of_sessions(self.frame,self.session_duration)
        if not data.empty:
            fig, ax = plt.subplots()
            ax.bar(data.index,data.values,width, color=colour)
    
            ax.set_ylabel(u"Session length [seconds]")
            ax.set_xlabel(u"Session number")
            ax.set_title(u"Lengths of sessions over time")
            
            plt.savefig(path, bbox_inches='tight')
            plt.close()


    def response_time_area(self,colour="cyan",threshold=5,path='',log=True):
        """Draws graph of lengths of sessions per session.
        
        :param threshold: number of points to annotate -- default is 0.4
        :param colour: colour of bars -- default is "cyan"
        :param path: -- default is '' (current_dir)
        :param log: whether to draw normal response times or logarithmic response times -- default is True
        """

        if not path:
            path = self.current_dir+'/graphs/responsetimearea.svg'
        data = analysis.response_time_place(self.frame)
        if not data.empty:
            data = pd.DataFrame(data)
            data['area'] = self.codes['area']
            data = data.reset_index()
    
            fig,ax = plt.subplots()
            ax.set_xlabel(u"Mean response time")
            if log:
                ax.set_ylabel(u"Log of land area of a country [km*km]")
                ax.set_yscale('log')
                data['area'] = np.log(data['area'])
            else:
                ax.set_ylabel(u"Land area of a country [km*km]")
            plt.plot(data['response_time'],data['area'],marker="o",ls='',color=colour)

            data = data.sort('response_time',ascending=False)
            for i in range(threshold):
                ax.annotate(self.get_country_name(data['place_asked'].values[i]),(data['response_time'].values[i],data['area'].values[i]))
                ax.annotate(self.get_country_name(data['place_asked'].values[-i]),(data['response_time'].values[-i],data['area'].values[-i]))
            plt.savefig(path, bbox_inches='tight')  
            plt.close()  


    def learning(self,path='',plot_date=True,plot_response_time=True,invert_response_time=True,session_threshold=None):
        """Draws graph of mean success rate and mean response time per session.
        
        :param plot_date: whether to draw dates or session numbers -- default is True
        :param plot_response_time: whether to draw response time plot -- default is True
        :param invert_response_time: whether to invert plot of response time --default is True
        :param session_threshold: how many sessions to draw -- default is None
        :param path: output directory -- default is '' (current_dir)
        """

        if not path:
            path = self.current_dir+'/graphs/learning.svg'
        data = analysis.learning(self.frame,self.session_duration,session_threshold)
        if plot_date:
            data = data.join(analysis.sessions_start_end(self.frame))
        if not data.empty:
            
            #setup mean_success_rate first
            fig, ax1 = plt.subplots()
            if plot_date:
                data['start'] = matplotlib.dates.date2num(data['start'])
                ax1.plot_date(data['start'], data['mean_success_rate'], 'green')
                ax1.set_xlabel('Date of session')
            else:
                ax1.plot(data.index, data['mean_success_rate'], 'green')
                ax1.set_xlabel('Session number')
            
            ax1.yaxis.set_major_formatter(FuncFormatter(lambda x,y: "%1.2f%%"%(100*x))) #sets y-axis to show percentages
            ax1.set_ylabel('Mean success rate', color='green')
            ax1.set_title(u"Learning over time")
            for tl in ax1.get_yticklabels():
                tl.set_color('green')
            
            #setup mean_response_time
            if plot_response_time:
                ax2 = ax1.twinx()
                if plot_date:
                    ax2.plot_date(data['start'], data['mean_response_time'], 'red')
                    fig.autofmt_xdate()
                else:
                    ax2.plot(data.index, data['mean_response_time'], 'red')
                ax2.set_ylabel('Mean response time', color='red')
                if invert_response_time:
                    plt.gca().invert_yaxis()
                for tl in ax2.get_yticklabels():
                    tl.set_color('red')
            plt.savefig(path, bbox_inches='tight') 
            plt.close()