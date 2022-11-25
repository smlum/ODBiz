# This finds address matches between files by looking for exact matches on street number and 'fuzzy' matches on street name
# the goal is to use Open Addresses files to assign geocoordinates

# conda install thefuzz
# conda install unidecode

import pandas as pd
import numpy as np

from thefuzz import fuzz
from thefuzz import process
import time
import sys
import unidecode #to remove accents
import re
from AddressFuncs import DirectionCheck, NameIsNumber

pd.options.mode.chained_assignment = None  # default='warn'

provinces = ['AB', 'BC', 'MB', 'NB', 'NT', 'NS', 'ON', 'PE', 'QC', 'SK']
# For testing:


#Read input files
df_all = pd.DataFrame()

df = pd.read_csv('data/formatted.csv', low_memory=False)
og_length = len(df)
print('Rows:', og_length)
print('Rows without lat/lon:', len(df[df['longitude'].isnull()]))

# Exclude rows without a parsed street addresses
df_na = df[df['street_no'].isna() | df['formatted_en'].isna() | df['province'].isna() | df['city'].isna()]
print('Rows without a parsed street address (ignored): ', len(df_na))

df = df[df['street_no'].notnull() & df['formatted_en'].notnull() & df['province'].notnull() & df['city'].notnull()]

df = df.sort_values(['latitude'])

# Exclude rows duplicated on their street address
df_dup = df[df.duplicated(subset=['street_no','formatted_en', 'province', 'city'], keep='first')]
print('Remaining rows with duplicate street addresses:', len(df_dup))

# Keep non-duplicated rows and the first of the duplicated rows
df = df[~df.duplicated(subset=['street_no','formatted_en', 'province', 'city'], keep='first')]
print('Rows left to match:', len(df[df['longitude'].isnull()]))

if (og_length - len(df) - len(df_na) - len(df_dup) != 0):
    print('Possible error in filtering/ deduplication: length of output dataframe is bigger than inputs')

df_input = df

#This is a semi-arbitrary cut off for fuzzy string matching
# Sam: we found ~93 to be the best cutoff
cut_off = 92

for province_code in provinces:
    
#     sample_size = 100
    # provinces = ['AB', 'BC', 'MB', 'QC']
    
    t1 = time.time()
    print(province_code)

    df = df_input[df_input['province'] == province_code]
    print('rows to match: ', len(df))

    # read in open adress files    
    ocd_file = "data/oda-addresses/ODA_" + province_code + "_v1_formatted.csv"
    DF = pd.read_csv(ocd_file, low_memory=False)
    
    # drop any entries without a street number
    # I think this is redundent, since this is done before the for loop
    DF = DF.dropna(subset=['street_no'])
    print('ODA addresses to match against:', len(DF))

    #force street numbers to be integers rather than strings (pandas converts to float if there are empty entries)
    DF["street_no"] = DF["street_no"].astype('int', errors='ignore').astype('str')
    df["street_no"] = pd.to_numeric(df["street_no"], errors='coerce').fillna(0).astype(np.int64)
    df["street_no"] = df["street_no"].astype('int', errors='ignore').astype('str')
    
#     sample_size = len(df)
#     FOR TESTING, use a sample
#     if (len(df) > sample_size):
#         df = df.sample(sample_size)
#     else:
#         sample_size = len(df)


    num = list(df["street_no"])
    street = []
    
    # fill street columns with formatted street names 
    if (province_code == 'QC'):
        for i in df.formatted_fr.astype('str'):
            street.append(unidecode.unidecode(i))
    else:
        for i in df.formatted_en.astype('str'):
            street.append(unidecode.unidecode(i))
    
    
    
    # create empty columns that will be added from ODA to new dataset
    n = len(num)
    MATCHES_r = [0]*n
    ratio = [0]*n
    x = [0]*n
    y = [0]*n
    csdname_oda = [0]*n
    keep_match = [0]*n
    no_match_reason = [0]*n
#     provider_oda = [0]*n
#     city_pcs_oda = [0]*n
    

    # loop through main list
    for i in range(n):
        number = num[i]
        DF_temp = DF.loc[DF["street_no"] == number]
        STREET=[]
        
        # fill STREET column with ODA street names and restrict to unique names (avoid repetitions)
        for j in DF_temp["street_formatted"].unique().astype('str'):
            STREET.append(unidecode.unidecode(j))	

        #process reduced address list with fuzzywuzzy
        addr1 = street[i]
