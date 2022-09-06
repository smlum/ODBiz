There are three Python scripts here used to geocode the Open data (when necessary) for the proximity measures. The main one is apply_geocoder.py, which calls the other two as functions. It reads in a csv or Excel sheet as a Pandas dataframe, and uses Address, City, Postal Code, and Province information to submit to a geocoder to retrieve geocoded address information and geocoordinates. It will only geocode those entries that are already missing lat/lon information.

The CleanAddresses.py script just uses regular expressions to clean the address field of information that can make it harder for the geocoder, such as P.O. Box, Suite, Office, telephone number, etc. 

Bing_Geocode_General.py contains the function that actually submits queries to the geocoding API. It’s structured such that if city and/or postal code information exists, it will submit that information in the request alongside the full address. It uses the python geocoder package, which is essentially a library to make it easy to submit queries to a number of different geocoding APIs. It requires a Bing Maps API key to run.

This script was written by Joseph