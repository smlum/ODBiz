'''
decompress_vancouver.py

Decompresses the Vancouver dataset from the Git repo
Compares the hash of the new csv file to the hash of the original csv to ensure
that no data was lost.
'''

import zlib
import hashlib 
sha256 = hashlib.sha256()

# Define file paths
wkdir = '/home/jovyan/ODBiz/1-PreProcessing/raw/'
filename = 'BC_Vancouver_Business_Licences'
input_file = f'{wkdir}compress_vancouver/{filename}.zip'
output_dir = f'{wkdir}{filename}.csv'
hash_dir = f'{wkdir}compress_vancouver/van_original_sha256_hash.txt'

# Read the zip archive
with open(input_file, mode = 'rb') as fp:
    data = fp.read()
    decomp_fp = zlib.decompress(data)

# Extract the zip archive contents to a csv
output_filename = output_dir
with open(output_filename, mode = 'wb') as fp:
    fp.write(decomp_fp)
    print(f'Extracted to {output_filename}')

# Calculate the hash of the extracted csv
with open(output_filename, mode = 'rb') as fp:
    data = fp.read()
    sha256.update(data)
new_hash = sha256.hexdigest()

# Retrieve the hash of the original csv
with open(hash_dir) as fp:
    van_original_sha256_hash = fp.read()

# Compare the hashes to ensure it's the exact same file
if new_hash == van_original_sha256_hash:
    print('The extracted file hash matches the original hash! Extraction successful!')
    print(f'SHA256: {van_original_sha256_hash}')
else:
    print('WARNING! Hashes don\'t match! Extraction failed! :(')
    print(f'Original SHA256 hash: {van_original_sha256_hash}')
    print(f'New SHA256 hash: {new_hash}')

