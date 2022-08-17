import pandas as pd 
from tqdm import tqdm
import numpy as np

def duplicate_dashes(df: pd.DataFrame):
    '''
    Replace dashes to avoid Excel's date conversion
    '''
    new_df = df.copy()

    new_df['LP2_unit'] = new_df['LP2_unit'].str.replace('-', '--')
    new_df['LP_street_no'] = new_df['LP_street_no'].str.replace('-', '--')
    
    return new_df

def simple_parse(df: pd.DataFrame, output_path: str):
    '''
    Split LP_street_no by dashes (-), set the right most value as LP2_street_no, 
    set everything else as LP2_unit
    '''

    new_df = df.copy()

    ### Apply the easiest blanket rule on the specific datasets below
    localfiles = [  'BC_Victoria_Business_Licences.csv',
                    # 'BC_Indigenous_Business_Listings.csv',
                    'BC_Chilliwack_Business_Licences.csv',
                    'ON_Brampton_Business_Directory.csv',
                    'QC_Etablissements.csv',
                    # 'ON_Toronto_Business_Licences.csv',
                    # 'Indigenous_Business_Directory.csv',
                    ]
    localfiles_idx = new_df['localfile'].isin(localfiles)

    # Set right most value as street_no, everything else is unit
    temp = new_df.loc[localfiles_idx, 'LP_street_no'].str.rsplit('-', expand = True, n = 1)
    new_df.loc[localfiles_idx, ['LP2_unit', 'LP2_street_no']] = temp.rename(columns = {0: 'LP2_unit', 1: 'LP2_street_no'})

    new_df.to_csv(output_path, index = False)
    print(f'Saved new_df to {output_path}')

    return new_df


def toronto_parse(df: pd.DataFrame, output_path: str):
    '''
    Apply a parsing rule specific to several Toronto businesses

    '''

    new_df = df.copy()

    ### Apply Toronto's modified parsing rule
    localfiles_idx = new_df['localfile'] == 'ON_Toronto_Business_Licences.csv'
    has_comma = new_df['full_address'].str.contains(',') & localfiles_idx

    # If there's no comma, set right most value as street_no, everything else is unit
    new_df.loc[~has_comma, ['LP2_unit', 'LP2_street_no']] = new_df.loc[~has_comma, 'LP_street_no'].str.rsplit('-', expand = True, n = 1).rename(columns = {0: 'LP2_unit', 1: 'LP2_street_no'})

    # If there is a comma, apply parsing rule
    new_df.loc[has_comma, ['LP2_street_no', 'LP2_unit']] = new_df.loc[has_comma, 'full_address'].str.extract(r'(\d+)[A-Z\s]*,\s?(.*)').rename(columns = {0: 'LP2_street_no', 1: 'LP2_unit'})

    new_df.to_csv(output_path, index = False)
    print(f'Saved new_df to {output_path}')

    return new_df


def flag_incorrect_QC(df: pd.DataFrame, QC_parsed_wrong_df_path: str):
    '''
    Identify incorrectly parsed entries in the QC dataset and flag them
    by setting LP2_unit and LP2_street_no as nan
    '''
    df = df.copy()

    ### Identify QC entries with the most common pattern, flag them!
    QC_df = pd.read_csv(QC_parsed_wrong_df_path, dtype = str)
    common_pats = [
        "<unit>-<street_no> <street_name>",
        "<unit>-<street_no>, <street_name>",
        "<unit>-<street_no> , <street_name>"
    ]
    QC_wrong_idxs = QC_df.loc[~QC_df['pattern'].isin(common_pats), 'idx']           
    df.loc[QC_wrong_idxs, ['LP2_unit', 'LP2_street_no']] = np.nan

    return df

