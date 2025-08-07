"""
Prints out a list of script object names for all Actors and Platforms associated with unmatched ANCS or CMDL files.
"""

import os
import yaml
import tomllib
import json
from typing import Dict

resource_file = r'./output_json/mp_resource_names.json'
config_path = r'./config.toml'

config = tomllib.load(open(config_path, 'rb'))
hecl_root = config['paths']['mp1_hecl_root']
hecl_mp1 = f'{hecl_root}/MP1'
resource_obj = json.load(open(resource_file, 'r'))
res_dict: Dict[str, str] = {resource_obj[path]: path for path in resource_obj}

obj_types = {
    0x0: 'Actor',
    0x8: 'Platform'
}

asset_names = dict()

def trim_name(obj_name: str):
    for prefix in ['Platform', 'Actor', 'AActor']:
        if obj_name.startswith(prefix):
            obj_name = obj_name[len(prefix):]
    obj_name = obj_name.lstrip(' -_')

    for suffix in ['component']:
        while obj_name.endswith(suffix):
            obj_name = obj_name[:-len(suffix)]
            obj_name = obj_name.rstrip(' -_')

    return obj_name

for root, dirs, files in os.walk(hecl_mp1):
    for file in files:
        if file == '!objects.yaml':
            abs_file = os.path.join(root, file)
            objects = yaml.load(open(abs_file, 'r', encoding='utf8').read(), Loader=yaml.CLoader)['objects']
            for obj in objects:
                if obj['type'] in obj_types:
                    name = obj['name']
                    name = trim_name(name)
                    if not name:
                        continue
                    model = obj['model'][-14:-6].lower() if obj['model'] else None
                    char: str = obj['animationParameters']['animationCharacterSet']
                    char = char[-10:-2].lower() if char else None
                    for asset in [model, char]:
                        if asset and res_dict[asset].endswith('!!'):
                            if asset in asset_names:
                                asset_names[asset].add(name)
                            else:
                                asset_names[asset] = {name}

for i, key in enumerate(asset_names):
    print(f'{i:03} {key}{os.path.splitext(res_dict[key])[1][:-2]}: {asset_names[key]}')