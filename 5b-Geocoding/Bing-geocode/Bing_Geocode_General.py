#this script reads in a csv as a pandas dataframe, geocodes a column named 'address', and adds three new columns: geocoded address, lat, lon
import geocoder
import pandas as pd
import time
key='AsTU64fCN1w1cZJvCWI_n5FMqzSJUHQfjvfciEEBY5vky0MvVDRn12GZbEmmq1mz'
def geocode(query,city,province,postal):
	time.sleep(0.2) #to avoid throttling issues
#	print(query)
	#case 1: we have city + postal code	
	if postal != '' and city != '':
#		print('use postal, use city')
		g=geocoder.bing(query,key=key,method='details', countryRegion='CA',adminDistrict=province,
				locality=city,postalCode=postal)
	elif postal!='':
#		print('use postal')
		g=geocoder.bing(query,key=key,method='details', countryRegion='CA',adminDistrict=province,
				postalCode=postal)
	elif city!='':
#		print('use city')
		g=geocoder.bing(query,key=key,method='details', countryRegion='CA',adminDistrict=province,
				locality=city)
	else:
#		print('use nothin')
		g=geocoder.bing(query,key=key,method='details', countryRegion='CA',adminDistrict=province)

	if g.ok:
		
		addr_bing=g.address
		lat_bing=g.latlng[0]
		lon_bing=g.latlng[1]
		bing_city=g.city
		bing_street=g.street
		if bing_city==None:
			bing_city=''
		if bing_street==None:
			bing_street=''
		bing_prov=g.state
		bing_country=g.country
		if bing_prov==None:
			bing_prov=''
		if bing_country==None:
			bing_country=''

		print('Address Found:', addr_bing)
	else:
		
		addr_bing=''
		lat_bing=''
		lon_bing=''
		bing_city=''
		bing_street=''
		bing_prov=''
		bing_country=''
	return addr_bing,bing_street,bing_city,bing_prov,bing_country,lat_bing,lon_bing






#df['geo_address'],df['longitude'],df['latitude']= zip(*df['address'].map(geocode))

##Output file
#df.to_csv('Short_Test_Output.csv',index=False)
