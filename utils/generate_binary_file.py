import json
import struct
from typing import Dict

def generate_binary_file(res_dict: Dict[int, str], output_path: str):
    """
    Produces a simple binary file containing all confirmed matches; used for importing matched filenames to Metaforce.
    :param res_dict: A dict of integer hashes to string filenames. Non-matching filenames should be suffixed with "!!".
    :param output_path: Desination filename for the binary file.
    :return:
    """
    with open(output_path, 'wb') as output_file:
        output_file.write(struct.pack('I', len(res_dict)))
        for key, val in res_dict.items():
            output_file.write(struct.pack('I', key))
            output_file.write(val.encode() + b'\00')


if __name__ == '__main__':
    resource_file = r'../output_json/mp_resource_names_confirmed.json'
    output_filename = r'../output_json/mp_resource_names_confirmed.bin'
    resource_obj = json.load(open(resource_file, 'r'))
    resource_dict: Dict[int, str] = {int(resource_obj[path], 16): path for path in resource_obj}
    generate_binary_file(resource_dict, output_filename)