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
    def weekday_activity(self, width = 0.35, colour = "b"):
        data = self._weekdays()
        if not data.empty:
            ind = np.arange(7)
            
            fig, ax = plt.subplots()
            bars = ax.bar(ind+width/2, data, width, color=colour)
            ax.set_xticks(ind+width)
            
            ax.set_ylabel(u"Počty otázok")
            ax.set_title(u"Počty otázok v jednotlivých dňoch týždňa")
            ax.set_xticklabels( (u"Pondelok", u"Utorok", u"Streda", u"Štvrtok", u"Piatok",u"Sobota",u"Nedeľa"))
    
            plt.savefig(self.current_dir+'/graphs/weekdays.svg', bbox_inches='tight')

    def hour_activity(self, width = 0.35, colour = "b"):
        data = self._hours()
        if not data.empty:
            ind = np.arange(24)
            
            fig, ax = plt.subplots()
            bars = ax.bar(ind+width/2, data, width, color=colour)
            ax.set_xticks(ind+width)
            
            ax.set_ylabel(u"Počty otázok")
            ax.set_title(u"Počty otázok v jednotlivých hodinách")
            ax.set_xticklabels(np.arange(24))
    
            plt.savefig(self.current_dir+'/graphs/hours.svg', bbox_inches='tight')
    
    '''draws inserted to response_time plot 
    optional parameter wrongTimes - can be set to additional set of points to draw
    for example right/wrong answers 
    '''
    def response_time_inserted(self, right=None, colour1 = 'green',colour2 = 'red',name='responsetimeinserted'):
        if right is None:
            input1 = self._response_time_inserted(True)
        else:
            input1 = self._response_time_inserted(right)
        if not input1.empty:
            fig,ax = plt.subplots()
            ax.set_ylabel(u"Log času odpovede")
            ax.set_yscale('log')
            ax.set_title(u"Rýchlosť odpovede v čase")
    
            input1['inserted'] = matplotlib.dates.date2num(input1['inserted'])
            plt.plot_date(input1['inserted'],input1['response_time_log'],color = colour1,marker='o',ls='')
            
            if right is None:
                input2 = self._response_time_inserted(False)
                if not input2.empty:
                    input2['inserted'] = matplotlib.dates.date2num(input2['inserted'])
                    plt.plot_date(input2['inserted'],input2['response_time_log'],color = colour2,marker='o',ls='')
            
            fig.autofmt_xdate()
            plt.savefig(self.current_dir+'/graphs/'+name+'.svg', bbox_inches='tight')
    
    '''bar plot of session length
    '''
    def lengths_of_sessions(self, width = 0.35, colour = "cyan"):
        data = self._sessions_start_end()
        if not data.empty:
            ind = np.arange(len(data))
            fig, ax = plt.subplots()

            data['start'] = matplotlib.dates.date2num(data['start'])
            data['end'] = matplotlib.dates.date2num(data['end'])
            #ax.bar(ind+width/2,data['end']-data['start'], width, color=colour)
            plt.plot(data['start'],data['end']-data['start'],color = colour,ls='',marker = 'o')
            #ax.set_xticks(data['start'].values)
            
            ax.set_ylabel(u"Dĺžka session")
            ax.set_title(u"Začiatok a koniec session")
            
            fig.autofmt_xdate()
            plt.savefig(self.current_dir+'/graphs/lengthsofsessions.svg', bbox_inches='tight')
    
    def response_time_area(self,colour="cyan",threshold=5,name='responsetimearea'):
        data = self._response_time_place()
        if not data.empty:
            data = pd.DataFrame(data)
            data = data.reset_index()
            data.columns = ['id','response_time']
            data['area'] = self.codes['area']
            
            fig,ax = plt.subplots()
            ax.set_ylabel(u"Veľkosť štátu")
            ax.set_xlabel(u"Priemerná rýchlosť odpovede")
            #ax.set_yscale('log')
            #data['area'] = np.log(data['area'])
            plt.plot(data['response_time'],data['area'],marker="o",ls='',color=colour)

            data = data.sort('response_time',ascending=False)
            for i in range(threshold):
                ax.annotate(self.get_country_name(data['id'].values[i]),(data['response_time'].values[i],data['area'].values[i]))
            plt.savefig(self.current_dir+'/graphs/'+name+'.svg', bbox_inches='tight')    

    def response_time_session(self,right=None):
        data = Graph(self.current_dir,self.codes)
        data.set_frame(self.frame.groupby('session_number'))
        data = data.response_time_inserted(right,name='responsetimesession')
    
    def avg_success(self,colour = "cyan",threshold=0):
        data = self._avg_success(threshold)
        if not data.empty:
            fig,ax = plt.subplots()
            ax.set_ylabel(u"Priemerná rýchlosť odpovede")
            ax.set_xlabel(u"Priemerná úspešnosť")
            plt.plot(data['mean_success_rate'],data['mean_response_time'],marker="o",ls='',color=colour)

            plt.savefig(self.current_dir+'/graphs/avgsuccessresponse.svg', bbox_inches='tight')            