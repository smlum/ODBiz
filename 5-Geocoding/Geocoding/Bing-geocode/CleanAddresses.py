import pandas as pd
import re



def AddressClean(df,name_in, name_out):
	bad_list=[r'po box\b \d+',
		r'\bbox\b \d+',
		r'\bcp\b \d+',
		r'suite\b \d+',
		r'\bsuite\b \b[a-z]\b',
		r'\boffice\b \d+',
		r'\bbureau\b \d+',
		r'\bbox\b \d+',
		r'\([^()]*\)',
 		r'tel : \d{3} \d{3} \d{4}',
		r',,',
		r', +,']
	#get rid of periods
	df[name_out]=[x.replace('.','') for x in df[name_in].astype('str')]
	#make all lower case
	df[name_out]=df[name_out].str.lower()
	#replace all hyphens with a space
	df[name_out]=df[name_out].replace('-',' ',regex=True)
	#delete everything in the bad list
	for expr in bad_list:

		df[name_out]=df[name_out].replace(expr,'',regex=True)
	
	#replace multiple spaces
	df[name_out]=df[name_out].replace(' +',' ',regex=True)
	#strip trailing and leading commas
	df[name_out]=df[name_out].str.strip(',')

	#strip trailing and leading spaces
	df[name_out]=df[name_out].str.strip()
	return df


