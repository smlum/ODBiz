import pandas as pd 
from tqdm import tqdm
import numpy as np



def main():
    # Define filepaths
    input_csv = '/home/jovyan/ODBiz/4-Parsing/output/parsed_biz.csv'
    new_df_path = '/home/jovyan/ODBiz/4-Parsing/double_check/parsed_with_spillover.csv'
    df2_path = '/home/jovyan/ODBiz/4-Parsing/double_check/parsed_with_easy_blanket_rule.csv'
    dfTO_path = '/home/jovyan/ODBiz/4-Parsing/double_check/parsed_with_spillover_toronto.csv'
    QC_parsed_wrong_df_path = '/home/jovyan/ODBiz/4-Parsing/double_check/QC_Biz_parsed_wrong.csv'
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
    # df2 = new_df.copy()

    # Set right most value as street_no, everything else is unit
    temp = new_df.loc[localfiles_idx, 'LP_street_no'].str.rsplit('-', expand = True, n = 1)
    new_df.loc[localfiles_idx, ['LP2_unit', 'LP2_street_no']] = temp.rename(columns = {0: 'LP2_unit', 1: 'LP2_street_no'})

    # # Replace dashes to avoid Excel's date conversion
    # new_df.loc[localfiles_idx, 'LP2_unit'] = new_df.loc[localfiles_idx, 'LP2_unit'].str.replace('-', '--')
    # new_df.loc[localfiles_idx, 'LP_street_no'] = new_df.loc[localfiles_idx, 'LP_street_no'].str.replace('-', '--')

    new_df.to_csv(df2_path, index = False)
    print(f'Saved new_df to {df2_path}')


    ### Apply Toronto's modified parsing rule
    localfiles = [  
                    # 'BC_Victoria_Business_Licences.csv',
                    # 'BC_Indigenous_Business_Listings.csv',
                    # 'BC_Chilliwack_Business_Licences.csv',
                    # 'ON_Brampton_Business_Directory.csv',
                    # 'QC_Etablissements.csv',
                    'ON_Toronto_Business_Licences.csv',
                    # 'Indigenous_Business_Directory.csv',
                    ]
    localfiles_idx = new_df['localfile'] == 'ON_Toronto_Business_Licences.csv'
    # dfTO = new_df[localfiles_idx].copy()

    has_comma = new_df['full_address'].str.contains(',') & localfiles_idx

    # If there's no comma, set right most value as street_no, everything else is unit
    new_df.loc[~has_comma, ['LP2_unit', 'LP2_street_no']] = new_df.loc[~has_comma, 'LP_street_no'].str.rsplit('-', expand = True, n = 1).rename(columns = {0: 'LP2_unit', 1: 'LP2_street_no'})

    # If there is a comma, apply parsing rule
    new_df.loc[has_comma, ['LP2_street_no', 'LP2_unit']] = new_df.loc[has_comma, 'full_address'].str.extract('(\d+)[A-Z\s]*,\s?(.*)').rename(columns = {0: 'LP2_street_no', 1: 'LP2_unit'})

    # # Replace dashes to avoid Excel's date conversion
    # new_df['LP2_unit'] = new_df['LP2_unit'].str.replace('-', '--')
    # new_df['LP_street_no'] = new_df['LP_street_no'].str.replace('-', '--')

    new_df.to_csv(dfTO_path, index = False)
    print(f'Saved new_df to {dfTO_path}')


    ### Identify QC entries with the most common pattern, flag them!
    QC_df = pd.read_csv(QC_parsed_wrong_df_path, dtype = str)
    common_pats = [
        "<unit>-<street_no> <street_name>",
        "<unit>-<street_no>, <street_name>",
        "<unit>-<street_no> , <street_name>"
    ]
    QC_wrong_idxs = QC_df.loc[~QC_df['pattern'].isin(common_pats), 'idx']
    new_df = new_df.set_index('idx')
    # new_df.loc[QC_wrong_idxs, ['LP2_unit', 'LP2_street_no']] = '$'
    
    df = df.set_index('idx')
    print('Updating the big parsed csv...')
    df.update(new_df)    
    df.loc[QC_wrong_idxs, ['LP2_unit', 'LP2_street_no']] = np.nan
    # # I need to commit the changes in new_df into df!
    df.to_csv(output_csv, index = True)
    print(f'Saved new_df to {output_csv}')
    print('')

if __name__ == '__main__':
    main()