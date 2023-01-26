"""
Steps:
    I. PRE-PROCESSING
    1. Read in input file and dropp all entries where Street_Number, or Street_Name are empty
    2. Restrict to single Province or Territory, and read in OpenAddress data for that province
    3. Make everything a string
    4. clean address columns (remove excess white space, punctuation, etc)
    II. PROCESSING
    1. For the linkage, we block on Street Number to reduce the space of matches (if CSDUID can be made available, that would help a lot)
    2. We apply a function to turn text based numbers (eg fifth) to numbers (5)
    3. We compute the string distances between full addresses and parts of addresses:
        i) cosine distance for full addr (not including street number)
        ii) cosine distance for street name
    5. We have somewhat arbitrary score cut-offs to determine matches, a planned improvement is to 
       develop a training set for a classification model
"""
import pandas as pd
import recordlinkage
from Address_Format_Funcs import AddressClean_en, Type_Drop_en,AddressClean_fr, Type_Drop_fr, number_to_text


PR='NB'
pr=PR.lower()

#path to input file
f_in='Test_Input.csv'

#dictionary to remap the original address column names (left) to standard names (right)
col_dict={
        'Street_No': 'Number',
        'Street_Name': 'Street',
        'PCode':	'Postal_Code',
        'Municipality': 'City',
        'Prov_Terr': 'Province'
        }


DF=pd.read_csv(f_in, encoding='cp1252', low_memory=False)

DF=DF.rename(columns=col_dict)


DF=DF.dropna(subset=['Number','Street'])
DF.Province=DF.Province.str.upper()
DF=DF.loc[DF.Province==PR]
N1=len(DF)
print(N1, 'records to match in ',PR)
DF['Number']=DF['Number'].astype(int).astype(str)

ADD=pd.read_csv(r"F:\Addresses\OA_Linking\OA_Standardized\\"+PR+'_OA_STD.csv',low_memory=False)

ADD['NUMBER']=ADD['NUMBER'].astype(str)
ADD=ADD.reset_index()

DF=DF.reset_index()
DF=DF.fillna('')
DF['Postal_Code']=DF['Postal_Code'].str.replace(' ','').str.upper()
indexer=recordlinkage.BlockIndex(left_on=['Number'], right_on=['NUMBER'])


M_idx = indexer.index(DF,ADD)
#print(len(M_idx))

#DF['Street_Add']=DF['StdOpAddressStreetName']+' '+DF['StdOpAddressStreetType']+ ' '+DF['StdOpAddressStreetDir']
#DF['Street_Add']=DF['Street_Add'].str.replace('  ',' ')
#DF['Street_Add']=DF['Street_Add'].str.replace('   ',' ')

if PR!='QC':
    DF=AddressClean_en(DF,'Street','Street')
    DF=Type_Drop_en(DF,'Street','Street_Name')
    ADD=Type_Drop_en(ADD,'STREET','STREET_NAME')
else:
    DF=AddressClean_fr(DF,'Street','Street')
    DF=Type_Drop_fr(DF,'Street','Street_Name')    
    ADD=Type_Drop_fr(ADD,'STREET','STREET_NAME')


ADD['STREET_NAME']=ADD['STREET_NAME'].str.strip()
DF['Street']=DF['Street'].apply(number_to_text)
#this should probably be done in the OA standardise script:
ADD['STREET']=ADD['STREET'].apply(number_to_text)

comp=recordlinkage.Compare()

#DF['street_add']=DF['StdOpAddressStreetName']
#comp.exact('CSDUID','CSDUID')
comp.string('Street','STREET', method='cosine', label='Street_Cosine' )
comp.string('City','CITY',method='levenshtein',label='City_Fuzzy')
comp.string('Postal_Code','POSTCODE',method='levenshtein',label='PCode_Fuzzy')

results=comp.compute(M_idx, DF, ADD)

results=results.reset_index()
results=results.rename(columns={'level_0':'idx1','level_1':'idx2'})
#Keep only top scoring address for each match
results=results.loc[results.groupby('idx1')['Street_Cosine'].idxmax()]
#arbitrary score cut off
results=results.loc[results.Street_Cosine>0.6]


results['Index']=list(DF.iloc[list(results.idx1)]['Index'])
results['Street_in']=list(DF.iloc[list(results.idx1)]['Street'])
results['Street_OA']=list(ADD.iloc[list(results.idx2)]['STREET'])
results['City_in']=list(DF.iloc[list(results.idx1)]['City'])
results['City_OA']=list(ADD.iloc[list(results.idx2)]['CITY'])
results['PCode_in']=list(DF.iloc[list(results.idx1)]['Postal_Code'])
results['PCode_OA']=list(ADD.iloc[list(results.idx2)]['POSTCODE'])
results['Longitude']=list(ADD.iloc[list(results.idx2)]['LON'])
results['Latitude']=list(ADD.iloc[list(results.idx2)]['LAT'])

print(len(results), 'records matched out of ', N1)
results=results.drop(['idx1','idx2'],axis=1)
results.to_csv(r'Output/MATCHED_'+PR+'.csv',index=False, encoding='cp1252')
