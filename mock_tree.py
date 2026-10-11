"""
Creates and updates folder structures that display the current progress of matching MP1's file paths, using HECL files
to display the assets themselves.
"""

import shutil
import json
import os
import re
import math
import subprocess
import sqlite3
from typing import Dict, List
try:
    import tomllib
except ModuleNotFoundError:
    raise ModuleNotFoundError("Python 3.11 or greater is required")
try:
    import yaml
    import winshell
except ModuleNotFoundError:
    raise ModuleNotFoundError(
        "Required modules are missing. Please run the following command: 'pip install pyyaml pywin32 winshell'"
    )

resource_file = r'./output_json/mp_resource_names.json'
mp1_tree_cache_file = r'./output_json/mp1_mock_tree_cache.json'
mp2_tree_cache_file = r'./output_json/mp2_mock_tree_cache.json'
mp3_tree_cache_file = r'./output_json/mp3_mock_tree_cache.json'
mp2_tag_cache_file = r'./output_json/mp2_tag_cache.json'
mp3_tag_cache_file = r'./output_json/mp3_tag_cache.json'
config_path = r'./config.toml'
asset_db_path = r'./database/mp_resources.db'
md5_asset_db_path = r'./md5/md5_resources.db'

config = tomllib.load(open(config_path, 'rb'))
mp1_mock_tree_enabled = config['features']['mp1_enable_mock_tree']
mp2_mock_tree_enabled = config['features']['mp2_enable_mock_tree']
mp3_mock_tree_enabled = config['features']['mp3_enable_mock_tree']
mp1_unmatched_txtrs_enabled = config['features']['mp1_enable_unmatched_txtrs_folder']
mp2_unmatched_txtrs_enabled = config['features']['mp2_enable_unmatched_txtrs_folder']
mp3_unmatched_txtrs_enabled = config['features']['mp3_enable_unmatched_txtrs_folder']
mp1_mock_root = config['paths']['mp1_mock_tree_root']
mp2_mock_root = config['paths']['mp2_mock_tree_root']
mp3_mock_root = config['paths']['mp3_mock_tree_root']
mp1_hecl_root = config['paths']['mp1_hecl_root']
mp2_hecl_root = config['paths']['mp2_hecl_root']
mp3_hecl_root = config['paths']['mp3_hecl_root']
mp1_unmatched_root = config['paths']['mp1_unmatched_txtrs_root']
mp2_unmatched_root = config['paths']['mp2_unmatched_txtrs_root']
mp3_unmatched_root = config['paths']['mp3_unmatched_txtrs_root']

