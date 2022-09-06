import pandas as pd
from Bing_Geocode_General import geocode
from CleanAddresses import AddressClean
#read in full dataset


df=pd.read_excel('final_output.xlsx')


df[['Address','City','Province','PostalCode']]=df[['Address','City','Province','PostalCode']].fillna('')
temp=df.loc[df['Latitude'].isna()]

#clean addresses

temp=AddressClean(temp,'Address','Address_Clean')
df['geo_address']=''
df['geo_lat']=''
df['geo_lon']=''
#print(len(temp))

#df.loc[df['latitude'].isna(),'geo_address'],df.loc[df['latitude'].isna(),'geo_lat'],df.loc[df['latitude'].isna(),'geo_lon']= zip(*temp['address_concat'].map(geocode))
df.loc[df['Latitude'].isna(),'geo_address'],df.loc[df['Latitude'].isna(),'geo_street'],df.loc[df['Latitude'].isna(),'geo_city'],df.loc[df['Latitude'].isna(),'geo_prov'],df.loc[df['Latitude'].isna(),'geo_country'],df.loc[df['Latitude'].isna(),'geo_lat'],df.loc[df['Latitude'].isna(),'geo_lon']= zip(*temp.apply(lambda row: geocode(row['Address_Clean'],row['City'],row['Province'],row['PostalCode']),axis=1))
df.to_csv('Schools_geocoded.csv',index=False)
