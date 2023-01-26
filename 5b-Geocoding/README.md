## Geocoding

We use the GC NAR API to find latitude and longitude coordinates from parsed street address information.

geocoding.py contains the geocoding script. If there are duplicate addresses, only one is sent to the API.

post_processing.py is needed to add geocoordinates to duplicate addresses.

The output of this step is in data/output/geocoded.csv
