# -*- coding: utf-8 -*-

from numpy import uint32,uint16,uint8,float16
from pandas import read_csv
from yaml import dump,load
from collections import defaultdict

def load_geo_csv(path):
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
    df = read_csv(path, parse_dates=[5],dtype=types,index_col='id')
    return df


def load_general_csv(path,names = None,enc = 'utf-8',skip_rows=0):
    """Used for importing general csv

    :param names: new names for columns
    :param enc: encoding of csv file
    """

    if names is not None :
        df = read_csv(path,names=names,encoding=enc,skiprows=skip_rows)
    else:
        df = read_csv(path,encoding=enc,skiprows=skip_rows)
    return df


def defaultdict_factory():
    return (0,0)


def save_difficulties(difficulties,path):
    """Calculates and saves difficulties of countries into json file.

    :param frame: calculate from this frame
    :param path: save to this path
    """

    with open(path,'w') as diff:
        dump(difficulties,diff)


def load_difficulties(path=''):
    """Returns difficulties of countries either by loading from json or recalculating.

    :param frame: if you want to force recalculation, pass only frame
    :param path: if you want to load pre-calculated dificulties from path
    """

    if not path:
        return defaultdict(defaultdict_factory)
    else:
        with open(path) as diff:
            return load(diff)
