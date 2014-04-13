# -*- coding: utf-8 -*-

from numpy import uint32,uint16,uint8,float16
from pandas import read_csv
from json import load,dump
from collections import defaultdict

def load_geo_csv(filepath):
    """Imports csv into pandas DataFrame

    default dtypes:
    
    - 'user':uint32
    - 'id':uint32
    - 'place_asked':uint16
    - 'place_answered':float16 -- has to be float, because uint does not understand NaN (which place_answered may contain)
    - 'type':uint8
    - 'response_time':uint32
    - 'number_of_options':uint8
    - 'place_map':float16 -- has to be float, because uint does not understand NaN (which place_map may contain)
    
    """
    
    types = {'user':uint32,'id':uint32,'place_asked':uint16,'place_answered':float16,'type':uint8,'response_time':uint32,'number_of_options':uint8,'place_map':float16}
    df = read_csv(filepath, parse_dates=[5],dtype=types,index_col='id')
    return df


def load_general_csv(filepath,columns = None,enc = 'utf-8'):
    """Used for importing general csv
    
    :param columns: filtering out columns
    :param enc: encoding of csv file
    """
    
    if columns is not None:
        df = read_csv(filepath,usecols=columns,encoding=enc)
    else:
        df = read_csv(filepath,encoding=enc)
    return df


def save_difficulties(difficulties,path):
    """Calculates and saves difficulties of countries into json file.
    
    :param frame: calculate from this frame
    :param path: save to this path
    """
    
    dump(difficulties,open(path,'w'))
    

def load_difficulties(path=''):
    """Returns difficulties of countries either by loading from json or recalculating.
    
    :param frame: if you want to force recalculation, pass only frame 
    :param path: if you want to load pre-calculated dificulties from path
    """
    
    tuple_factory = lambda : (0,0)
    if not path:
        return defaultdict(tuple_factory)
    else:
        return defaultdict(tuple_factory,load(open(path)))