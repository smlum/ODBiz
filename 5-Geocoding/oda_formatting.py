import pandas as pd
from Address_Format_Funcs import AddressClean_en, AddressClean_fr

# apply formatting to quebec\
# CHANGED apply formatting script to all provinces


provinces = ['AB', 'BC', 'MB', 'NB', 'NT', 'NS', 'ON', 'PE', 'QC', 'SK']


for province_code in provinces:
    print(province_code)
    ocd_file = "data/oda-addresses/ODA_" + province_code + "_v1.csv"
    df = pd.read_csv(ocd_file, low_memory=False)
    if (province_code == 'QC'):
        df = AddressClean_fr(df,'street','street')
    else:
        df = AddressClean_en(df,'street','street')
    output_file_name = "data/oda-addresses/ODA_" + province_code + "_v1_formatted.csv"
    df.to_csv(output_file_name, index=False)