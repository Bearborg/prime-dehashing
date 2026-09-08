import sqlite3
import xml.etree.ElementTree
import json
import os

from utils.md5 import retro_md5

asset_db_path = r'F:\Documents\Code\prime-dehashing\md5\md5_resources.db'
connection = sqlite3.connect(asset_db_path)
asset_map_file = r'F:\Games\Emulation\Tools\PrimeWorldEditor\resources\gameinfo\AssetNameMap64.xml'
asset_map = xml.etree.ElementTree.parse(asset_map_file).getroot()

renames = {
    'ANCS': 'ACS',
    'ANIM': 'ANI',
    'CINF': 'CIN',
    'CRSC': 'CRSM.CRSC',
    'DPSC': 'DPSM.DPSC',
    'ELSC': 'ELSM.ELSC',
    'FONT': 'RPFF',
    'MLVL': 'MWLD',
    'PART': 'GPSM.PART',
    'SWHC': 'SWSH.SWHC',
    'WPSC': 'WPSM.WPSC',
    'SPSC': 'SPSM.SPSC'
}

resource_results = connection.execute(
    r"select hash, type, string_agg(game, ',') from asset_usages group by hash order by hash"
).fetchall()
resource_obj = dict()
pwe_names = dict()
for asset in asset_map.find('./AssetNameMap').iter("Asset"):
    asset_id = asset.find('Key').text.lower()
    val = asset.find('Value')
    name, directory, asset_type = val.find('Name').text, val.find('Directory').text, val.find('Type').text
    if asset_type in renames:
        asset_type = renames[asset_type]
    filename = f'$/{directory}{name}.{asset_type.lower()}'
    pwe_names[asset_id] = filename
for res in resource_results:
    asset_id = res[0]
    asset_type = res[1]
    if asset_id in pwe_names:
        filename = pwe_names[asset_id]
    else:
        games = set(res[2].split(','))
        games_str = ''
        if len(games) == 1:
            games_str = games.pop().replace('/NTSC', '') + '/'
        elif 'DKCR/NTSC' not in games:
            for game in ['MP3P', 'MP3/NTSC', 'MP3/PAL', 'MP3/Japan', 'TrilogyNTSC/MP3', 'TrilogyPAL/MP3','TrilogyFE/NTSC', 'TrilogyFE/PAL']:
                if game in games:
                    games_str = game.replace('/NTSC', '') + '/'
                    break
        if asset_type in renames:
            asset_type = renames[asset_type]
        filename = f'$/uncategorized/{games_str}{asset_id}.{asset_type.lower()}'
    assert filename not in resource_obj
    resource_obj[filename] = asset_id

matched_paths_for_db = [(resource_obj[path], path, int(resource_obj[path], 16) == retro_md5(path)) for path in resource_obj]

connection.executemany('INSERT INTO asset_paths VALUES(?, ?, ?) '
                       'ON CONFLICT DO UPDATE '
                       'SET path = excluded.path, path_matches = excluded.path_matches', matched_paths_for_db)
connection.commit()
connection.close()
