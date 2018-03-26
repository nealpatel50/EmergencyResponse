"""
Name: Neal Patel
File Name: google_maps_api.py
"""

import pandas
from django.templatetags.static import static
url = static('static/sfpd_dispatch_data_subset.csv')

stream = pandas.read_csv(url)

"""
    Files:       all_locations and call_types
    Description: Prints out the longitude and latitude for specific types of dispatches so that they can be copied and 
                 pasted into the Google Maps API to automatically create a heat map or marker map displaying dispatch 
                 frequencies and urgency over the city for those types of dispatches
"""

"""
    Function:    all_locations
    Description: Prints out every dispatch
    
"""

def all_locations():
    for i in range(len(stream)):
        location = stream.iloc[i]['location']
        print('new google.maps.LatLng' + location + ',')  # proper format accepted by API


"""
    Function:    call_types
    Description: Prints out specific markers (fire, first aid) for different call types of dispatches. The number of
                 dispatches for each call type are also added up to use for the bar graph
                 
                 fire: Structure Fire, Outside Fire, Vehicle Fire, Smoke Investigation (Outside)
                 medical: Medical Incident
                 alarm: Alarms
                 collision: Traffic Collision, Train/Rail Incident
                 service: Citizen Assist/Service Call
                 other: Other, Gas Leak, Electrical Hazard, Fuel Spill, Elevator, Odor, Water Rescue, HazMat   

"""

def call_types():
    call_types = {}
    counter = 0
    fire_count = 0
    medical_count = 0
    alarm_count = 0
    collision_count = 0
    service_count = 0
    other_count = 0
    for i in range(len(stream)):
        if stream.iloc[i]['call_type'] not in call_types:
            call_types[stream.iloc[i]['call_type']] = 0
    for i in range(len(stream)):
        counter += 1
        if stream.iloc[i]['call_type'] == 'Structure Fire' or stream.iloc[i]['call_type'] == 'Outside Fire' \
        or stream.iloc[i]['call_type'] == 'Vehicle Fire' or stream.iloc[i]['call_type'] == 'Smoke Investigation ' \
                                                                                           '(Outside)':
            latitude = stream.iloc[i]['latitude']
            longitude = stream.iloc[i]['longitude']
            text = """    var marker""" + str(counter) + """ = new google.maps.Marker({
    position: {lat: """ + str(latitude) + """, lng: """ + str(longitude) + """},  
    map: map,
    icon:fire
  });"""
            fire_count += 1
            print(text)

        if stream.iloc[i]['call_type'] == 'Medical Incident':
            latitude = stream.iloc[i]['latitude']
            longitude = stream.iloc[i]['longitude']
            text = """    var marker""" + str(counter) + """ = new google.maps.Marker({
    position: {lat: """ + str(latitude) + """, lng: """ + str(longitude) + """},  
    map: map,
    icon:medical
  });"""
            medical_count += 1
            print(text)

        if stream.iloc[i]['call_type'] == 'Alarms':
            latitude = stream.iloc[i]['latitude']
            longitude = stream.iloc[i]['longitude']
            text = """    var marker""" + str(counter) + """ = new google.maps.Marker({
    position: {lat: """ + str(latitude) + """, lng: """ + str(longitude) + """},  
    map: map,
    icon:alarm
  });"""
            alarm_count += 1
            print(text)

        if stream.iloc[i]['call_type'] == 'Traffic Collision' or stream.iloc[i]['call_type'] == 'Train / Rail Incident':
            latitude = stream.iloc[i]['latitude']
            longitude = stream.iloc[i]['longitude']
            text = """    var marker""" + str(counter) + """ = new google.maps.Marker({
    position: {lat: """ + str(latitude) + """, lng: """ + str(longitude) + """},  
    map: map,
    icon:collision
  });"""
            collision_count += 1
            print(text)

        if stream.iloc[i]['call_type'] == 'Citizen Assist / Service Call':
            latitude = stream.iloc[i]['latitude']
            longitude = stream.iloc[i]['longitude']
            text = """    var marker""" + str(counter) + """ = new google.maps.Marker({
    position: {lat: """ + str(latitude) + """, lng: """ + str(longitude) + """},  
    map: map,
    icon:service
  });"""
            service_count += 1
            print(text)

        if stream.iloc[i]['call_type'] == 'Other' or stream.iloc[i]['call_type'] == 'Gas Leak (Natural and LP Gases)' \
                or stream.iloc[i]['call_type'] == 'Electrical Hazard' or stream.iloc[i]['call_type'] == 'Fuel Spill' \
                or stream.iloc[i]['call_type'] == 'Elevator / Escalator Rescue' or stream.iloc[i]['call_type'] == \
                'Odor (Strange / Unknown)' or stream.iloc[i]['call_type'] == 'Water Rescue' or stream.iloc[i] \
                ['call_type'] == 'HazMat':
            latitude = stream.iloc[i]['latitude']
            longitude = stream.iloc[i]['longitude']
            text = """    var marker""" + str(counter) + """ = new google.maps.Marker({
    position: {lat: """ + str(latitude) + """, lng: """ + str(longitude) + """},  
    map: map,
    icon:other
  });"""
            other_count += 1
            print(text)
    print('fire:', fire_count, 'medical:', medical_count, 'alarm:', alarm_count, 'collision:', collision_count,
          'service:', service_count, 'other:', other_count)
    print(call_types)


"""
    Function:    zipcode_colors
    Description: Uses an equation to convert the dispatch times for each zipcode to an opacity percentage between 0% and
                 100% so that a map that is split up by zipcode areas can be color coded based on their dispatch times
                 
"""

def zipcode_colors():
    dispatch_times = [[94121, 574], [94104, 1007], [94124, 1011], [94116, 1020], [94123, 1023], [94111, 1028],
                      [94133, 1034], [94117, 1034], [94108, 1034], [94112, 1036], [94134, 1040], [94118, 1045],
                      [94115, 1047], [94158, 1053], [94131, 1065], [94102, 1069], [94105, 1079], [94114, 1081],
                      [94127, 1097], [94129, 1105], [94130, 1106], [94132, 1108], [94110, 1227], [94107, 1429],
                      [94109, 1472], [94122, 1577], [94103, 1757]]
    shortest = dispatch_times[0][1]
    longest = dispatch_times[26][1]
    difference = longest - shortest
    for dispatch in dispatch_times:
        dispatch[1] = (100 / difference) * (dispatch[1] - shortest)
    print(dispatch_times)



# all_locations()
# call_types()
zipcode_colors()