import pandas as pd
import recordlinkage

# This script deduplicates our data using the record linkage toolkit

'''
Steps:
    (1) Formatting
            Read in input file and dropp all entries where Street_Number, or Street_Name are empty
            Restrict to single Province or Territory, and read in OpenAddress data for that province
            Make everything a string
            Clean address columns (remove excess white space, punctuation, etc)
    (2) Identify duplicates
            
    (3) Scrap duplicates

'''

df = pd.read_csv('~/ODBiz/5a-Matching/output/matched.csv', low_memory=False)


# Create an indexer
indexer = recordlinkage.Index()

# Block on 'business_name', 'province', 'city', 'licence_number'
indexer.block('business_name')
indexer.block('province')
indexer.block('city')
indexer.block('licence_number')

# Create a candidate index
candidate_index = indexer.index(df)

# Create a comparison object
compare_cl = recordlinkage.Compare()

# Compare 'business_name', 'province', 'city', 'licence_number'
compare_cl.string('business_name', 'business_name', method='jarowinkler', threshold=0.85)
compare_cl.exact('province', 'province')
compare_cl.exact('city', 'city')
compare_cl.exact('licence_number', 'licence_number')

# Get a comparison vector
compare_vectors = compare_cl.compute(candidate_index, df)

# Get a list of duplicate indexes
duplicate_indexes = compare_vectors[compare_vectors.sum(axis=1) > 3].index

# Subset the dataframe to the duplicate rows
df_duplicates = df.loc[duplicate_indexes]

df_duplicates.to_csv('duplicates.csv', index=False)