def generate_tag_cache(
        game_id: str,
        game_hecl_root: str,
        game_tag_cache_file: str,
        game_hecl_base_dir: str,
        game_hecl_orig_spec_dir: str
    ):
    print(f"Generating tag cache for {game_id}...")
    db_path = asset_db_path if 'MP3' not in game_id else md5_asset_db_path
    resources: Dict[str, List[str]] = {}
    with sqlite3.connect(db_path) as connection:
        resource_results = connection.execute(
            "select hash, type from asset_usages au "
            f"where au.game = '{game_id}' "
            "group by hash"
        ).fetchall()
        resources = {res[0].upper(): [res[1]] for res in resource_results}
    asset_pattern = re.compile(r'.*_([A-Z0-9]{8})$') if 'MP3' not in game_id else re.compile(r'.*_([A-Z0-9]{16})$')
    for (dirpath, dirnames, filenames) in os.walk(game_hecl_base_dir):
        for filename in filenames:
            name, ext = os.path.splitext(filename)
            if match := asset_pattern.match(name):
                res_hash = match[1]
                assert res_hash in resources, f"Unrecognized resource id: {match[1]}"
                if len(resources[res_hash]) > 1:
                    currpath = os.path.split(resources[res_hash][1])[0]
                    if dirpath.endswith('LogBook'):
                        continue
                    elif currpath.endswith('LogBook'):
                        pass
                    elif dirpath.endswith('Low'):
                        continue
                    elif currpath.endswith('Low'):
                        pass
                    elif dirpath.endswith('SamGunFxMulti'):
                        continue
                    elif currpath.endswith('SamGunFxMulti'):
                        pass
                    elif dirpath.endswith('NoARAM'):
                        continue
                    elif currpath.endswith('NoARAM'):
                        pass
                    elif dirpath.endswith('Shared') and not currpath.endswith('Shared'):
                        pass
                    elif currpath.endswith('Shared'):
                        continue
                    elif dirpath.endswith('MiscData'):
                        pass
                    elif currpath.endswith('MiscData'):
                        continue
                    elif dirpath.endswith('TestAnim'):
                        pass
                    elif currpath.endswith('TestAnim'):
                        continue
                    elif ext != '.blend' and resources[res_hash][1].endswith('.blend'):
                        continue
                    elif ext == '.blend' and not resources[res_hash][1].endswith('.blend'):
                        pass
                    elif ext == '.yaml' and resources[res_hash][1].endswith('.mid'):
                        pass
                    elif ext == '.mid' and resources[res_hash][1].endswith('.yaml'):
                        continue
                    else:
                        print(f'Conflict for hash {res_hash}: "{resources[res_hash][1]}", "{os.path.join(dirpath, filename)}"')
                        continue
                else:
                    resources[res_hash].append('')
                resources[res_hash][1] = os.path.join(dirpath, filename)
        for directory in dirnames:
            if match := asset_pattern.match(directory):
                res_hash = match[1]
                assert res_hash in resources, f"Unrecognized resource id: {match[1]}"
                if len(resources[res_hash]) > 1:
                    currpath = os.path.split(resources[res_hash][1])[0]
                    if dirpath.endswith('LogBook'):
                        continue
                    elif currpath.endswith('LogBook'):
                        pass
                    elif dirpath.endswith('Shared'):
                        pass
                    elif currpath.endswith('Shared'):
                        continue
                    elif os.path.isfile(resources[res_hash][1]):
                        continue
                    else:
                        print(f'Conflict for hash {res_hash}: "{resources[res_hash][1]}", "{os.path.join(dirpath, directory)}"')
                        continue
                else:
                    resources[res_hash].append('')
                resources[res_hash][1] = os.path.join(dirpath, directory)
    for (dirpath, dirnames, filenames) in os.walk(game_hecl_orig_spec_dir):
        for filename in filenames:
            name, ext = os.path.splitext(filename)
            if match := asset_pattern.match(name):
                res_hash = match[1]
                assert res_hash in resources, f"Unrecognized resource id: {match[1]}"
                if len(resources[res_hash]) > 1:
                    if not re.search(r'MP\d-ORIG', resources[res_hash][1]):
                        continue
                    currpath = os.path.split(resources[res_hash][1])[0]
                    if dirpath.endswith('Low'):
                        continue
                    elif currpath.endswith('Low'):
                        pass
                    elif dirpath.endswith('LogBook'):
                        continue
                    elif currpath.endswith('LogBook'):
                        pass
                    elif dirpath.endswith('NoARAM'):
                        continue
                    elif currpath.endswith('NoARAM'):
                        pass
                    elif dirpath.endswith('Shared'):
                        pass
                    elif currpath.endswith('Shared'):
                        continue
                    else:
                        print(f'Conflict for hash {res_hash}: "{resources[res_hash][1]}", "{os.path.join(dirpath, filename)}"')
                        continue
                else:
                    resources[res_hash].append('')
                resources[res_hash][1] = os.path.join(dirpath, filename)
    for res in resources:
        if len(resources[res]) > 1:
            resources[res][1] = os.path.relpath(resources[res][1], game_hecl_root).replace('\\', '/')
        else:
            assert res == 'FFEA999CB52E4185' # weird RAUD file that's not actually present
            resources.pop(res)
    json.dump(resources, open(game_tag_cache_file, 'w'), indent='  ')

