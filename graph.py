# -*- coding: utf-8 -*-

from analysis import *
from drawer import Drawer
import matplotlib.pyplot as plt
import matplotlib

class Graph(Analysis,Drawer):

    def __init__(self,path,df=None,codes=None,user=None,place_asked=None,response_time_threshold=60000,lower_bound = 50,upper_bound = 236,session_duration= np.timedelta64(30, 'm')):
        Analysis.__init__(self,df,user,place_asked,response_time_threshold,lower_bound,upper_bound,session_duration)
        Drawer.__init__(self,path,codes)

        matplotlib.interactive(False)
        matplotlib.rc('font', **{'sans-serif' : 'Arial','family' : 'sans-serif'}) #nice font that can display non-ascii characters
        
    '''weekdays bar plot
    '''
    def weekday_activity(self, width = 0.35, colour = "b",path=''):
        if not path:
            path = self.current_dir+'/graphs/weekdayacivity.svg'
        data = self._weekdays()
        if not data.empty:
            ind = np.arange(7)
            
            fig, ax = plt.subplots()
            bars = ax.bar(ind+width/2, data, width, color=colour)
            ax.set_xticks(ind+width)
            
            ax.set_ylabel(u"Počty otázok")
            ax.set_title(u"Počty otázok v jednotlivých dňoch týždňa")
            ax.set_xticklabels( (u"Pondelok", u"Utorok", u"Streda", u"Štvrtok", u"Piatok",u"Sobota",u"Nedeľa"))
    
            plt.savefig(path, bbox_inches='tight')

    def hourly_activity(self, width = 0.35, colour = "b",path=''):
        if not path:
            path = self.current_dir+'/graphs/hourlyactivity.svg'
        data = self._hours()
        if not data.empty:
            ind = np.arange(24)
            
            fig, ax = plt.subplots()
            bars = ax.bar(ind+width/2, data, width, color=colour)
            ax.set_xticks(ind+width)
            
            ax.set_ylabel(u"Počty otázok")
            ax.set_title(u"Počty otázok v jednotlivých hodinách")
            ax.set_xticklabels(np.arange(24))
    
            plt.savefig(path, bbox_inches='tight')
    
    '''draws inserted to response_time plot 
    optional parameter wrongTimes - can be set to additional set of points to draw
    for example right/wrong answers 
    '''
    def response_time_inserted(self,log=True, right=None, colour1 = 'green',colour2 = 'red',path=''):
        if not path:
            path = self.current_dir+'/graphs/responsetimeinserted.svg'
        if right is None:
            input1 = self._response_time_inserted(True,log)
        else:
            input1 = self._response_time_inserted(right,log)
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
                input2 = self._response_time_inserted(False,log)
                if not input2.empty:
                    input2['inserted'] = matplotlib.dates.date2num(input2['inserted'])
                    if log:
                        plt.plot_date(input2['inserted'],input2['response_time_log'],color = colour2,marker='o',ls='')
                    else:
                        plt.plot_date(input2['inserted'],input2['response_time'],color = colour2,marker='o',ls='')
            
            fig.autofmt_xdate()
            plt.savefig(path)
            plt.close()
    
    '''bar plot of session length
    '''
    def lengths_of_sessions(self, width = 0.4, colour = "cyan",path=''):
        if not path:
            path = self.current_dir+'/graphs/lenghtsofsessions.svg'
        data = self._sessions_start_end()
        if not data.empty:
            fig, ax = plt.subplots()
            data['start'] = matplotlib.dates.date2num(data['start'])
            data['end'] = matplotlib.dates.date2num(data['end'])

            ax.bar(data['start'],data['end']-data['start'], width, color=colour)
            ax.xaxis_date()
            
            ax.set_ylabel(u"Length of session")
            ax.set_xlabel(u"Date of session")
            ax.set_title(u"Lengths of sessions over time")

            plt.savefig(path, bbox_inches='tight')
        
    def response_time_area(self,colour="cyan",threshold=5,path='',log=False):
        if not path:
            path = self.current_dir+'/graphs/responsetimearea.svg'
        data = self._response_time_place()
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

    def response_time_session(self,right=None,log=True,lower_bound=0,upper_bound=None):
        if upper_bound is None:
            maximum = self.frame.session_number.max()
        else:
            maximum = upper_bound
        data = Graph(self.current_dir,codes=self.codes)
        for i in range(lower_bound,maximum+1):
            data.set_frame(self.frame[self.frame.session_number==i])
            filename = self.current_dir+'/animations/graph '+str(i+1)+' of '+str(maximum+1)+'.svg'
            data.response_time_inserted(path=filename,log=log)

    def learning(self,path=None):
        if not path:
            path = self.current_dir+'/graphs/learning.svg'
        data = self._learning()
        if not data.empty:
            fig, ax1 = plt.subplots()
            data['inserted'] = matplotlib.dates.date2num(data['inserted'])
            ax1.plot_date(data['inserted'], data['mean_success_rate'], 'green')
            ax1.set_xlabel('Date of session)')
            ax1.set_ylabel('Mean success rate', color='green')
            for tl in ax1.get_yticklabels():
                tl.set_color('green')
            
            
            ax2 = ax1.twinx()
            ax2.plot_date(data['inserted'], data['mean_response_time'], 'red')
            ax2.set_ylabel('Mean response time', color='red')
            plt.gca().invert_yaxis()
            for tl in ax2.get_yticklabels():
                tl.set_color('red')
            fig.autofmt_xdate()
            plt.savefig(path, bbox_inches='tight') 
            plt.close()
        
    def avg_success(self,colour = "cyan",threshold=0,path=''):
        if not path:
            path = self.current_dir+'/graphs/avgsuccess.svg'
        data = self._avg_success(threshold)
        if not data.empty:
            fig,ax = plt.subplots()
            ax.set_ylabel(u"Priemerná rýchlosť odpovede")
            ax.set_xlabel(u"Priemerná úspešnosť")
            plt.plot(data['mean_success_rate'],data['mean_response_time'],marker="o",ls='',color=colour)

            plt.savefig(path, bbox_inches='tight')       
            plt.close()     