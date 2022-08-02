'''
compress_vancouver.py

Compresses the Vancouver dataset located in raw/ to allow it to be stored on GitHub
Store the hash to a txt file
'''

import zlib
import hashlib 
sha256 = hashlib.sha256()

# Define file paths
filename = 'BC_Vancouver_Business_Licences'
input_file = f'/home/jovyan/ODBiz/1-PreProcessing/raw/{filename}.csv'
output_dir = f'/home/jovyan/ODBiz/1-PreProcessing/raw/compress_vancouver'
hash_dir = f'{output_dir}/van_original_sha256_hash.txt'

# Read the Vancouver dataset
with open(input_file, mode = 'rb') as fp:
    data = fp.read()
    comp_fp = zlib.compress(data)

# Compress the dataset
output_filename = f'{output_dir}/{filename}.zip'
with open(output_filename, mode = 'wb') as fp:
    fp.write(comp_fp)
    print(f'Saved archive to {output_filename}')

# Record the sha256 hash of the csv for data verification
with open(input_file, mode = 'rb') as fp:
    data = fp.read()
    sha256.update(data)
van_original_sha256_hash = sha256.hexdigest()

# Save the hash to a txt file
with open(hash_dir, mode = 'w') as fp:
    fp.write(van_original_sha256_hash)
    print(f'The sha256 hash of the archive is: {van_original_sha256_hash}')
    print(f'Saved hash to {hash_dir}')