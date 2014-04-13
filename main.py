import os
from map import *
from graph import *
import inputoutput
import analysis

current_path = os.path.dirname(os.path.realpath(__file__))
codes = inputoutput.load_general_csv(current_path+"/base/areas.csv")
csv = inputoutput.load_geo_csv(current_path+"/base/large.csv")

try: #script is ran Nth time, we do not have to recalculate difficulties
    difficulties = inputoutput.load_difficulties(path=current_path+'/base/difficulties.json')
    am = Map(current_path,codes,difficulties,csv,session_numbers=False)
except IOError: #script is ran for the first time so we have to generate global difficulties
    am = Map(current_path,codes,None,csv,session_numbers=True)
    difficulties = analysis.get_difficulties(am,current_path+'/base/difficulties.json')
    am.set_difficulties(difficulties)
    

m = Map(current_path, codes, difficulties, csv, place_asked=150)
g = Graph(current_path, codes, difficulties,csv, user=10)
ag = Graph(current_path, codes, difficulties, csv,session_numbers=True)


g.success_response()
g.learning()
ag.lengths_of_sessions()
ag.number_of_answers()
ag.weekday_activity()
ag.hourly_activity()
ag.response_time_area()

m.mistaken_countries()
am.predict_success()
am.mean_success()
am.number_of_answers()
am.response_time()