if mp1_mock_tree_enabled or mp1_unmatched_txtrs_enabled:
    if os.path.exists(mp1_hecl_root):
        tag_cache_file = os.path.join(mp1_hecl_root, r'.hecl/cooked/MP1.spec/tag_cache.yaml')
        tag_cache_text = open(tag_cache_file, 'r', encoding='utf8').read()
        # pyyaml doesn't always parse asset ids correctly, so we have to escape them with single quotes before parsing
        escaped_tag_cache_text = re.sub(r'^([A-Z0-9]{8})', r"'\1'", tag_cache_text, flags=re.MULTILINE)
        mp1_tag_cache = yaml.load(escaped_tag_cache_text, Loader=yaml.CLoader)
    else:
        print(f'HECL root folder "{mp1_hecl_root}" does not exist, please choose an existing folder.')
        mp1_mock_tree_enabled = False
        mp1_unmatched_txtrs_enabled = False

if mp2_mock_tree_enabled or mp2_unmatched_txtrs_enabled:
    if mp2_mock_tree_enabled:
        if os.path.exists(mp2_hecl_root):
            if not os.path.exists(mp2_tag_cache_file):
                generate_tag_cache(
                    'MP2/NTSC',
                    mp2_hecl_root,
                    mp2_tag_cache_file,
                    os.path.join(mp2_hecl_root, r'MP2'),
                    os.path.join(mp2_hecl_root, r'.hecl\cooked\MP2-ORIG.spec\MP2')
                )
            mp2_tag_cache = json.load(open(mp2_tag_cache_file, 'r'))
        else:
            print(f'HECL root folder "{mp2_hecl_root}" does not exist, please choose an existing folder.')
            mp2_mock_tree_enabled = False
            mp2_unmatched_txtrs_enabled = False
            
if mp3_mock_tree_enabled or mp3_unmatched_txtrs_enabled:
    if mp3_mock_tree_enabled:
        if os.path.exists(mp3_hecl_root):
            if not os.path.exists(mp3_tag_cache_file):
                generate_tag_cache(
                    'MP3/NTSC',
                    mp3_hecl_root,
                    mp3_tag_cache_file,
                    os.path.join(mp3_hecl_root, r'MP3'),
                    os.path.join(mp3_hecl_root, r'.hecl\cooked\MP3-ORIG.spec\MP3')
                )
            mp3_tag_cache = json.load(open(mp3_tag_cache_file, 'r'))
        else:
            print(f'HECL root folder "{mp3_hecl_root}" does not exist, please choose an existing folder.')
            mp3_mock_tree_enabled = False
            mp3_unmatched_txtrs_enabled = False


def create_junction(link_name, target_path):
    """
    Creates a junction (i.e. a shortcut to a folder).
    :param link_name: Path of the junction itself, a .lnk file.
    :param target_path: Path of the folder that the junction leads to.
    :return: None
    """
    if os.path.exists(link_name):
        os.remove(link_name)
    subprocess.run(['mklink', '/J', link_name, target_path], shell=True, stdout=subprocess.DEVNULL)

def update_mock_tree_32(resource_dict):
    """
    Updates (or creates) a set of folders in the same structure of Retro's asset tree. Assets are displayed as shortcuts
    to HECL files. Folder location and HECL root directory must be set in 'config.toml'.
    :param resource_dict: A dict of string hashes to string filenames. Unmatched filenames should be suffixed with "!!".
    :return: None
    """
    if not (mp1_mock_tree_enabled or mp2_mock_tree_enabled):
        print("Mock tree disabled, skipping")
        return
    if mp1_mock_tree_enabled:
        update_game_mock_tree(resource_dict, mp1_hecl_root, mp1_mock_root, mp1_unmatched_root, mp1_tree_cache_file, mp1_tag_cache)
    if mp2_mock_tree_enabled:
        update_game_mock_tree(resource_dict, mp2_hecl_root, mp2_mock_root, mp2_unmatched_root, mp2_tree_cache_file, mp2_tag_cache)

