import os
from map import *
from graph import *
import inputoutput
import analysis

current_path = os.path.dirname(os.path.realpath(__file__))
codes = inputoutput.load_general_csv(current_path+"/geography.place.csv")
csv = inputoutput.load_geo_csv(current_path+"/geography.answer.csv")

try: #script is ran Nth time, we do not have to recalculate difficulties
    difficulties = inputoutput.load_difficulties(path=current_path+'/difficulties.yaml')
    am = Map(current_path,codes,difficulties,csv,session_numbers=False)
except IOError: #script is ran for the first time so we have to generate global difficulties
    am = Map(current_path,codes,None,csv,session_numbers=True)
    difficulties = analysis.get_difficulties(am.frame,current_path+'/difficulties.yaml')
    am.set_difficulties(difficulties)
    
g = Graph(current_path, codes, difficulties,csv, user=10)
'''
m = Map(current_path, codes, difficulties, csv, place_asked=150)
ag = Graph(current_path, codes, difficulties, csv,session_numbers=True)

ddsadssadsad
g.success()
g.skill()
ag.lengths_of_sessions()
ag.number_of_answers()
ag.weekday_activity()
ag.hourly_activity()
ag.response_time_area()

am.difficulty()
am.success()
m.mistaken_countries()
am.number_of_answers()
am.response_time()'''



