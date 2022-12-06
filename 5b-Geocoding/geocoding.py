import requests
import json
import pandas as pd
import numpy as np
import time
from os.path import exists
from datetime import datetime

# Libraries for GC API
import os
from dotenv import load_dotenv

# For testing
import mitosheet


# requires a valid key to use the GC API
# see docs https://api.canada.ca/en/homepage 
# create a .env file in this repository and add GC_API_KEY="YOUR_GC_API_KEY"
# make sure to add .env filetype to gitignore
load_dotenv()
gc_key = os.environ.get("GC_API_KEY")

# temporarily suppresses SettingWithCopyWarning
pd.options.mode.chained_assignment = None 


input_data = "../5a-Matching/output/matched_processed.csv"
df = pd.read_csv(input_data, low_memory=False, dtype="str")


# ---------------------


# Filter the data

print('Input data length: ', len(df))

# filter to those with a street number and street name
df = df[~df.street_no.isna()]
df = df[~df.formatted_en.isna()]
print('After removing those with no address data: ', len(df))

# filter those without lat/lon 
df = df[df.latitude.isna()]
print('After removing those already with lat/lon: ', len(df))

# remove duplicates 
df_dup = df[df.duplicated(subset=['street_no','formatted_en', 'province', 'city'], keep='first')]
df = df[~df.duplicated(subset=['street_no','formatted_en', 'province', 'city'], keep='first')]
print('After removing duplicates: ', len(df))

# For testing
# df = df.sample(100)



# ---------------------



# Set up our GC API call

# define parameters for osm api call
url_gc = 'https://national-address-register-statcan.api.canada.ca:443/v2/addresses/search'

# clean dataset for queries
df.fillna('', inplace=True)

# define api query string
df['gc_request_street'] = df['street_no'] + ', ' + df['formatted_en'] + ', ' + df['city'] + ', ' + df['province']

# create list of provinces in the dataset
provinces = df['province'].unique()

# For testing
# df = df.sample(100)
# provinces = ['QC']

# ---------------------



# Set a timer
t1 = time.time()

# Reset arrays for collecting our results
JSONS = []
JSONS_CITIES = []
JSONS_ALL = []

# loop through dataframe by province
for province in reversed(provinces):
    
    # Reset arrays for collecting our results
    JSONS = []
    JSONS_CITIES = []
    
    df2 = df[df['province'] == province]
    print(province)
    print('Number to geocode: ', len(df2))
    reqs_gc = list(df2['gc_request_street'])
    idxs = list(df2['idx'])

    # Loop through each request
    for i in range(len(reqs_gc)):
        query_gc = reqs_gc[i]
        
        # Set query interval
        time.sleep(1) 
        
        # Print a message every 1000 queries
        if (i % 1000 == 0):
            print(str(i), ' of ', str(len(df2)), ' queries completed')
            t2 = time.time()
            print('seconds elapsed: ', str(round(t2-t1, 2)), '\n')

        # set GC API parameters
        params_gc = {'qstr': query_gc}
        headers_gc = {'user_key': gc_key}
        
        # Send API request
        try:
            coords_gc = requests.get(url_gc, params=params_gc, headers=headers_gc)
    
            # If the API response is success
            if (coords_gc.status_code == 200):

                # Save response to a variable
                resp = coords_gc.json()

                # Delete all but the first three results
                for index in range(len(resp['data'])):
                    if (index > 2):
                        del resp['data'][3]
                        
                # Add data id's to json
                resp['idx'] = idxs[i]
                
            else:
                resp = ''
    #             print('no gc street address found')
        
        except requests.exceptions.ConnectionError:
            print("Connection refused for query: ", query_gc) 
            resp = ''
        

    
        # Append to array of results
        JSONS.append(resp)
        JSONS_ALL.append(resp)
    
    # once each province is complete, create a json file to save the results object
    json_name = 'data/geocoded_' + str(province) + '.json'
    with open(json_name, 'w', encoding='utf-8') as f:
        json.dump(JSONS, f, ensure_ascii=False, indent=4)
    print(province, " DONE")

# create a big json dump at the end
with open('data/geocoded.json', 'w', encoding='utf-8') as f:
    json.dump(JSONS_ALL, f, ensure_ascii=False, indent=4) 

t2 = time.time()
print('DONE. Seconds elapsed: ', str(round(t2-t1, 2)))