def update_mock_tree_64(resource_dict):
    """
    Updates (or creates) a set of folders in the same structure of Retro's asset tree. Assets are displayed as shortcuts
    to HECL files. Folder location and HECL root directory must be set in 'config.toml'.
    :param resource_dict: A dict of string hashes to string filenames. Unmatched filenames should be suffixed with "!!".
    :return: None
    """
    if not mp3_mock_tree_enabled:
        print("Mock tree disabled, skipping")
        return
    if mp3_mock_tree_enabled:
        update_game_mock_tree(resource_dict, mp3_hecl_root, mp3_mock_root, mp3_unmatched_root, mp3_tree_cache_file, mp3_tag_cache)

def update_game_mock_tree(resource_dict, hecl_root, mock_root, unmatched_root, tree_cache_file, tag_cache):
    if not os.path.isdir(mock_root):
        print(f'Mock tree root "{mock_root}" does not exist, please choose an existing folder')
        return

    is_first_run = False
    if os.path.isfile(tree_cache_file):
        tree_cache = json.load(open(tree_cache_file, 'r', encoding='utf8'))
    else:
        tree_cache = dict()
        is_first_run = True

    if is_first_run:
        print("Performing first-time creation of mock tree...")
    sync_directory(hecl_root, mock_root, unmatched_root, resource_dict, tag_cache, tree_cache, is_first_run)

    with open(tree_cache_file, 'w', encoding='utf8') as out_file:
        out_file.write(json.dumps(tree_cache, indent=2))

