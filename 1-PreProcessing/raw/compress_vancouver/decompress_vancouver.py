import zlib
import hashlib 
sha256 = hashlib.sha256()
van_original_sha256_hash = '634bd8f6378968c610d7afa5bad7f80e17701d5d1ebc605be3e89849217a2392'

wkdir = '/home/jovyan/ODBiz/1-PreProcessing/raw/'
filename = 'BC_Vancouver_Business_Licences'
input_file = f'{wkdir}compress_vancouver/{filename}.zip'
output_dir = f'{wkdir}{filename}.csv'

with open(input_file, mode = 'rb') as fp:
    data = fp.read()
    decomp_fp = zlib.decompress(data)

output_filename = output_dir
with open(output_filename, mode = 'wb') as fp:
    fp.write(decomp_fp)
    print(f'Extracted to {output_filename}')

with open(output_filename, mode = 'rb') as fp:
    data = fp.read()
    sha256.update(data)

new_hash = sha256.hexdigest()
if new_hash == van_original_sha256_hash:
    print('The extracted file hash matches the original hash! Extraction successful!')
    print(f'SHA256: {van_original_sha256_hash}')
else:
    print('WARNING! Hashes don\'t match! Extraction failed! :(')
    print(f'Original SHA256 hash: {van_original_sha256_hash}')
    print(f'New SHA256 hash: {new_hash}')

