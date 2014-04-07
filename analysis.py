# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import datetime



def add_session_numbers(frame,session_duration):
    """Assignes session number to every answer.

    :param session_duration: duration of one session
    """

    result = frame.sort(['inserted'])
    result['session_number'] = (result['inserted'] - result['inserted'].shift(1) > session_duration).fillna(1).cumsum() #adds session numbers to every row
    return result


def get_session_lengths(frame):
    """Calculates session lengths in seconds.
    """

    group = frame.groupby('session_number')
    start = group.first()['inserted']
    end = group.last()['inserted']
    return (end-start)/np.timedelta64(1,'s')


def sessions_start_end(frame):
    """Returns session's start and end for every session.
    """

    result = pd.DataFrame()
    group = frame.groupby('session_number')
    result['start'] = group.first()['inserted']
    result['end'] = group.last()['inserted']
    return result


def first_questions(frame):
    """Returns first questions for every session.
    """

    return frame.groupby('session_number').apply(lambda x: x.drop_duplicates(cols=['place_asked']))


def weekdays(frame):
    """Returns counts of answers per weekdays (first value is Monday etc)
    """

    data = pd.DataFrame()
    data['weekday'] = pd.DatetimeIndex(frame.inserted).weekday
    counts = pd.DataFrame(np.arange(7)*0)
    return (counts[0]+data.weekday.value_counts()).fillna(0)


def hours(frame):
    """Returns counts of answers per hour
    """

    data = pd.DataFrame()
    data['hour'] = pd.DatetimeIndex(frame.inserted).hour
    counts = pd.DataFrame(np.arange(24)*0)
    return (counts[0]+data.hour.value_counts()).fillna(0)


def number_of_answers(frame,right=None):
    """Returns numbers of answers per country.

    :param right: filter only right/wrong/both answers
    :type right: True/False/None -- default is None
    """

    answers = frame
    if right:
        answers = frame[frame.place_asked==frame.place_answered]
    elif right==False:
        answers = frame[frame.place_asked!=frame.place_answered]
    return answers['place_asked'].value_counts()


def response_time_place(frame, right=None):
    """Returns dataframe of mean response times per country.
    
    :param right: filter only right/wrong/both answers
    :type right: True/False/None -- default is None
    """

    answers = frame
    if right:
        answers = answers[answers.place_asked==answers.place_answered]
    elif right == False:
        answers = answers[answers.place_asked!=answers.place_answered]
    answers = answers.groupby('place_asked')
    return answers['response_time'].mean()


def response_time_inserted(frame,right=None,log=True):
    """Returns dataframe of response times, inserted.
    
    :param right: filter only right/wrong/both answers
    :type right: True/False/None -- default is None
    :param log: whether to return normal response times or logarithmic response times -- default is True
    """

    answers = frame
    if right:
        answers = answers[answers.place_asked==answers.place_answered]
    elif right == False:
        answers = answers[answers.place_asked!=answers.place_answered]
    if log:
        return answers[['inserted','response_time_log']]
    else:
        return answers[['inserted','response_time']]


def mistaken_countries(frame,threshold=None):
    """Returns counts of countries that are most mistaken for this country.

    :param threshold: only return top counts -- default is None (which means return all)
    """

    wrong_answers = frame[frame.place_asked!=frame.place_answered]
    wrong_answers = wrong_answers['place_answered'].value_counts()
    return wrong_answers[:threshold]


def mean_success_rate(frame):
    """Returns mean_success_rate for each country
    """

    result = pd.DataFrame()
    groups = frame.groupby('place_asked')
    result['mean_success_rate'] = groups.apply(lambda x: len(x[x.place_asked==x.place_answered])/float(len(x))*100)
    result['mean_response_time'] = groups.response_time.mean()
    return result.dropna()


def lengths_of_sessions(frame,session_duration):
    """Returns length of each session.

    :param session_duration: duration of one session
    """

    if len(frame.groupby('user'))==1:
        groups = get_session_lengths(frame)
    else:
        groups = frame.groupby('user').apply(get_session_lengths)
    groups = groups.reset_index()

    maximum = groups.session_number.value_counts().max()
    groups = groups.groupby('session_number')
    return groups.apply(lambda x: x.inserted.sum()/maximum)


def learning(frame,session_duration,session_threshold=None):
    """Returns progress of mean_success_rate and mean_response_time over sessions.

    :param session_threshold: consider only this many sessions
    """

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