import json
import urllib
import pprint
import urllib.request
import csv
import dateutil.parser
import datetime


pp=pprint.PrettyPrinter(indent=4)

with open('data2.json') as json_data:
    data = json.load(json_data)
    # pp.pprint(data)
    #print(type(data))
    # pp.pprint(data.keys())


flights = (data["flights"])
flight = flights
# pp.pprint(flights)

doc = open('ttest.csv', 'w')
columnTitleRow = "flight ID, Destination, Destination_IATA, Continent, Country, Time, Distance, Emissions, TaxCuts\n"
doc.write(columnTitleRow)




# print(flights[0]['flightLegIdentifier']['arrivalAirportIata'])

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
