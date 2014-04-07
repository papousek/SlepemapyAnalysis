import matplotlib
import os
from map import *
from graph import *
import importer


current_path = os.path.dirname(os.path.realpath(__file__))
codes = importer.load_general_csv(current_path+"/base/areas.csv")
csv = importer.load_geo_csv(current_path+"/base/large.csv")


m = Map(current_path,codes,csv,user=10)
g = Graph(current_path,codes,csv,user=10)
am = Map(current_path,codes,csv)
ag = Graph(current_path,codes,csv,add_session_numbers=True)


g.lengths_of_sessions()
g.learning()
g.response_time_inserted()

ag.weekday_activity()
ag.hourly_activity()
ag.response_time_area()


m.mistaken_countries()
am.number_of_answers()
am.response_time()
am.mean_success_rate()