def main():
    # Define filepaths
    input_csv = '/home/jovyan/ODBiz/4-Parsing/output/parsed_biz.csv'
    new_df_path = '/home/jovyan/ODBiz/4-Parsing/double_check/parsed_with_spillover.csv'
    df2_path = '/home/jovyan/ODBiz/4-Parsing/double_check/parsed_with_easy_blanket_rule.csv'
    dfTO_path = '/home/jovyan/ODBiz/4-Parsing/double_check/parsed_with_spillover_toronto.csv'
    QC_parsed_wrong_df_path = '/home/jovyan/ODBiz/4-Parsing/custom_parsing_data/QC_Biz_parsed_wrong.csv'
    postal_code_csv = '/home/jovyan/ODBiz/4-Parsing/custom_parsing_data/postal_code_err.csv'
    unparsed_addrs_path = '/home/jovyan/ODBiz/4-Parsing/custom_parsing_data/unparsed_addresses.csv'
    output_csv = '/home/jovyan/ODBiz/4-Parsing/output/2-parsed_biz.csv'
    
    # Load the csv
    total_lines = 803658
    chunksize = 10000
    df = pd.concat([chunk for chunk in tqdm(pd.read_csv(input_csv,
                                            chunksize=chunksize, 
                                            dtype=str), 
                                        desc='Loading data', 
                                        total=total_lines//chunksize+1)
                    ])
    num_of_rows = df.shape[0]
    print(f'Successfully loaded {input_csv}')
    print(f'df has {num_of_rows} rows')

    # Extract only entries that spillover their unit+street_no values
    new_df = df[~df['spill'].isna()].copy()
    new_df = new_df[['idx', 'localfile', 'business_name', 'full_address', 'LP2_unit', 'LP2_street_no', 'spill', 'LP_street_no', 'LP_street_name', 'LP_City', 'LP_Province', 'LP_PostCode', 'LP_Unit', 'LP3_unit']]
    new_df.to_csv(new_df_path, index = False)
    print(f'Saved new_df to {new_df_path}')

    # Apply a simple parsing rule
    new_df = simple_parse(new_df, df2_path)
    print('simple_parse applied')

    # Apply a parsing rule specific to Toronto businesses
    new_df = toronto_parse(new_df, dfTO_path)
    print('toronto_parse applied')

    # Update main df with changes so far
    print('Merging above changes with main df')
    new_df = new_df.set_index('idx')
    df = df.set_index('idx')
    df.update(new_df) 

    # Flag incorrectly parsed QC entries
    df = flag_incorrect_QC(df, QC_parsed_wrong_df_path)

    ### First number in sequence separated by dashes is the street_no
    st_no_1st_df = df[['LP_street_no']].copy()
    temp = st_no_1st_df['LP_street_no'].str.split('-', expand = True)
    second_col_contains_letter = temp[1].str.contains(r'\D', na = False)
    for col in tqdm(temp.columns, desc = 'Determining if 1st number in dashes sequence is the max'):
        temp[col] = pd.to_numeric(temp[col], errors = 'coerce', downcast = 'integer')
        temp[col] = np.floor(temp[col]).astype(pd.Int64Dtype())

    print('Calculating max col indicies')
    temp['max_col'] = temp.max(axis = 1).astype(pd.Int64Dtype())
    temp['first_col_max'] = (~temp[2].isna()) & (temp['max_col'] == temp[0])

    st_no_1st_df = st_no_1st_df.join(temp)
    st_no_1st_df['has_dash_and_1st_col_max'] = st_no_1st_df['LP_street_no'].str.contains('-') & st_no_1st_df['first_col_max']
    has_dash_and_1st_col_max = st_no_1st_df['has_dash_and_1st_col_max'].fillna(False) | second_col_contains_letter

    ### Create df of incorrectly parsed addresses (for entries with full_address)
    street_no_conds = [
            (df['full_address'].str.contains(r'\d')),   # full_address contains a digit
            (df['street_no'].isna()),                   # street_no is blank
            (df['LP_street_no'].isna()),                # LP_street_no is blank
            (df['LP2_street_no'].isna()),               # LP2_street_no is blank
            ]
    usa_postcode_err = df['LP_PostCode'].str.fullmatch(r'\d+', na = False)
    dashes_with_spaces = df['full_address'].str.contains(r'\s+-\s?|\s?-\s+', na = False)
    street_no_blank = True
    for i in street_no_conds:
        street_no_blank = street_no_blank & i

    idxs = street_no_blank | usa_postcode_err | dashes_with_spaces | has_dash_and_1st_col_max
    unparsed_df = df.loc[idxs].copy()
    unparsed_df['parsing_err'] = ''
    unparsed_df.loc[street_no_blank, 'parsing_err'] = unparsed_df.loc[street_no_blank, 'parsing_err'] + 'street_no_blank,'
    unparsed_df.loc[usa_postcode_err, 'parsing_err'] = unparsed_df.loc[usa_postcode_err, 'parsing_err'] + 'usa_postcode_err,'
    unparsed_df.loc[dashes_with_spaces, 'parsing_err'] = unparsed_df.loc[dashes_with_spaces, 'parsing_err'] + 'dashes_with_spaces,'
    unparsed_df.loc[has_dash_and_1st_col_max, 'parsing_err'] = unparsed_df.loc[has_dash_and_1st_col_max, 'parsing_err'] + 'has_dash_and_1st_col_max,'
    print(f'There are {unparsed_df.shape[0]} rows of incorrectly parsed addresses')


    ### Fix postal code errors
    # For these entries, LP parsed the street no as a postal code, and the unit no as a street no. 
    # This block of code maps the values to their proper column
    usa_postcode_err_df = unparsed_df.loc[usa_postcode_err].copy()
    usa_postcode_err_df['LP2_unit'] = usa_postcode_err_df['LP2_street_no']
    usa_postcode_err_df['LP2_street_no'] = usa_postcode_err_df['LP_PostCode']
    usa_postcode_err_df['LP_PostCode'] = np.nan
    print('Updating the big parsed csv with postal code error correction...')
    df.update(usa_postcode_err_df)    
    unparsed_df.update(usa_postcode_err_df)    

    usa_postcode_err_df.to_csv(postal_code_csv, index = True)
    print(f'Saved new_df to {postal_code_csv}')

    ### Drop addresses that I know are parsed from the unparsed_df
    fixed_conds = [
                unparsed_df['parsing_err'] == 'usa_postcode_err,', # Only postal codes caused the error
                unparsed_df['localfile'] == 'BC_Victoria_Business_Licences.csv', # Victoria was determined to be fully parsed 
                ]
    drop_rows = False 
    for i in fixed_conds:
        drop_rows = drop_rows | i
    drop_idxs = unparsed_df[drop_rows].index
    unparsed_df = unparsed_df.drop(index = drop_idxs)


    # unparsed_df.loc[usa_postcode_err, ['full_address', 'LP2_unit', 'LP2_street_no', 'LP_PostCode', 'parsing_err']]
    ### Unit starts with letter
    regex_groups = r'^([A-z\d\.#\/]+)\s?-\s?([A-z\d\.#\/]+)'
    re_mapping = {
                    0: 'regex_g1', 
                    1: 'regex_g2'
                    }
    temp = unparsed_df['full_address'].str.extract(regex_groups)
    unparsed_df[['regex_g1', 'regex_g2']] = temp.rename(columns = re_mapping)
    for i in re_mapping.values():
        unparsed_df[i] = unparsed_df[i].str.lower()
    unparsed_df.to_csv(unparsed_addrs_path, index = True)
    print(f'Saved unparsed_df to {unparsed_addrs_path}')
    print('')

    
    # Save the main csv
    df.to_csv(output_csv, index = True)
    print(f'Saved new_df to {output_csv}')
    # print(f'Reminder: df was not saved!')

if __name__ == '__main__':
    main()