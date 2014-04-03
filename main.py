import matplotlib
import os
from map import *
from graph import *
from importer import Importer

current_path = os.path.dirname(os.path.realpath(__file__))
input = Importer()
codes = input.load_general_csv(current_path+"/base/areas.csv")
csv = input.load_geo_csv(current_path+"/base/large.csv")

a = Analysis(csv,user=10)
m = Map(current_path,csv,codes,place_asked=150)
g = Graph(current_path,csv,codes,user=10)
am = Map(current_path,csv,codes)
ag = Graph(current_path,csv,codes)


g.lengths_of_sessions()
g.learning()

ag.weekday_activity()
ag.hourly_activity()
ag.response_time_area()


m.mistaken_countries()
am.number_of_answers()
am.response_time()
am.avg_success()



