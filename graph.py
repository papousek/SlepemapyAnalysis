# -*- coding: utf-8 -*-

from analysis import *
import matplotlib.pyplot as plt
import matplotlib

'''used for drawing graphs
'''
class Graph(Analysis):
    def __init__(self,path,df,user=None,place_asked=None,response_time_threshold=60000,lower_bound = 50,upper_bound = 236,session_duration= np.timedelta64(30, 'm')):
        Analysis.__init__(self,df,user,place_asked,response_time_threshold,lower_bound,upper_bound,session_duration)
        self.current_dir = path
        matplotlib.rc('font', **{'sans-serif' : 'Arial','family' : 'sans-serif'}) #nice font that can display non-ascii characters
        
    '''weekdays bar plot
    '''
    def weekdays(self, width = 0.35, colour = "b"):
        data = self._weekdays()
        if not data.empty:
            ind = np.arange(7)
            
            fig, ax = plt.subplots()
            bars = ax.bar(ind+width/2, data, width, colour=colour)
            ax.set_xticks(ind+width)
            
            ax.set_ylabel(u"Počty otázok")
            ax.set_title(u"Počty otázok v jednotlivých dňoch týždňa")
            ax.set_xticklabels( (u"Pondelok", u"Utorok", u"Streda", u"Štvrtok", u"Piatok",u"Sobota",u"Nedeľa"))
    
            plt.savefig(self.current_dir+'\\graphs\\weekdays.svg', bbox_inches='tight')
        
    '''draws inserted to response_time plot 
    optional parameter wrongTimes - can be set to additional set of points to draw
    for example right/wrong answers 
    def response_time_inserted(self, input1, input2=None, colour1 = 'green',colour2 = 'red',):
        if not input1.empty:
            fig,ax = plt.subplots()
            ax.set_ylabel(u"Log času odpovede")
            ax.set_yscale('log')
            ax.set_title(u"Čas odpovede počas existencie užívateľa")
    
            input1[0] = matplotlib.dates.date2num(input1[0])
            plt.plot_date(input1[0],input1[1],colour = colour1,marker='o',ls='')
            
            if input2 is not None:
                input2[0] = matplotlib.dates.date2num(input2[0])
                plt.plot_date(input2[0],input2[1],colour = colour2,marker='o',ls='')
            
            fig.autofmt_xdate()
            plt.savefig(self.current_dir+'\\graphs\\responsetimetinserted.svg', bbox_inches='tight')
    '''
    
    '''bar plot of session length
    '''
    def lengths_of_sessions(self, width = 0.35, colour = "b"):
        data = self._sessions_start_end()
        if not data.empty:
            ind = np.arange(len(data))
            fig, ax = plt.subplots()
            
            data['start'] = matplotlib.dates.date2num(data['start'])
            data['end'] = matplotlib.dates.date2num(data['end'])
            
            bars = ax.bar(ind+width/2, data['end']-data['start'], width, colour=colour)
            ax.set_xticks(ind+width)
            
            ax.set_ylabel(u"Dĺžka session")
            ax.set_title(u"Začiatok a koniec session")
            
            fig.autofmt_xdate()
            plt.savefig(self.current_dir+'\\graphs\\lengthsofsessions.svg', bbox_inches='tight')