def sync_directory(hecl_root, mock_root, unmatched_root, resource_dict, tag_cache, tree_cache, is_first_run):
    for index, line in enumerate(tag_cache):
        if is_first_run and index % (len(tag_cache) // 20) == 0:
            print(f'Creating mock tree: {math.ceil(index / len(tag_cache) * 100)}%')
        asset = str(line).lower()
        hecl_path = tag_cache[line][1]
        if '*' in hecl_path:
            hecl_path = hecl_path[:hecl_path.find('*')] + 'blend'
        if asset in resource_dict and not resource_dict[asset].endswith('!!'):
            abs_hecl_path = os.path.join(hecl_root, hecl_path)
            abs_shortcut_path = os.path.join(mock_root, resource_dict[asset][2:] + '.lnk')

            if asset in tree_cache:
                cached_tree_path, cached_dest_path = tree_cache[asset]
                if cached_tree_path == abs_shortcut_path and cached_dest_path == abs_hecl_path:
                    continue
                else:
                    print(f'{cached_tree_path} != {abs_shortcut_path} or {cached_dest_path} != {abs_hecl_path}')

            assert os.path.exists(abs_hecl_path), f'Missing HECL resource for {asset}, path "{abs_hecl_path}"'

            if not is_first_run:
                print(f'Updated mock tree: {asset} - "{hecl_path}" => "{abs_shortcut_path[:-4]}"')
            tree_cache[asset] = [abs_shortcut_path, abs_hecl_path]

            os.makedirs(os.path.split(abs_shortcut_path)[0], exist_ok=True)
            if '.' in abs_hecl_path:
                with winshell.shortcut(abs_shortcut_path) as shortcut:
                    shortcut.path = abs_hecl_path
                if abs_shortcut_path[:-4].upper().endswith('TXTR'):
                    hecl_folder = hecl_path.split('/')[1]
                    unmatched_path = f'{unmatched_root}/{hecl_folder}/{asset}.png'
                    if os.path.isfile(unmatched_path):
                        os.remove(unmatched_path)
            else:
                create_junction(abs_shortcut_path[:-4], abs_hecl_path)

def update_unmatched_txtrs_32(resource_dict):
    """
    Updates (or creates) a folder containing PNG copies of unmatched TXTR files, organized by originating PAK.
    Folder location and HECL root directory must be set in 'config.toml'.
    :param resource_dict: A dict of string hashes to string filenames. Unmatched filenames should be suffixed with "!!".
    :return: None
    """
    if not (mp1_unmatched_txtrs_enabled or mp2_unmatched_txtrs_enabled):
        print("Unmatched TXTR folder disabled, skipping")
        return
    if mp1_unmatched_txtrs_enabled:
        if not os.path.isdir(mp1_unmatched_root):
            print(f'Unmatched TXTR root "{mp1_unmatched_root}" does not exist, please choose an existing folder')
            return
        else:
            update_txtr_folder('MP1/1.00', mp1_unmatched_root, mp1_hecl_root, mp1_tag_cache, resource_dict)

    if mp2_unmatched_txtrs_enabled:
        if not os.path.isdir(mp2_unmatched_root):
            print(f'Unmatched TXTR root "{mp2_unmatched_root}" does not exist, please choose an existing folder')
            return
        else:
            update_txtr_folder('MP2/NTSC', mp2_unmatched_root, mp2_hecl_root, mp2_tag_cache, resource_dict)

def update_unmatched_txtrs_64(resource_dict):
    """
    Updates (or creates) a folder containing PNG copies of unmatched TXTR files, organized by originating PAK.
    Folder location and HECL root directory must be set in 'config.toml'.
    :param resource_dict: A dict of string hashes to string filenames. Unmatched filenames should be suffixed with "!!".
    :return: None
    """
    if not mp3_unmatched_txtrs_enabled:
        print("Unmatched TXTR folder disabled, skipping")
        return
    if mp3_unmatched_txtrs_enabled:
        if not os.path.isdir(mp3_unmatched_root):
            print(f'Unmatched TXTR root "{mp3_unmatched_root}" does not exist, please choose an existing folder')
            return
        else:
            update_txtr_folder('MP3/NTSC', mp3_unmatched_root, mp3_hecl_root, mp3_tag_cache, resource_dict)

def update_txtr_folder(game_id: str, game_root: str, hecl_root: str, tag_cache, resource_dict):
    is_first_run = game_id == len(os.listdir(game_root)) == 0
    if is_first_run:
        print("Performing first-time creation of unmatched TXTR folder...")
        connection = sqlite3.connect(asset_db_path)
        resource_results = connection.execute(
            "select path, ap.hash from asset_paths ap "
            "inner join asset_usages au on au.hash = ap.hash "
            "where au.game = ? AND ap.path_matches = 0 "
            "and au.type = 'TXTR' "
            "order by path", (game_id,)
        ).fetchall()
        txtr_dict = {res[1].upper(): res[0] for res in resource_results}
        for index, asset in enumerate(txtr_dict):
            hecl_path = tag_cache[asset][1]
            abs_hecl_path = os.path.join(hecl_root, hecl_path)
            assert os.path.exists(abs_hecl_path), f'Missing HECL resource for {asset}, path "{abs_hecl_path}"'
            hecl_folder = hecl_path.split('/')[1]
            out_path = f'{game_root}/{hecl_folder}/{asset}.png'
            if index % (len(txtr_dict.keys()) // 20) == 0:
                print(f'Creating unmatched TXTR folder for {game_id}: {math.ceil(index / len(txtr_dict.keys()) * 100)}%')
            os.makedirs(os.path.split(out_path)[0], exist_ok=True)
            shutil.copyfile(abs_hecl_path, out_path)
    else:
        for line in tag_cache:
            asset = str(line).lower()
            hecl_path = tag_cache[line][1]
            if asset in resource_dict and not resource_dict[asset].endswith('!!'):
                if resource_dict[asset].upper().endswith('TXTR'):
                    hecl_folder = hecl_path.split('/')[1]
                    unmatched_path = f'{game_root}/{hecl_folder}/{asset}.png'
                    if os.path.isfile(unmatched_path):
                        os.remove(unmatched_path)

if __name__ == '__main__':
    resource_obj = json.load(open(resource_file, 'r'))
    res_dict: Dict[str, str] = {resource_obj[path]: path for path in resource_obj}
    update_mock_tree_32(res_dict)