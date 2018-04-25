# -*- coding: utf-8 -*-
#bunch of libraries #
import http.client, urllib.request, urllib.parse, urllib.error, base64
import json
import pprint
import json
import csv
import dateutil.parser
import datetime


#method to print prettier
pp=pprint.PrettyPrinter(indent=4)

headers = {
    # Request headers
    'Accept': 'application/json',
    'Ocp-Apim-Subscription-Key': '8bc665be00d44f229e30136fe4196eb7',
}

params = urllib.parse.urlencode({
})


#ask user for inputs
print("give date input: 2018-04-XX")
dateInput =  '2018-04-' + str(input())
print(dateInput)
print('- ' * 20)

print('select departure airport')
airport = str(input()).upper()
print(airport)
print('- ' * 20)


#access Swedavia API
try:
    conn = http.client.HTTPSConnection('api.swedavia.se')
    conn.request("GET", "/flightinfo/v2/"+ airport +"/departures/" + dateInput + "%s" % params, "{body}", headers)
    # conn.request("GET", finalURL % params, headers)    
    response = conn.getresponse()
    data = response.read()
    # print(data)
    conn.close()
except Exception as e:
    pp.pprint("[Errno {0}] {1}".format(e.errno, e.strerror))



#transform the data from the API into json, and clear it up
data = data.decode('utf8')
data = data.replace("'", '"')
data = data.replace("ö", "o").replace("Ö", "O")
data = data.replace("å", "a").replace("Å", "A")
data = data.replace("ä", "a").replace("Ä", "A")
data = data.replace("ü", "u").replace("Ü", "U")
DataJSON = data

# pp.pprint(DataJSON)
print(type(DataJSON))
print('- ' * 20)

data = json.loads(DataJSON)
s = json.dumps(data, indent=4, sort_keys=True)

filenameJson = str(airport)+str(dateInput)+".json"
docJson = open(filenameJson, 'w')
docJson.write(DataJSON)


flights = (data["flights"])
flight = flights


print('- ' * 20)
print("Choose an output filename:")
filename = '[' + airport + '-' + dateInput + '] ' + str(input()) +  '.csv'
print('your file will be called ' + filename)
print('- ' * 20)

doc = open(filename, 'w')
columnTitleRow = "flight ID, Destination, Destination_IATA, Continent, Country, Time, Distance, Emissions, TaxCuts\n"
doc.write(columnTitleRow)



#Calculate all the stuff
for i in range (len(flights)):
# for i in range (0,50):
    # pp.pprint(flights[i])

    #get flight ID, and destination codes, generate URL. 
    flightID=flights[i]['flightId']
    destinationIATA = flights[i]['flightLegIdentifier']['arrivalAirportIata']
    destinationEnglish = flights[i]['arrivalAirportEnglish']
    destinationEnglish_noSpace = destinationEnglish.replace(" ", "")
    departureTime = flights[i]['departureTime']['scheduledUtc']
    finalURL = 'https://www.distance24.org/route.json?stops=stockholm|' + (destinationEnglish_noSpace)
    flights['finalURL'] : finalURL
    

    #access URL, gets Json and calculate distance.
    accessURL = urllib.request.urlopen(finalURL)
    distanceData = json.load(accessURL)
    distance = float(distanceData['distance'])
    if (distance < 463):
        emissions = distance*0.257
    else: 
        emissions = distance*0.177

    #calculate tax cuts (according to that paper)
    taxCuts = (emissions/2.24)*6.5  


    # find continent and country of destination
    try: 
        # distanceData['stops'][1]['timeZone']['id']
        continent = distanceData['stops'][1]['timeZone']['id']
    except KeyError: 
            continent =  "null" 
    
    if ( "Africa" in continent):
        continent = "Africa"
    elif ('Europe' in continent):
        continent = "Europe"
    elif ('Asia' in continent):     
        continent = 'Asia'
    elif('America' in continent):
        continent = 'America'
    else:
        continent = "other"

    print(continent)
    
    try: 
        countryCode = distanceData['stops'][1]['countryCode']
    except KeyError:
        coutryCode = "null"

    print(countryCode)
    

    departureTimeParsed = dateutil.parser.parse(departureTime)

    # pp.pprint(flights[i])

    flights[i]["distance (in KM)"] = distance
    flights[i]["emissions (in Kg)"] = emissions
    flights[i]["taxCuts (in SEK)"] = taxCuts
    flights[i]['Destination Continent'] = continent
    flights[i]['Destination Country'] = countryCode

    row = flightID +','+ destinationEnglish+','+ destinationIATA+','+ continent+','+countryCode +','+ str(departureTime)  +','+ str(distance) +','+ str(emissions) +','+ str(taxCuts) +','+ '\n'
    doc.write(row)

    print("writing doc. in row: " + str(i))
    
    summary = ("this is flight ID " + flightID +   " its going to " + destinationIATA +  " Scheduled Departure  " + departureTime + " the url is " + finalURL + " Total Distance " + str(distance) + " carbon emissions " + str(emissions) + ' gov tax cuts ' + str(taxCuts))
    



import winsound
duration = 1000  # millisecond
freq = 440  # Hz
winsound.Beep(freq, duration)   
print("Done!")
