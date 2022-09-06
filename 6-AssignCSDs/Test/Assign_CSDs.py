"""
this code was modified for the ODHF v2 in March 2022 from the previous ODEF project
"""
import pandas as pd
import geopandas as gpd

df=pd.read_csv("Geocoded.csv", low_memory=False, dtype='str')



# THIS BIT OF CODE IS ONLY TO FIX A MISTAKE IN A GEOCODED FILE AND SHOULD NOT BE NECESSARY IN THE FUTURE AS THE MISTAKE HAS BEEN FIXED
df['temp_long'] = df['latitude'].str.extract(',(.*)')
df['latitude'] = df['latitude'].str.replace(',(.*)', '', regex=True)
df['longitude'] = df['longitude'].fillna(df['temp_long'])
df = df.drop(columns=['temp_long'])



gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df['longitude'], df['latitude']))
gdf.crs="EPSG:4326"

#read in Statcan boundary file
CSD = gpd.read_file("../6-AssignCSDs/CSD_shapefile/lcsd000a16a_e.shx")
CSD=CSD[['CSDUID', 'CSDNAME','PRUID', 'geometry']]

#convert geometry of addresses to statcan geometry
gdf=gdf.to_crs(CSD.crs)


#perform spatial merge
gdf_csd=gpd.sjoin(gdf,CSD, predicate='within', how='left')

df=pd.DataFrame(gdf_csd)
df.to_csv('Assigned_CSDs.csv', index=False)
df.to_csv('../7-Deduplication/inputs/Assigned_CSDs.csv', index=False)
