# this script applies formating to our source addresses

# The formatting functions apply three main processes to the input addresses. These are
# * removing punctuation
# * standardising directions (e.g., north &rarr; n)
# * standardising street types (e.g., street &rarr; st)

import pandas as pd
from Address_Format_Funcs import AddressClean_en, AddressClean_fr

def main():

    df = pd.read_csv('data/ODBiz_parsed.csv', low_memory=False)
#     df = df.sample(100)

    # apply formatting functions
    # test = df
    df = AddressClean_en(df,'street_name','formatted_en')
    df = AddressClean_fr(df,'street_name','formatted_fr')

    df.to_csv('data/formatted.csv',index=False)
    
if __name__ == "__main__":
    main()

