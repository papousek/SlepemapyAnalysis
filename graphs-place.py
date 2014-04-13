# -*- coding: utf-8 -*-

from graph import *
import inputoutput

from argparse import ArgumentParser
from os import path,makedirs


parser = ArgumentParser(description='Generate graphs for specific place.')
parser.add_argument('-i', '--items', required=True, metavar = 'ITEMS',nargs='+', help='id of a place to filter')
parser.add_argument('-f', '--file', metavar = 'FILE', help='Optional path to directory with geography-answer.csv and difficulties.yaml')

args = parser.parse_args()

if args.file is None:
    working_directory = path.dirname(path.realpath(__file__))
else:
    working_directory = args.file
frame = inputoutput.load_geo_csv(working_directory+"/geography.answer.csv")
diff = inputoutput.load_difficulties(path=working_directory+'/difficulties.yaml')

for item in args.items:
    g = Graph(path, difficulties = diff, df = frame, place_asked=int(item))
    
    directory = working_directory+'/graphs/place/'+item+'/'
    if not path.exists(directory):
        makedirs(directory)
        
    print 'Generating graphs for place',item    
    g.success(path=directory)
    g.skill(path=directory)