# -*- coding: utf-8 -*-

from map import *
import inputoutput

from argparse import ArgumentParser
from os import path,makedirs


parser = ArgumentParser(description='Generate maps for specific place.')
parser.add_argument('-i', '--items', required=True, metavar = 'ITEMS',nargs='+', help='id of a place to filter')
parser.add_argument('-f', '--file', metavar = 'FILE', help='Optional path to directory with geography-answer.csv and geography-place.csv')

args = parser.parse_args()

if args.file is None:
    working_directory = path.dirname(path.realpath(__file__))
else:
    working_directory = args.file
frame = inputoutput.load_geo_csv(working_directory+"/geography.answer.csv")
codes = inputoutput.load_general_csv(path=working_directory+'/geography.place.csv',names=['id','code','name','type'],skip_rows=1)

for item in args.items:
    m = Map(path=working_directory, codes=codes, df=frame, place_asked=int(item))

    directory = working_directory+'/maps/place/'+item+'/'
    if not path.exists(directory):
        makedirs(directory)

    print 'Generating maps for place',item
    m.mistaken_countries(path=directory)
