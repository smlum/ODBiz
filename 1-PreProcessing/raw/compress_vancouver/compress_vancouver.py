import zlib

filename = 'BC_Vancouver_Business_Licences'
input_file = f'/home/jovyan/NewServer/ODBiz/1-PreProcessing/raw/{filename}.csv'
output_dir = f'/home/jovyan/NewServer/ODBiz/1-PreProcessing/raw/compress_vancouver'

with open(input_file, mode = 'rb') as fp:
    data = fp.read()
    comp_fp = zlib.compress(data)

output_filename = f'{output_dir}/{filename}.zip'
with open(output_filename, mode = 'wb') as fp:
    fp.write(comp_fp)
    print(f'Saved archive to {output_filename}')
