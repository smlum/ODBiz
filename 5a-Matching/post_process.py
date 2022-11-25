# In the matching script we removed duplicate rows before matching
# Here we want to add data from any successfully matched rows into their duplicates

# We also:
# 2. replace lat lon with x y values for matches 
# 3. remove columns created in matching that are no longer needed 

import pandas as pd
import numpy as np
import time

t1 = time.time()

df = pd.read_csv('output/matched.csv', low_memory=False)

# Add in missing matching values for previously de-duplicated rows
# Start by sorting so we only have to compare to adjacent rows
df.sort_values(['province', 'city', 'street_no', 'formatted_en'], inplace=True)
df.reset_index(inplace=True)

# df = df.head(1000)

for i in range(len(df)):
    
    # check if the street number is the same as the previous row
    if (i > 1):
        if (df.at[i , 'street_no'] == df.at[i - 1, 'street_no']):
            # then street name
            if (df.at[i, 'formatted_en'] == df.at[i - 1, 'formatted_en']):
                # then city
                if (df.at[i, 'city'] == df.at[i - 1, 'city']):
                    # then province
                    if (df.at[i, 'province'] == df.at[i - 1, 'province']):
                        # we might also want to check the source is the same
                        
                        # if they are all the same and we have an x,
                        # then assign it to the previous row
                        
                        # check if previous value had an 'x' 
                        x = df.at[i - 1, 'x']
                        if (not pd.isna(x) and x != 0):
                            # if yes, then assign it to the current row
                            df.at[i, 'x'] = x
                            
                            # do the same for y
                            y = df.at[i - 1, 'y']
                            if (not pd.isna(y) and y != 0):
                                df.at[i, 'y'] = y
                    
                            # also add info other columns from the matching stage
                            df.at[i, 'matches_r'] = df.at[i - 1, 'matches_r']
                            df.at[i, 'ratio'] = df.at[i - 1, 'ratio']
                            df.at[i, 'csdname_oda'] = df.at[i - 1, 'csdname_oda']
                            df.at[i, 'keep_match'] = df.at[i - 1, 'keep_match']


# we use two columns to decide whether to keep a match or not
# if we have no existing lat/lon AND keep_match is yes AND ratio > 92 AND , 
# then we use xy values for lat/lon
# we record this by setting geo source to oda_match

# df['new'] = np.where((df['keep_match'] == 'yes') & (df['ratio'] > 92) & (df['longitude'].isna()), df['x'], '')
df['geo_source'] = np.where((df['keep_match'] == 'yes') & (df['ratio'] > 92) & (df['latitude'].isna()), "oda_match", df['geo_source'])
df['latitude'] = np.where((df['keep_match'] == 'yes') & (df['ratio'] > 92) & (df['latitude'].isna()), df['y'], df['latitude'])
df['longitude'] = np.where((df['keep_match'] == 'yes') & (df['ratio'] > 92) & (df['longitude'].isna()), df['x'], df['longitude'])

# finally, we clean up columns that are not being used
# df = df.drop(columns=['x', 'y', 'ratio', 'matches_r'])

# df.to_csv('output/matched.csv', index=False)
df.to_csv('output/matched_processed.csv', index=False)
# we expect for x and y to be assigned to our repeats

t2 = time.time()
print('time taken: ', str(round(t2-t1, 2)), '\n')