# We may have many rows that have duplicate addresses. E.g. if two businesses are located at the same address
# or if we just have some duplicate rows.

# This step removes those duplicates
# Note we'll want to keep these duplicate entries and add them back at the end of this stage

import pandas as pd

def main():
    df = pd.read_csv('data/formatted.csv', low_memory=False)

    # Here we are aiming to remove rows which have the same street address as another row
    # We will keep them to 
    
    # First we sort by lat/lon so that we keep records of the lat/lon if they're present
    df.sort_values(['latitude'])

    # next we remove rows that are either: 
    # - duplicated across street_no, formatted street name, province or city - we keep the first
    # - OR have na for street_no, formatted street name, province or city
    df_city = df[~df.duplicated(subset=['street_no','formatted_en', 'province', 'city'], keep='first') | df['street_no'].isna() | df['formatted_en'].isna() | df['province'].isna() | df['city'].isna()]

    # here we make a dataset for all values dropped - to be added in later
    # made up of:
    # - duplicated rows EXCEPT the first instance
    # - rows with na for na for street_no, formatted street name, province or city

if __name__ == "__main__":
    main()