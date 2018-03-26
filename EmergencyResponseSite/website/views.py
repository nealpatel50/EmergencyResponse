from __future__ import unicode_literals

from django.shortcuts import render

from django.http import HttpResponse
from django.template import loader
from django.conf import settings

import math
import pandas
import sys
import operator
import os
from django.contrib.staticfiles.templatetags.staticfiles import static


def index(request):
    template = loader.get_template('website/index.html')
    print(request.POST)
    address = None
    time = None
    try:
        address = request.POST['address']
        time = request.POST['time']
    except:
        address = 'address'
        time = 'time'
    file = open(os.path.join(settings.STATIC_ROOT, 'website/sfpd_dispatch_data_subset.csv'))
    stream = pandas.read_csv(file)
    num_of_closest_locs = 10
    max_dist = 5
    hours_between = 3
    total_medical_incidents = 6791
    context = {
        
    }
    return HttpResponse(template.render(context, request))

"""
    Function:    distance
    Description: Finds the distance between two GPS coordinates, factoring in the curvature of the Earth using a 
                 simplified version of the Haversine formula
"""
def distance(loc1_latitude, loc1_longitude, loc2_latitude, loc2_longitude):
    earth_radius = 6371
    deg_to_dist_coeff = earth_radius/360
    dist_latitude = (loc2_latitude - loc1_latitude) * deg_to_dist_coeff
    dist_longitude = (loc2_longitude - loc1_longitude) * deg_to_dist_coeff * math.cos(loc1_latitude * math.pi/180)
    dist = math.sqrt(dist_latitude * dist_latitude + dist_longitude * dist_longitude)
    return dist


"""
    Function:    convert_to_min
    Description: Takes a time string in the time format 'HH:MM:SS' and converts it to seconds

"""

def convert_to_min(time_str):
    h, m, s = time_str.split(":")
    return int(h) * 60 + int(m)

"""
    Function:    truncate
    Description: Takes a float, f, and truncates it to n decimal places without rounding

"""

def truncate(f, n):
    s = '{}'.format(f)
    if 'e' in s or 'E' in s:
        return '{0:.{1}f}'.format(f, n)
    i, p, d = s.partition('.')
    return '.'.join([i, (d+'0'*n)[:n]])

"""
    Function:    update_closest
    Description: If current location is closer than the furthest location in closest, is within a 3 km radius, and 
                 occurred close to the time of the incident, then the location of the furthest location in the list is 
                 updated with the current location    
"""
def update_closest(closest, i, dist, time, time2):
    largest_ele = 0
    largest_ele_index = -1
    global num_of_closest_locs
    for j, ele in enumerate(closest):
        if ele[0] >= largest_ele:
            largest_ele = ele[0]
            largest_ele_index = j
    if dist < largest_ele and dist <= max_dist and abs(time2 - time) <= hours_between * 60:
        closest[largest_ele_index] = [dist, stream.iloc[i]]


"""
    Function:    closest_locations
    Description: Creates a list of closest locations and calls the distance function and update_closest function on the
                 location passed in and returns a list of closest locations with their corresponding distances
"""

def closest_locations(loc1_latitude, loc1_longitude, time):
    global num_of_closest_locs
    time = convert_to_min(time)
    closest = [(sys.maxsize, []) for i in range(num_of_closest_locs)]
    for i in range(len(stream)):
        loc2_latitude = stream.iloc[i]['latitude']
        loc2_longitude = stream.iloc[i]['longitude']
        received_timestamp = stream.iloc[i]['received_timestamp']
        time2 = received_timestamp[10:19]
        time2 = convert_to_min(time2)
        dist = distance(loc1_latitude, loc1_longitude, loc2_latitude, loc2_longitude)
        update_closest(closest, i, dist, time, time2)
    for k, ele in enumerate(closest):
        if ele[0] == sys.maxsize:
            closest.pop(k)
            num_of_closest_locs -= 1
    return closest


"""
    Function:    dispatch_probabilities
    Description: Calls closest_locations on the location passed in and predicts the proportion of each unit type
                 by adding up each unit type and dividing it by the total number of closest locations. Returns 
                 dictionary with the likely unit types and their corresponding probabilities
"""

def dispatch_probabilities(loc1_latitude, loc1_longitude, time):
    closest = closest_locations(loc1_latitude, loc1_longitude, time)
    global num_of_closest_locs
    unit_types = {}
    probabilities = {}
    for i in range(len(stream)):
        if stream.iloc[i]['unit_type'] not in unit_types:
            unit_types[stream.iloc[i]['unit_type']] = 0
    for ele in closest:
        unit_types[ele[1][27]] += 1
    for unit in unit_types:
        if unit_types[unit] != 0:
            prob = unit_types[unit] / num_of_closest_locs
            prob = truncate(prob, 3)
            probabilities[unit] = prob
    return probabilities


"""
    Function:    most_likely_dispatch
    Description: Calls dispatch_probabilities on the location passed in and determines the most likely unit type to
                 occur in that location by finding the location with the highest probability
"""

def most_likely_dispatch(loc1_latitude, loc1_longitude, time):
    probabilities = dispatch_probabilities(loc1_latitude, loc1_longitude, time)
    sorted_probabilities = sorted(probabilities.items(), key=operator.itemgetter(1))
    most_likely = sorted_probabilities[len(sorted_probabilities) - 1][0]
    return most_likely

