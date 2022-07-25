import pandas as pd
import numpy as np
from tqdm import tqdm
from pytz import timezone
from datetime import datetime as dt

def main():    
    # Retrieve today's date
    ET = 'Canada/Eastern'
    start_time = dt.now(timezone(ET))
    today = str(start_time)[:10]
    inputFileDate = today
    # inputFileDate = '2022-07-04'

    # File path names
    inputFileName = f"/home/jovyan/ODBiz/3-Merging/output/1-ODBiz_merged_{inputFileDate}.csv"
    outputFileName = f"/home/jovyan/ODBiz/3-Merging/output/2-ODBiz_merged_{today}.csv"
    inv_coords_csv = f'/home/jovyan/ODBiz/3-Merging/output/invalid_coords_affected_rows_{today}.csv'

    # Load in the csv
    total_lines = 802564 
    chunksize = 10000
    df = pd.concat([chunk for chunk in tqdm(pd.read_csv(inputFileName, chunksize=chunksize, dtype = str), desc='Loading data', total=total_lines//chunksize+1)])

    # Force lat/lon to be floats
    df[["latitude", "longitude"]] = df[["latitude", "longitude"]].apply(pd.to_numeric, errors = 'coerce')
    df['valid_coord'] = False
    # df_copy = df.copy() # For debugging

    # Fix invalid longitudes
    print('Fixing invalid coordinates and marking valid ones')
    old_time = dt.now(timezone(ET))
    wrong_lons = [123.0058404, 120.8552187]
    invalid_lons = df['longitude'].isin(wrong_lons)
    df_inval_lons = df[invalid_lons]
    df.loc[invalid_lons, 'longitude'] = -df_inval_lons['longitude']
    df.loc[invalid_lons, 'valid_coord'] = True

    # Mark valid coordinates
    is_valid_coords = ((df['latitude'] > 0) & (df['longitude'] < 0)) | (df['latitude'] is np.nan)
    df.loc[is_valid_coords, 'valid_coord'] = True

    # old_time = new_time
    new_time = dt.now(timezone(ET))
    exetime = new_time - old_time
    print(f'Done in {exetime.seconds} s')

    export_idx = False

    # df = df.set_index('idx')
    # export_idx = True

    print('Forcing invalid coords to be blank')
    df_invalid_coords = df[~df['valid_coord']].copy()
    df_invalid_coords.to_csv(inv_coords_csv, index = export_idx)
    print(f'Affected rows saved to {inv_coords_csv}')

    # Force invalid coords to be blank
    df.loc[df_invalid_coords.index, ['longitude', 'latitude']] = np.nan
    old_time = new_time
    new_time = dt.now(timezone(ET))
    exetime = new_time - old_time
    print(f'Done in {exetime.seconds} s')

    # Save df to csv
    df.to_csv(outputFileName, index = export_idx)
    print(f'df saved to {outputFileName}')

if __name__ == '__main__':
    main()