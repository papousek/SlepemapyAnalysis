import matplotlib
import os
from map import *
from graph import *
from importer import Importer
from exporter import Exporter

current_path = os.path.dirname(os.path.realpath(__file__))
input = Importer()
codes = input.load_general_csv(current_path+"/base/areas.csv")
csv = input.load_geo_csv(current_path+"/base/large.csv")

a = Analysis(csv,user=10)
m = Map(current_path,codes,csv,place_asked=150)
g = Graph(current_path,csv,user=10)

matplotlib.interactive(False)
'''g.lengths_of_sessions()
g.weekday(width = 0.5, colour = 'cyan')
'''
matplotlib.interactive(True)

'''
ex = Exporter()
ex.generate_index_html(current_path)
ex.export(current_path,'','')'''