"""
    Function:    convert_to_sec
    Description: Takes a time string in the time format 'HH:MM:SS' and converts it to seconds
    
"""

def convert_to_sec(time_str):
    h, m, s = time_str.split(":")
    return int(h) * 3600 + int(m) * 60 + int(s)

"""
    Function:    update_dispatch_times
    Description: Takes a dictionary of zipcodes and finds the average dispatch time for each zipcode and updates the
                 dictionary. Subtracts the received time from the on scene time after converting time format to seconds
                 to find the total dispatch time for each dispatch at a zipcode. Divides the total dispatch time by
                 the total number of zipcodes to get the average dispatch time.
"""

def update_dispatch_times(dispatch_times):
    total_dispatch_time = 0
    counter = 0
    for code in dispatch_times.keys():
        for j in range(len(stream)):
            if pandas.isnull(stream['on_scene_timestamp'].iloc[j]):
                continue
            if code == stream.iloc[j]['zipcode_of_incident']:
                received_time = stream.iloc[j]['received_timestamp']
                received_time = str(received_time)
                received_time = received_time[10:19]
                on_scene_time = stream.iloc[j]['on_scene_timestamp']
                on_scene_time = str(on_scene_time)
                on_scene_time = on_scene_time[10:19]
                received_time_sec = convert_to_sec(received_time)
                on_scene_time_sec = convert_to_sec(on_scene_time)
                time_diff = abs(on_scene_time_sec - received_time_sec)
                total_dispatch_time = total_dispatch_time + time_diff
                counter += 1
        average_dispatch_time = int(total_dispatch_time / counter)
        dispatch_times[code] = average_dispatch_time
    return dispatch_times

"""
    Function:    sort_dispatch_times
    Description: Takes the dictionary of zipcodes with their average dispatch times in seconds and sorts it, giving a
                 list of the average times from least to greatest. Uses timedelta to convert the seconds back into the
                 time format 'HH:MM:SS'
"""

def sort_dispatch_times(updated_dispatch_times):
    sorted_dispatch_times = sorted(updated_dispatch_times.items(), key=operator.itemgetter(1))
    sorted_dispatch_times = [list(tuple) for tuple in sorted_dispatch_times]
    for code in sorted_dispatch_times:
        code[1] = str(datetime.timedelta(seconds=(code[1])))
    return sorted_dispatch_times

"""
    Function:    area_dispatch_times
    Description: Creates a dictionary of zipcodes and calls update_dispatch_times and sort_dispatch_times to form a
                 list of zipcodes sorted by their average dispatch times from shortest to longest
"""

def area_dispatch_times():
    dispatch_times = {}
    for i in range(len(stream)):
        if stream.iloc[i]['zipcode_of_incident'] not in dispatch_times:
            dispatch_times[stream.iloc[i]['zipcode_of_incident']] = 0
    updated_dispatch_times = update_dispatch_times(dispatch_times)
    sorted_dispatch_times = sort_dispatch_times(updated_dispatch_times)
    return sorted_dispatch_times

"""
    Function:    longest_dispatch_times
    Description: Calls the dispatch_times function and creates a sublist of the five zipcodes with the longest dispatch
                 times
"""

def longest_dispatch_times():
    dispatch_times = area_dispatch_times()
    longest_dispatches = dispatch_times[-5:]
    return longest_dispatches


"""
    Function:    als_frequency
    Description: Finds the percentages of medical incident dispatches where an ambulance with (or without) advanced life 
                 support was sent where the incident was considered non (or potentially) life-threatening.

"""

def als_frequency():
    als_no_threat_counter = 0
    als_threat_counter = 0
    no_als_no_threat_counter = 0
    no_als_threat_counter = 0
    for i in range(len(stream)):
        if stream.iloc[i]['call_type'] == 'Medical Incident' and stream.iloc[i]['als_unit'] is True and \
        stream.iloc[i]['call_type_group'] == 'Non Life-threatening':
            als_no_threat_counter += 1
        if stream.iloc[i]['call_type'] == 'Medical Incident' and stream.iloc[i]['als_unit'] is True and \
        stream.iloc[i]['call_type_group'] == 'Potentially Life-Threatening':
            als_threat_counter += 1
        if stream.iloc[i]['call_type'] == 'Medical Incident' and stream.iloc[i]['als_unit'] is False and \
        stream.iloc[i]['call_type_group'] == 'Non Life-threatening':
            no_als_no_threat_counter += 1
        if stream.iloc[i]['call_type'] == 'Medical Incident' and stream.iloc[i]['als_unit'] is False and \
        stream.iloc[i]['call_type_group'] == 'Potentially Life-Threatening':
            no_als_threat_counter += 1
    als_no_threat_percent = truncate((als_no_threat_counter / total_medical_incidents), 3)
    als_threat_percent = truncate((als_threat_counter / total_medical_incidents), 3)
    no_als_no_threat_percent = truncate((no_als_no_threat_counter / total_medical_incidents), 3)
    no_als_threat_percent = truncate((no_als_threat_counter / total_medical_incidents), 3)
    return 'als_no_threat_percent:', als_no_threat_percent, 'als_threat_percent', als_threat_percent, \
    'no_als_no_threat_percent:', no_als_no_threat_percent, 'no_als_threat_percent', no_als_threat_percent