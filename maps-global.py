# -*- coding: utf-8 -*-

from map import *
import inputoutput

from argparse import ArgumentParser
from os import path,makedirs


parser = ArgumentParser(description='Generate global maps.')
parser.add_argument('-f', '--file', metavar = 'FILE', help='Optional path to directory with geography-answer.csv, geography-place.csv and difficulties.yaml')

args = parser.parse_args()

if args.file is None:
    working_directory = path.dirname(path.realpath(__file__))
else:
    working_directory = args.file
frame = inputoutput.load_geo_csv(working_directory+"/geography.answer.csv")
diff = inputoutput.load_difficulties(path=working_directory+'/difficulties.yaml')
codes = inputoutput.load_general_csv(path=working_directory+'/geography.place.csv',names=['id','code','name','type'],skip_rows=1)

m = Map(path=working_directory, codes=codes, difficulties=diff, df=frame)

directory = working_directory+'/maps/global/'
if not path.exists(directory):
    makedirs(directory)

print 'Generating global maps'
m.difficulty(path=directory)
m.success(path=directory)
m.number_of_answers(path=directory)
m.response_time(path=directory)
