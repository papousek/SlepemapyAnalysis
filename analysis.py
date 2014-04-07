# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import datetime


"""Assignes session number to every answer.

session_duration -- duration of one session
"""

def add_session_numbers(frame,session_duration):
    result = frame.sort(['inserted'])
    result['session_number'] = (result['inserted'] - result['inserted'].shift(1) > session_duration).fillna(1).cumsum() #adds session numbers to every row
    return result


"""Calculates session lengths in seconds.
"""
def get_session_lengths(frame):
    group = frame.groupby('session_number')
    start = group.first()['inserted']
    end = group.last()['inserted']
    return (end-start)/np.timedelta64(1,'s')


"""Returns session's start and end for every session.
"""
def sessions_start_end(frame):
    result = pd.DataFrame()
    group = frame.groupby('session_number')
    result['start'] = group.first()['inserted']
    result['end'] = group.last()['inserted']
    return result


"""Returns first questions for every session.
"""
def first_questions(frame):
    return frame.groupby('session_number').apply(lambda x: x.drop_duplicates(cols=['place_asked']))


"""Returns counts of answers per weekdays (first value is Monday etc)
"""
def weekdays(frame):
    data = pd.DataFrame()
    data['weekday'] = pd.DatetimeIndex(frame.inserted).weekday
    counts = pd.DataFrame(np.arange(7)*0)
    return (counts[0]+data.weekday.value_counts()).fillna(0)


"""Returns counts of answers per hour
"""
def hours(frame):
    data = pd.DataFrame()
    data['hour'] = pd.DatetimeIndex(frame.inserted).hour
    counts = pd.DataFrame(np.arange(24)*0)
    return (counts[0]+data.hour.value_counts()).fillna(0)


"""Returns numbers of answers per country.

right (True/False/None) -- filter only right/wrong/both answers -- default is None
"""
def number_of_answers(frame,right=None):
    answers = frame
    if right:
        answers = frame[frame.place_asked==frame.place_answered]
    elif right==False:
        answers = frame[frame.place_asked!=frame.place_answered]
    return answers['place_asked'].value_counts()


"""Returns dataframe of mean response times per country.

right (True/False/None) -- filter only right/wrong/both answers -- default is None
"""
def response_time_place(frame, right=None):
    answers = frame
    if right:
        answers = answers[answers.place_asked==answers.place_answered]
    elif right == False:
        answers = answers[answers.place_asked!=answers.place_answered]
    answers = answers.groupby('place_asked')
    return answers['response_time'].mean()


"""Returns dataframe of response times, inserted.

right (True/False/None) -- filter only right/wrong/both answers -- default is None
log -- whether to return normal response times or logarithmic response times -- default is True
"""
def response_time_inserted(frame,right=None,log=True):
    answers = frame
    if right:
        answers = answers[answers.place_asked==answers.place_answered]
    elif right == False:
        answers = answers[answers.place_asked!=answers.place_answered]
    if log:
        return answers[['inserted','response_time_log']]
    else:
        return answers[['inserted','response_time']]


"""Returns counts of countries that are most mistaken for this country.

threshold -- only return top counts -- default is None (which means return all)
"""
def mistaken_countries(frame,threshold=None):
    wrong_answers = frame[frame.place_asked!=frame.place_answered]
    wrong_answers = wrong_answers['place_answered'].value_counts()
    return wrong_answers[:threshold]


"""Returns mean_success_rate for each country
"""
def mean_success_rate(frame):
    result = pd.DataFrame()
    groups = frame.groupby('place_asked')
    result['mean_success_rate'] = groups.apply(lambda x: len(x[x.place_asked==x.place_answered])/float(len(x))*100)
    result['mean_response_time'] = groups.response_time.mean()
    return result.dropna()


"""Returns length of each session.

session_duration -- duration of one session
"""
def lengths_of_sessions(frame,session_duration):
    groups = frame.groupby('user').apply(get_session_lengths)
    groups = groups.reset_index()

    maximum = groups.session_number.value_counts().max()
    groups = groups.groupby('session_number')
    return groups.apply(lambda x: x.inserted.sum()/maximum)


"""Returns progress of mean_success_rate and mean_response_time over sessions.

session_threshold -- consider only this many sessions
"""
def learning(frame,session_duration,session_threshold=None):
    first = first_questions(frame)
    
    rates = [] #collects already calculated rates
    times = [] #collects already calculated times
    if session_threshold is None:
        limit = first.session_number.max()+1
    else:
        limit = threshold

    for i in range(0,limit):
        temp = first[first.session_number<=i] #calculate with i# of sessions
        rates += [len(temp[temp.place_asked==temp.place_answered])/float(len(temp.place_asked))]
        times += [temp.response_time.mean()]

    result = pd.DataFrame() #finalize output
    result['mean_success_rate'] = rates
    result['mean_response_time'] = times
    return result