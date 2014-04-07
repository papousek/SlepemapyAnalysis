# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np

import colorsys
import sys

"""assorted methods for bin:
-- classification
-- manipulation
-- colouring
"""



"""Returns string in format 'rgb(r,g,b)'.
"""
def colour_value_rgb_string(r,g,b):
    return '\'rgb('+str(int(255*r))+', '+str(int(255*g))+', '+str(int(255*b))+')\''

"""Returns colour rgb value for hsv.
"""
def colour_value_hsv(h,s=1,v=1):
    colours = colorsys.hsv_to_rgb(h,s,v)
    return [colours[0],colours[1],colours[2]]

"""Generates range of colours.

length -- how many colours to generate
hue_limit -- limits the hue value -- default 0.32
"""
def colour_range(length,hue_limit=0.32):
    colors = [colour_value_hsv((hue_limit*x)/length) for x in range(length)]
    return colors
    
    
################################################################################


"""recursive helper function of nested-means
"""
def _nested_means_classification(data,num):
    if num<=0 or data.empty:
        return []
    mean = data.mean()
    return [mean]+_nested_means_classification(data[data<mean],num-1)+_nested_means_classification(data[data>=mean],num-1)

"""Data is divided by nested-means.

data -- values to bin
classes -- divide values into this many bins, should be a power of 2
"""
def nested_means_classification(data,classes=8):
    if len(data)<classes:
        return [data.min()-1,data.max()+1]
    breaks = [data.min()-1,data.max()+1]+_nested_means_classification(data,np.log2(classes))
    breaks.sort()
    return breaks

"""Data is divided by equally distant ranges.

data -- values to bin
classes -- divide values into this many bins
"""
def equidistant_classification(data,classes=8):
    x = (data.max() - data.min())/classes
    breaks = [data.min()-1,data.max()+1]+[i*x for i in range(1,classes)]
    breaks.sort()
    return breaks

"""Data is divided by jenks algorithm.

data -- values to bin
classes -- divide values into this many bins
"""
def jenks_classification(data, classes=8) :
    input = data.copy()
    input.sort()
    input = input.tolist()
    length = len(data)
    
    #define initial values of the LC and OP 
    lower_class_limits = [[1 for x in range(0,classes+1)] if y==0 else [0 for x in range(0,classes+1)] for y in range(0,length+1)] #LC
    variance_combinations = [[0 for x in range(0,classes+1)] if y==0 else [sys.maxint for x in range(0,classes+1)] for y in range(0,length+1)] #OP
    variance = 0

    #calculate optimal LC
    for i in range(1,length):
        sum = 0 #SZ
        sum_squares = 0 #ZSQ
        counter = 0 #WT

        for j in range(0,i+1):
            i3 = i - j + 1 #III
            value = input[i3-1]
            counter+=1 #WT

            sum += value
            sum_squares += value * value
            variance = sum_squares - (sum * sum) / counter
            i4 = i3 - 1 #IV
            
            if (i4 != 0) :
                for k in range(0,classes+1):
                    #deciding whether an addition of this element will increase the class variance beyond the limit
                    #if it does, break the class
                    if (variance_combinations[i][k] >= (variance + variance_combinations[i4][k - 1])) :
                        lower_class_limits[i][k] = i3
                        variance_combinations[i][k] = variance + variance_combinations[i4][k - 1]
        lower_class_limits[i][1] = 1
        variance_combinations[i][1] = variance #we can use variance_combinations in calculations of goodness-of-fit, but we do not need it right now
    
    #create breaks
    length -= 1
    breaks = []
    breaks.append(input[0]-1) #append lower bound that was not found during calculations
    breaks.append(input[length]+1) #append upper bound that was not found during calculations
    while (classes > 1):
        breaks.append(input[lower_class_limits[length][classes] - 2])
        length = lower_class_limits[length][classes] -1
        classes-=1

    breaks.sort()
    return breaks



################################################################################


"""Combines classification methods with colouring, returns binned data with assigned colours

data -- values to bin
binning_function -- which function to use for binning -- default is None (-> jenks_classification)
number_of_bins -- how many bins to divide data-- default is 8
additional_countries -- whether to add additional countries AFTER binning -- default is None
additional_labels -- whether to add additional labels AFTER calculations -- default is []
"""
def bin_data(data,binning_function=None,number_of_bins=8,additional_countries=None,additional_labels=[]):
    if binning_function is None:
        binning_function = jenks_classification
    binned = pd.DataFrame(data)
    binned = binned.reset_index()
    binned.columns=['country','counts']

    bins = binning_function(binned['counts'],number_of_bins)
    binned['bin'] = pd.cut(binned['counts'], bins=bins,labels=False)

    colours = colour_range(len(bins)-1)
    binned['r'] = binned.bin.apply(lambda x: colours[x][0])
    binned['g'] = binned.bin.apply(lambda x: colours[x][1])
    binned['b'] = binned.bin.apply(lambda x: colours[x][2])
    binned = binned.append(additional_countries)

    colours.reverse()
    colours = pd.DataFrame(colours)
    if additional_countries is not None:
        colours = colours.append([[additional_countries.r.values[0],additional_countries.g.values[0],additional_countries.b.values[0]]],ignore_index=True)         
    colours = colours.append([colour_value_hsv(0,s=0)]) #special colour for No data bin
    colours.columns = ['r','g','b']
    colours['label'] = bins_to_string(bins)+additional_labels+['No data']
    return (binned,colours)


""" Returns list of strings from the bins in the interval form: (lower,upper]

bins -- bins to get strings from
"""
def bins_to_string(bins):
    bins[0]+=1 #corrections for bins
    bins[-1]-=1
    bins = [round(x,2) for x in bins]
    labels = ['('+str(bins[curr])+', '+str(bins[curr+1])+']' for curr in range(len(bins)-1)]
    labels.reverse()
    return labels