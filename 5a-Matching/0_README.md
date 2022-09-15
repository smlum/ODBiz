# Matching
The goal of this step is to find latitutde and longitude coordinates where they are missing from our dataset. To do so, we match our addresses against the Open Database of Addresses (ODA) dataset. 

In our original ODBiz dataset we have around 400k rows missing lat/lons. Matching reduces this number by around 200k.

## oda_download.py 
Downloads the ODA data files for each province and saves them in data/oda_addresses

## oda_formatting.py
Applies formatting to street name columns in the ODA datasets. Takes in arguments of the files to be formatted and stores all outputs in data/oda_addresses/formatted.

## address_formatting.py
Applies formatting to street names. Takes in arguments of the files to be formatted and stores all outputs in data/formatted.

## address_match.py
Takes in our source dataset and ODA datasets to match against. Outputs a csv of matched data for each province and one complete csv for the entire dataset in data/output

## post_process.py
Adds back in any data that has been removed for geocoding. 



Data removed
- a column has na (eg street no) - can just be re-added
- is a duplicate of an address - add to a new dataset, add the idx of the column kept to the column removed. then use the idx to find which lat lons to give it when you add it back in

### Formatting

Before matching, we apply some basic formatting to the street name columns in the source and ODA datasets.

The matched file from the past 

The formatting functions apply three main processes to the input addresses. These are:
* removing punctuation
* standardising directions (e.g., north &rarr; n)
* standardising street types (e.g., street &rarr; st)

There are two formatting script for English and French respectively, with the French being applied to addresses in Quebec.

Dedpuplication

Putting the data back together

