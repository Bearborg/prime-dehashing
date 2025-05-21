"""
Main script, responsible for updating resource DB, outputting JSON files, and performing various automatic brute-forcing
techniques to extrapolate new matches based on currently known ones.

This script should be run whenever you're adding new matches.
"""
mock_tree_enabled = True
resource_file = r'./output_json/mp_resource_names.json'
asset_db_path = r'./database/mp_resources.db'

import json
from utils.crc32 import crc32
from typing import Dict, List
import sqlite3
try:
    import mock_tree
except ModuleNotFoundError as e:
    print(f'Mock tree error: {e}')
    print('Disabling mock tree functionality')
    mock_tree_enabled = False

from extrapolating.guess_anim_paths import guess_anim_paths
from extrapolating.guess_fonts import guess_fonts
from extrapolating.guess_buttons import guess_buttons
from extrapolating.guess_frmes import guess_frmes
from extrapolating.guess_lightmaps import guess_lightmaps
from extrapolating.guess_particles import guess_particles
from extrapolating.guess_scans_old import guess_scans_old
from extrapolating.guess_textures import guess_textures
from extrapolating.unscramble_lightmaps import unscramble_lightmaps
from extrapolating.guess_character_paths import guess_character_paths
from extrapolating.guess_scan_images import guess_scan_images
from extrapolating.guess_room_names import guess_room_names
from extrapolating.guess_adjacent_files import guess_adjacent_files

def check_manual_guesses(res_dict, guesses: List[str]):
    """
    Simple function that takes in a dictionary of hashes, then iterates through a list of manually-entered filenames and
    checks if they match any unmatched hashes from the dict. Matching hashes are overwritten in the dict.

    This is the primary way to input newly-discovered matches from the other brute-forcing scripts, since this will sync
    the results to the DB and JSON output. Can also be used to quickly test wild guesses.

    :param res_dict: A dict of integer hashes to string filenames. Non-matching filenames should be suffixed with "!!".
    :param guesses: List of string filenames to be tested against the hashes in the resource dictionary.
    :return: Number of newly-added filename matches, as an int.
    """
    print("Checking manual guesses...")
    matched = 0
    start_green = '\033[92m'
    end_color = '\033[0m'
    for path in guesses:
        key = crc32(path.lower())
        if key in res_dict and res_dict[key].endswith(path[path.rfind('.'):] + "!!"):
            print(f'{start_green}Match: {res_dict[key]} -> {path}{end_color}')
            res_dict[key] = path
            matched += 1

    return matched

def main(guesses: List[str], read_from_json = False):
    """
    Main loop. Loads hash-to-resource dictionary from the DB (or, optionally, the JSON) and validates it, then performs
    several forms of targeted brute-forcing and validates manual guesses. Finally, outputs the updated filename data to
    the DB as well as the mp_resource_names.json and mp_resource_names_confirmed.json files.

    :param guesses: List of string filenames to be tested against the hashes in the resource dictionary.
    :param read_from_json: Boolean indicating whether the mp_resource_names.json file should be used as the primary
        source of filename data, rather than the SQLite DB. Sometimes useful when making bulk edits.
    :return: None
    """
    connection = sqlite3.connect(asset_db_path)
    if read_from_json:
        resource_obj = json.load(open(resource_file, 'r'))
    else:
        resource_results = connection.execute(
            r"select path || IIF(path_matches, '', '!!') as path, hash from asset_paths order by path"
        ).fetchall()
        resource_obj = {res[0]: res[1] for res in resource_results}

    resource_dict: Dict[int, str] = {}
    total = 0
    matched = 0

    for path in resource_obj:
        total += 1
        key = int(resource_obj[path], 16)
        path = path.rstrip('!')
        if crc32(path.lower()) == key:
            matched += 1
        else:
            path += '!!'
        resource_dict[key] = path

    matched += check_manual_guesses(resource_dict, guesses)
    matched += guess_anim_paths(resource_dict)
    matched += guess_character_paths(resource_dict)
    # matched += guess_buttons(resource_dict)
    matched += guess_fonts(resource_dict)
    #matched += unscramble_lightmaps(resource_dict)
    #matched += guess_lightmaps(resource_dict)
    #matched += guess_scans_old(resource_dict, False, True)
    #matched += guess_scan_images(resource_dict, connection)
    matched += guess_frmes(resource_dict)
    # matched += guess_room_names(resource_dict)
    matched += guess_adjacent_files(resource_dict)
    matched += guess_textures(resource_dict, False)
    matched += guess_particles(resource_dict, False)
    # todo: scrape mpr cmdl names
    # todo: scrape mp2 poi names (Use RDS?)
    # todo: scrape effect/actor/platform names (Use RDS?)
    # todo: scrape evnt contents for particle names
    # todo: mp2 missing references?
    # todo: get names for mp1/2 demo anims and chars
    # todo: match TEXT_RHSsystem|TEXT_Pickups strings from MPR

    sorted_paths: List[str] = sorted(resource_dict.values(), key=str.casefold)
    printed_id_dict = {'{0:08x}'.format(x): resource_dict[x] for x in resource_dict}
    flipped_dict = {printed_id_dict[x]: x for x in printed_id_dict}
    sorted_dict = {x: flipped_dict[x] for x in sorted_paths}


    real_matched = len(list(filter(lambda x: not x.endswith('!!'), resource_dict.values())))
    if real_matched != matched:
        print("Incorrect match total")

    json.dump(sorted_dict, open(resource_file, 'w'), indent=2)
    json.dump({x: sorted_dict[x] for x in sorted_paths if not x.endswith('!!')}, open(
        r'./output_json/mp_resource_names_confirmed.json', 'w'), indent=2)

    matched_paths_for_db = [
        (sorted_dict[asset_path], asset_path.rstrip('!'), not asset_path.endswith('!!')) for asset_path in sorted_dict
    ]

    connection.executemany('INSERT INTO asset_paths VALUES(?, ?, ?) '
                           'ON CONFLICT DO UPDATE '
                           'SET path = excluded.path, path_matches = excluded.path_matches', matched_paths_for_db)
    mp1_total, mp1_matched = connection.execute(
        r"with mp1_matches as (select ap.hash, ap.path_matches from asset_paths ap "
        "inner join asset_usages us on ap.hash = us.hash "
        "group by ap.hash "
        "having SUM(us.game = 'MP1/1.00') > 0) "
        "select count(hash), sum(path_matches) from mp1_matches"
    ).fetchone()

    connection.commit()
    connection.close()

    if mock_tree_enabled:
        mock_tree.update_mock_tree(printed_id_dict)
        mock_tree.update_unmatched_txtrs(printed_id_dict)

    print()
    print(f'Overall progress: {matched}/{total} - {matched / total:.2%}')
    print(f'Prime 1 progress: {mp1_matched}/{mp1_total} - {mp1_matched / mp1_total:.2%}')

if __name__ == '__main__':
    manual_guesses = [
        "$/AnimatedObjects/RuinsWorld/scenes/chozoStatue/cooked/chozo_Statue.acs",
        "$/AnimatedObjects/RuinsWorld/scenes/chozoStatue/cooked/chozoStatue_bound.cmdl",
        "$/AnimatedObjects/RuinsWorld/scenes/chozoStatue/cooked/chozoStatue_bound_frozen.cmdl",
        "$/AnimatedObjects/RuinsWorld/scenes/chozoStatue/cooked/chozoStatue_bound.cskr",
        "$/AnimatedObjects/RuinsWorld/scenes/chozoStatue/cooked/chozoStatue_bound.cin",
    ]
    main(manual_guesses, False)