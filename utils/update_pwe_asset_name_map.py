import xml.etree.ElementTree as ET
import json
import os
import tomllib

config_path = r'../config.toml'
config = tomllib.load(open(config_path, 'rb'))
orig_name_map = config['paths']['pwe_asset_name_map_32']
confirmed_names = r'../output_json/mp_resource_names_confirmed.json'
out_name_map = r'../output_json/AssetNameMap32.xml'

renames = {
    'ACS': 'ANCS',
    'ANI': 'ANIM',
    'CIN': 'CINF',
    'RPFF': 'FONT',
    'MWLD': 'MLVL',
}
inverse_renames = {renames[key] : key for key in renames}

tree = ET.parse(orig_name_map)

confirmed_dict = json.load(open(confirmed_names, 'r'))
confirmed = {confirmed_dict[key] : key for key in confirmed_dict}
confirmed_lower = {key.lower() : confirmed_dict[key] for key in confirmed_dict}
handled_assets = set()
pwe_names = dict()

name_map = tree.getroot().find('AssetNameMap')

for asset in name_map:
    asset_id = asset.find('Key').text.lower()
    if asset_id in confirmed:
        path, name = os.path.split(confirmed[asset_id][2:])
        if path:
            path += '/'
        name = os.path.splitext(name)[0]
        asset.find('Value/Name').text = name
        asset.find('Value/Directory').text = path
        asset.find('Value/AutoGenName').text = 'false'
        asset.find('Value/AutoGenDir').text = 'false'
        handled_assets.add(asset_id)
    else:
        name = asset.find('Value/Name').text
        path = asset.find('Value/Directory').text
        ext = asset.find('Value/Type').text
        if ext in inverse_renames:
            ext = inverse_renames[ext]
        fullpath = f'$/{path}{name}.{ext}'.lower()
        assert fullpath not in pwe_names
        pwe_names[fullpath] = asset_id

for asset in confirmed:
    if asset not in handled_assets:
        new_asset = ET.SubElement(name_map, 'Asset')
        ET.SubElement(new_asset, 'Key', ).text = asset.upper()
        vals = ET.SubElement(new_asset, 'Value')
        path, name = os.path.split(confirmed[asset][2:])
        if path:
            path += '/'
        name, ext = os.path.splitext(name)
        ext = ext[1:].upper()

        if ext in renames:
            ext = renames[ext]
        ET.SubElement(vals, 'Name').text = name
        ET.SubElement(vals, 'Directory').text = path
        ET.SubElement(vals, 'Type').text = ext
        ET.SubElement(vals, 'AutoGenName').text = 'false'
        ET.SubElement(vals, 'AutoGenDir').text = 'false'

for path in pwe_names:
    if path in confirmed_lower and pwe_names[path] != confirmed_lower[path]:
            raise Exception(f'Duplicated path: "{path}"')

ET.indent(tree, space=" " * 4, level=0)
tree.write(out_name_map)