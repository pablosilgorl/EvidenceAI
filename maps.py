import json
from datetime import datetime, timedelta
import re


start_date=datetime.strptime("2022-09-11T15:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
end_date=datetime.strptime("2023-09-26T19:30:00Z", "%Y-%m-%dT%H:%M:%SZ")
MONTHS = ['JANUARY', 'FEBRUARY', 'MARCH', 'APRIL', 'MAY', 'JUNE', 'JULY', 'AUGUST', 'SEPTEMBER', 'OCTOBER', 'NOVEMBER', 'DECEMBER']
time_place = {}
total_seconds = 0
locations_by_date = {}
city = ""

def insert_location_and_date_time(address, starttimestamp, seconds):
    global city
    global time_place
    global total_seconds
    global locations_by_date
    date = str(starttimestamp.date())
    display_date = "<h2 id=\"display-date\">"+starttimestamp.date().strftime("%d/%m/%Y")+" UBICACIONES</h2>"
    content = starttimestamp.time().strftime('%H:%M:%S')+" "+address+" "+convert_seconds_to_hours(seconds)
    if city != "" and re.search(city, content, re.IGNORECASE):
        pos = re.search(city, content, re.IGNORECASE).span()[0]
        content = insert_string_in_string(content, "<mark>", pos)
        content = insert_string_in_string(content, "</mark>", pos+6+len(city))
    if locations_by_date.get(date)!=None:
        locations_by_date[date].append(content)
    else:
        locations_by_date[date]=[display_date,content]

    if time_place.get(address)!=None:
        time_place[address]+=seconds
        total_seconds+=seconds
    else:
        time_place[address]=seconds
        total_seconds+=seconds

def insert_string_in_string(bigstring, smallstring, index):
    return bigstring[:index] + smallstring + bigstring[index:]

def convert_seconds_to_hours(seconds):
    min, sec = divmod(seconds, 60)
    hour, min = divmod(min, 60)
    return '%dh%02dm%02ds' % (hour, min, sec)

def get_statistics(data):
    global city
    global time_place
    global total_seconds
    global locations_by_date
    # Check if the JSON structure contains 'timelineObjects' (some files have this structure)
    if 'timelineObjects' in data:
        locations = data['timelineObjects']
    else:
        # If not, assume the 'locations' key is directly in the JSON root
        locations = data['locations']

    # Process the JSON data

    for location in locations:
        if 'placeVisit' in location:
            place = location['placeVisit']['location']
            starttimestampms = location['placeVisit']['duration']['startTimestamp']
            endtimestampms = location['placeVisit']['duration']['endTimestamp']

        else:
            place = location['activitySegment']['startLocation']
            starttimestampms = location['activitySegment']['duration']['startTimestamp']
            endtimestampms = location['activitySegment']['duration']['endTimestamp']

        if place.get('address')!=None:
            address = place['address']
        elif place.get('name')!=None:
            address = place['name']
        else:
            address = "TRANSPORT"

        try:
            starttimestamp = datetime.strptime(starttimestampms, "%Y-%m-%dT%H:%M:%S.%fZ")
        except ValueError:
            starttimestamp = datetime.strptime(starttimestampms, "%Y-%m-%dT%H:%M:%SZ")
        try:
            endtimestamp = datetime.strptime(endtimestampms, "%Y-%m-%dT%H:%M:%S.%fZ")
        except ValueError:
            endtimestamp = datetime.strptime(endtimestampms, "%Y-%m-%dT%H:%M:%SZ")   

        if starttimestamp.date() == endtimestamp.date():
            seconds = (endtimestamp-starttimestamp).total_seconds()
            if "Bogo" not in address and start_date < starttimestamp and end_date > endtimestamp:
                insert_location_and_date_time(address, starttimestamp, seconds)
        else:
            while starttimestamp.date() != endtimestamp.date():
                seconds = ((starttimestamp+ timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)-starttimestamp).total_seconds()
                if "Bogo" not in address and start_date < starttimestamp and end_date > endtimestamp:
                    insert_location_and_date_time(address, starttimestamp, seconds)
                starttimestamp = (starttimestamp+ timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            seconds = (endtimestamp-starttimestamp).total_seconds()
            if "Bogo" not in address and start_date < starttimestamp and end_date > endtimestamp:
                insert_location_and_date_time(address, starttimestamp, seconds)

def process_data():
    # Load the JSON data from the file
    global locations_by_date
    global time_place
    global total_seconds
    locations_by_date.clear()
    for year in  [2022,2023]:
        for month in MONTHS:
            json_file_path = 'maps\\'+str(year)+'\\'+str(year)+'_'+month+'.json'
            try:
                with open(json_file_path, 'r', encoding = 'utf-8') as json_file:
                    data = json.load(json_file)
                get_statistics(data)
                time_city = {}
                print(year, month)
                for key in time_place:
                    if len(key.split(",")) != 1:
                        city = key.split(",")[-2]+", "+key.split(",")[-1]
                    else:
                        city = key
                    city = re.sub(r'[0-9]+', '', city)
                    while city[0]==" " or city[0]=="-":
                        city=city[1:]
                    if time_city.get(city)!=None:
                        time_city[city]+=time_place[key]
                    else:
                        time_city[city]=time_place[key]

                for key in time_city:
                    print(key ,round(time_city[key]/total_seconds*100,2), "%")
                    
                time_place = {}
                total_seconds = 0
            except FileNotFoundError:
                print(f"File '{json_file_path}' not found.")

process_data()