#         print('search: ', addr1)
        if STREET==[]: #this means the street number isn't in the address list, so obviously no match
            #do nothing
            r=0
            best=''
        else:		
            bests = process.extract(addr1, STREET, scorer=fuzz.ratio)
    # 		print(bests)
            #The print statement below is to determine how much 'better' the best match is than the 2nd best
    #		if len(bests)>1:	
    #			print((bests[0])[1]-(bests[1])[1])

            #bests is a list of tuples, of the form ("street name", ratio) 
            b0 = bests[0]

            r = b0[1]
            best = b0[0]
            ratio[i] = r
            MATCHES_r[i] = best
        #This is where we determine if we found an address match
        #We consider a match if the 'best' match is significantly better than the 2nd best, AND that the best is also good (>70, semi-arbitrary cut-off).
            #assume directions match until we find they don't
            DIR_MATCH = True
            RAT_MATCH = False
            if r > cut_off:
                if r == 100: #perfect string match
                    RAT_MATCH = True
                else:
                    check_list = pd.Series([addr1,best])						
                    #check to see if direction exists and matches
                    DIR_MATCH = DirectionCheck(check_list)
                    #check to see if the street name is a number and that if so it isn't a mismatch
                    NUM_MATCH = NameIsNumber(check_list)
                    if (DIR_MATCH == True) and (NUM_MATCH == True):
                        if len(bests) > 1:
                            r1 = (bests[1])[1]
#                             print('second best: ', (bests[1])[0])
                            if (r-r1) > 10: #clearly better than 2nd option
                                RAT_MATCH = True


                            else: #not clearly better than second option
                                RAT_MATCH = False
                                no_match_reason[i] = 'close 2nd: ' + (bests[1])[0]


                        else: #Only one option, and score above cutoff
                            RAT_MATCH=True
                    else: # direction or number do not match
                        RAT_MATCH =False
                        no_match_reason[i] = 'dir or no'
                        
            else: #Best option ratio < cutoff, not good
                RAT_MATCH=False
                no_match_reason[i] = '< cutoff'


            if RAT_MATCH==True:
                    #some addresses repeat in address lists with slightly different lat/lons
                    #this is PERPLEXING. We take the mean.
                    x[i]=DF_temp.loc[DF_temp["street_formatted"]==best,"longitude"].mean()
                    y[i]=DF_temp.loc[DF_temp["street_formatted"]==best,"latitude"].mean()
                    keep_match[i] = 'yes'
                    
                    # get csd name
                    if not DF_temp.loc[DF_temp["street_formatted"]==best,"csdname"].empty:
                        csdname_oda[i] = DF_temp.loc[DF_temp["street_formatted"]==best,"csdname"].values[0]
#                     provider_oda[i] = DF_temp.loc[DF_temp["street"]==best,"provider"].values[0]
#                     city_pcs_oda[i] = DF_temp.loc[DF_temp["street"]==best,"city_pcs"].values[0]
                    else:
                        csdname_oda[i] = ''
            else:
#                     x[i]=DF_temp.loc[DF_temp["street"]==best,"longitude"].mean()
#                     y[i]=DF_temp.loc[DF_temp["street"]==best,"latitude"].mean()
                    x[i] = ''
                    y[i] = ''
                    keep_match[i] = 'no'
                    csdname_oda[i] = ''
                    
    df["matches_r"]=MATCHES_r	
    df["ratio"]=ratio
    df["x"]=x
    df["y"]=y
    df["csdname_oda"] = csdname_oda
    df["keep_match"] = keep_match
    df["no_match_reason"] = no_match_reason
    

    # create output
    sample_size = len(df)
    keep_match_yes = df[df["keep_match"] == 'yes']
    no_matches = len(keep_match_yes)
    percent_matches = (100 * no_matches / sample_size)
    print('matches (n = ', sample_size, '): ', percent_matches, '%')
    
    # generate csv for each province
    output_filename = 'output/output-' + province_code + '.csv'
    df.to_csv(output_filename, index=False)

    t2 = time.time()
    print('time taken: ', str(round(t2-t1, 2)), '\n')
    
    df_all = pd.concat([df_all, df])


df_all = pd.concat([df_all, df_na, df_dup])

print('Number of rows in output dataframe: ', len(df_all))

# df_all.to_csv("output/matched_test.csv", index=False)
df_all.to_csv("output/matched.csv", index=False)