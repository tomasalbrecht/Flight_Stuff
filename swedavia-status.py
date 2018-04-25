# -*- coding: utf-8 -*-
#bunch of libraries #
import http.client, urllib.request, urllib.parse, urllib.error, base64
import json
import pprint
import json
import csv
import datetime
import dateutil
import time
import threading
import requests


#method to print prettier
pp=pprint.PrettyPrinter(indent=4)

headers = {
    # Request headers
    'Accept': 'application/json',
    'Ocp-Apim-Subscription-Key': '8bc665be00d44f229e30136fe4196eb7',
}

params = urllib.parse.urlencode({
})


timenow = datetime.datetime.now()
today = datetime.datetime.strftime(timenow, "%Y-%m-%d")
print(timenow)
# print(type(timenow))

#ask user for inputs
print("give date input: 2018-04-XX")
dateInput =  '2018-04-' + str(input())
print(dateInput)
print('- ' * 20)

# print('select departure airport')
# airport = str(input()).upper()
# print(airport)
# print('- ' * 20)

airport = "ARN"
print("Checking Arlanda departures .... ")
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


print(type(data))
#transform the data from the API into json, and clear it up
data = data.decode('utf8')
data = data.replace("'", '"')
data = data.replace("ö", "o").replace("Ö", "O")
data = data.replace("å", "a").replace("Å", "A")
data = data.replace("ä", "a").replace("Ä", "A")
data = data.replace("ü", "u").replace("Ü", "U")
DataJSON = data
print(type(DataJSON))

# pp.pprint(DataJSON)
# print(type(DataJSON))
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
filename = '[' + airport + '-' + dateInput + " with prices]" + str(input()) +  '.csv'
print('your file will be called ' + filename)
print('- ' * 20)

doc = open(filename, 'w')
columnTitleRow = "entryID, flight ID, Destination, Destination_IATA, Continent, Country, Time, Status, Price, Distance, Emissions, TaxCuts \n"
doc.write(columnTitleRow)



#Calculate all the stuff
for i in range (len(flights)):
# for i in range (0,5):
    # pp.pprint(flights[i])

    #get flight ID, and destination codes, generate URL. 
    flightID=flights[i]['flightId']
    dataID = str(i)
    destinationIATA = flights[i]['flightLegIdentifier']['arrivalAirportIata']
    destinationEnglish = flights[i]['arrivalAirportEnglish']
    destinationEnglish_noSpace = destinationEnglish.replace(" ", "")
    departureTime = flights[i]['departureTime']['scheduledUtc']
    finalURL = 'https://www.distance24.org/route.json?stops=stockholm|' + (destinationEnglish_noSpace)
    flights['finalURL'] : finalURL

    # departureTimeParsed = dateutil.parser.parse(departureTime)
    departureTimeParsed =  datetime.datetime.strptime(departureTime, "%Y-%m-%dT%H:%M:%SZ") #"YYYY-MM-DDTHH:MM:SS %Z")
    # print(type(departureTimeParsed))

    flightStatus = flights[i]['locationAndStatus']['flightLegStatusEnglish']
    print(flightStatus)

    # if(timenow > departureTimeParsed):
    #     print("this ship has sailed")
    #     flightStatus = "Departed"
    # else:
    #     print("not yet")
    #     flightStatus = "Still in STHLM"      

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

    # print(continent)
    
    try: 
        countryCode = distanceData['stops'][1]['countryCode']
    except KeyError:
        coutryCode = "null"

    flights[i]["distance (in KM)"] = distance
    flights[i]["emissions (in Kg)"] = emissions
    flights[i]["taxCuts (in SEK)"] = taxCuts
    flights[i]['Destination Continent'] = continent
    flights[i]['Destination Country'] = countryCode
    flights[i]['DepartureTimeParsed'] = departureTimeParsed
    flights[i]['Flight Status'] = flightStatus
    flights[i]['ID'] = dataID

    print("flightStatus " + flightStatus)
    # print("in dict: " + flights[i]['Flight Status'])

    price_parameters = {
            "currency" : "SEK",
            "origin" : airport,
            "destination" : flight[i]['flightLegIdentifier']['arrivalAirportIata'],
            "depart_date" : timenow}

    

    pricesURL = requests.get("http://api.travelpayouts.com/v2/prices/latest?currency=usd&period_type=year&page=1&limit=30&show_to_affiliates=true&sorting=price&trip_class=0&token=fc796b73d53c1b96aae3d2a7af9cdb76", data= price_parameters)
    pp.pprint(pricesURL.url)
    pricesdata = pricesURL.json()
    pp.pprint(pricesdata)
    try:
        pricesdata = pricesdata['data'][0]['value']
        flights[i]['price'] = pricesdata
        price = pricesdata
        # pp.pprint(pricesdata)
    except IndexError:
        princesdata = 15000    
        flights[i]['price'] = pricesdata
        # price = pricesdata    

    print(pricesdata)        


    row = dataID + ',' + flightID +','+ destinationEnglish+','+ destinationIATA+','+ continent+','+countryCode +','+ str(departureTime) +','+ flightStatus +','+ ',' + str(distance) +','+ str(emissions) +','+ str(taxCuts)  +'\n'
    doc.write(row)
    #+ str(pricesdata) +',' + str(pricesURL) 
    print("writing doc. in row: " + str(i))        

    print(10*"---")
    flights[i]['row'] = row



import winsound
duration = 1000  # millisecond
freq = 440  # Hz
winsound.Beep(freq, duration)   
print("Done!")


def CheckStatus():
    print("Checking Flight Status")
    conn2 = http.client.HTTPSConnection('api.swedavia.se')
    conn2.request("GET", "/flightinfo/v2/"+ airport +"/departures/" + dateInput + "%s" % params, "{body}", headers)
    # conn.request("GET", finalURL % params, headers)    
    response2 = conn2.getresponse()
    updateData = response2.read()
    updateData = updateData.decode('utf8').replace("'", '"').replace("ö", "o").replace("Ö", "O").replace("å", "a").replace("Å", "A").replace("ä", "a").replace("Ä", "A").replace("ü", "u").replace("Ü", "U")

    updateData = json.loads(updateData)
    x = json.dumps(updateData, indent=4, sort_keys=True)
    updateFlights=updateData['flights']
    
    for i in range(len(flights)):
    # for i in range (0,5):
        updateStatus = updateFlights[i]['locationAndStatus']['flightLegStatusEnglish']
        pp.pprint(updateStatus)

        if(updateStatus !=  flights[i]['locationAndStatus']['flightLegStatusEnglish']) :
            flights[i]['flightLegStatusEnglish'] = updateStatus
            print("something changed!")
            doc.write(flight[i]['row'])
            # winsound.Beep(480, 100)   
            # winsound.Beep(480, 100)   
            # winsound.Beep(480, 100)   
        else:
            pass
            # print("nothing to see in flight " +  flight[i]['flightId'])
    
    print(20*"===")

    threading.Timer(300, CheckStatus).start()
    

CheckStatus()
       
def printer(): 
        for i in range (0,1):
            print("is it still running?")
threading.Timer(1000,printer)
printer()
print("yup")

