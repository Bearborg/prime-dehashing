import sqlite3
import json
from utils.md5 import retro_md5
import re
import os
import itertools
from md5.extrapolating.match_audio import match_audio
from md5.extrapolating.find_lightmaps import find_lightmaps
from md5.extrapolating.match_scans import match_scans
from md5.extrapolating.guess_anim_paths import guess_anim_paths
from md5.extrapolating.guess_character_paths import guess_character_paths
from md5.extrapolating.guess_textures import guess_textures
from md5.extrapolating.guess_fsms import guess_fsms
mock_tree_enabled = True
try:
    import mock_tree
except ModuleNotFoundError as e:
    print(f'Mock tree error: {e}')
    print('Disabling mock tree functionality')
    mock_tree_enabled = False

start_green = '\033[92m'
start_red = '\033[91m'
end_color = '\033[0m'

asset_db_path = r'F:\Documents\Code\prime-dehashing\md5\md5_resources.db'
resource_file = r'F:\Documents\Code\prime-dehashing\md5\md5_resources.json'
resource_file_confirmed = r'F:\Documents\Code\prime-dehashing\md5\md5_resources_confirmed.json'

def check_manual_guesses(res_dict, guesses: list[str]):
    print("Checking manual guesses...")
    matched = 0
    for path in guesses:
        key = retro_md5(path)
        if key in res_dict:
            if res_dict[key].endswith("!!"):
                if res_dict[key].lower().endswith(path[path.rfind('.'):].lower() + "!!") or res_dict[key].endswith('.dgrp!!'):
                    print(f'{start_green}Match: {res_dict[key]} -> {path}{end_color}')
                    res_dict[key] = path
                    matched += 1
                else:
                    print(f'{start_red}Type mismatch: {res_dict[key]} -x> {path}{end_color}')
        # else:
        #     print(f'{start_red}No match: {path}{end_color}')

    return matched


def main(guesses: list[str], read_from_json=False):
    connection = sqlite3.connect(asset_db_path)

    if read_from_json:
        resource_obj = json.load(open(resource_file, 'r'))
    else:
        resource_results = connection.execute(
            r"select path || IIF(path_matches, '', '!!') as path, hash from asset_paths order by path"
        ).fetchall()
        resource_obj = {res[0]: res[1] for res in resource_results}
    resource_dict: dict[int, str] = {}
    total = 0
    matched = 0

    for path in resource_obj:
        total += 1
        key = int(resource_obj[path], 16)
        path = path.rstrip('!')
        if retro_md5(path) == key:
            matched += 1
        else:
            path += '!!'
        resource_dict[key] = path

    matched += check_manual_guesses(resource_dict, guesses)
    matched += find_lightmaps(resource_dict)
    matched += match_scans(resource_dict)
    # matched += match_audio(resource_dict, False)
    matched += guess_anim_paths(resource_dict)
    matched += guess_character_paths(resource_dict)
    matched += guess_textures(resource_dict)
    matched += guess_fsms(resource_dict)

    sorted_paths: list[str] = sorted(resource_dict.values(), key=lambda x: x.casefold())
    printed_id_dict = {'{0:016x}'.format(x): resource_dict[x] for x in resource_dict}
    flipped_dict = {printed_id_dict[x]: x for x in printed_id_dict}
    sorted_dict = {x: flipped_dict[x] for x in sorted_paths}
    confirmed_dict = {x: sorted_dict[x] for x in sorted_paths if not x.endswith('!!')}

    real_matched = len(list(filter(lambda x: not x.endswith('!!'), resource_dict.values())))
    if real_matched != matched:
        print(f"Incorrect match total: {real_matched} != {matched}")

    print("Updating output files...")
    json.dump(sorted_dict, open(resource_file, 'w'), indent=2)
    json.dump(confirmed_dict, open(resource_file_confirmed, 'w'), indent=2)
    matched_paths_for_db = [
        (sorted_dict[asset_path], asset_path.rstrip('!'), not asset_path.endswith('!!')) for asset_path in sorted_dict
    ]
    print("Updating resource DB...")
    connection.executemany('INSERT INTO asset_paths VALUES(?, ?, ?) '
                           'ON CONFLICT DO UPDATE '
                           'SET path = excluded.path, path_matches = excluded.path_matches', matched_paths_for_db)
    connection.commit()
    connection.close()

    if mock_tree_enabled:
        print('Updating mock tree...')
        mock_tree.update_mock_tree_64(printed_id_dict)
        mock_tree.update_unmatched_txtrs_32(printed_id_dict)

    print(f'Overall progress: {real_matched}/{total} - {real_matched / total:.2%}')

def match_case_variation(text: str, goal: int):
    for curr_case in all_case_variations(text):
        if retro_md5(curr_case) == goal:
            print(start_green + curr_case + end_color)
            return

def all_case_variations(text: str):
    uppers = []
    char_list = [c for c in text[:text.find('.')]] + [text[text.find('.'):].upper()]
    for c in range(len(char_list)):
        if char_list[c].isupper():
            uppers.append(c)
    for i in range(len(uppers) + 1):
        for combo in itertools.combinations(uppers, i):
            out_text = ''.join([c.lower() if i in combo else c for (i, c) in enumerate(char_list)])
            yield out_text


if __name__ == '__main__':
    #todo: multithreaded brute forcer
    #todo: port sql queries
    #todo: dll in config, fallback if absent
    resources32 = r'F:\Documents\Code\prime-dehashing\output_json\mp_resource_names_confirmed.json'
    resource_obj_32 = json.load(open(resources32, 'r'))

    mp3p_names = dict()
    mp3p_root = r'E:\Game Files\MP3P'
    for file in os.listdir(mp3p_root):
        abs_path = os.path.join(mp3p_root, file)
        if os.path.isfile(abs_path) and file.endswith('.contents.txt'):
            with open(abs_path, 'r') as contents:
                for line in contents:
                    res_name = re.match(r'^.*\t0x(\w+)\t.:/[^/]+/(.*)( \[.*)', line)
                    if res_name:
                        mp3p_names['$/' + res_name.group(2)] = res_name.group(1).lower()
    match_case_variation('$/Sounds/AudioGroups/HYPERMODE.agsc', 0x2d2ae281f423faed)
    manual_guesses = [
        *resource_obj_32.keys(),
        # *[f'$/strings/metroid3/lore/bryyo_lore/bryyo_{n:03}.{ext}' for n in range(13) for ext in ('strg','scan')],
        '$/strings/metroid3/scans_worlds/bryyo/13_statue_torches.strg',
        '$/strings/metroid3/scans_worlds/skytown/01_chozo head.strg',
        '$/strings/metroid3/scans_worlds/skytown/01_chozo head.scan',
        '$/strings/metroid3/scans_worlds/pirate_planet/01_vent.strg',
        '$/strings/metroid3/scans_worlds/phaaze/02_phazon_vines.strg',
        '$/strings/metroid3/scans_worlds/phaaze/02_phazon_vines.scan',
        '$/strings/metroid3/scans_worlds/abandoned_ship/05_cables.strg',
        '$/strings/metroid3/scans_worlds/abandoned_ship/05_cables.scan',
        '$/strings/metroid3/scans_worlds/seeds/00_ls_orb.strg',
        '$/characters/blink_wolves_new/cooked/b_hop_back_blinkwolves.ani',
        '$/characters/gragnol_flyer/cooked/gragnol_flyer_bound.cskr',
        '$/characters/eyepod/textures/eyepodlight_i.txtr',
        '$/characters/trooper_male_civilian/cooked/b_180_malecivilian.ani',
        '$/characters/aurora_unit/cooked/r_stunned_c_unit.ani',
        '$/characters/korba_maw/cooked/r_salivate_korbamaw.ani',
        '$/characters/aurora_unit/cooked/auroraunit_bound.cskr',
        '$/characters/korba_maw/cooked/korba_maw_bound.cskr',
        '$/characters/metaree_skytown/cooked/r_death_metaree.ani',
        '$/characters/metaree_skytown/cooked/metaree_skytown_bound.cskr',
        '$/characters/space_pirate_standard/cooked/space_pirate_korakk/r_staggered_spkorakk.ani',
        '$/objects/metroid_doors/sp_morphball_door/cooked/sp_morphball_door_bound.cskr',
        '$/objects/metroid_doors/gf_morphball_door/cooked/gf_morphball_door_bound.cskr',
        '$/characters/0e_phaaze_aazelion/cooked/b_bite_aazelion.ani',
        '$/worlds/bryyo/objects/05_missle_racks/cooked/05_missleracks_ready_up.ani',
        '$/worlds/phaaze/objects/0c_floorboss/cooked/0c_floorboss_bound.cskr',
        '$/characters/snagvines/cooked/b_relaxed_c_snagvine.ani',
        '$/cinematics/bountyhunters_meeting/cooked/rundas_shot1.ani',
        '$/cinematics/corruption_of_hunters/cooked/run_shot13.ani',
        '$/samus/samus_cinematic/cooked/cinematic/ridley_1_outro_samus/cooked/c_02_ridley1outro_samus.ani',
        '$/samus/samus_cinematic/cooked/cinematic/ridley_1_outro/cooked/c_02_ridley1outro_samus.ani',
        "$/characters/metroid/source_images/metroid_reflected.txtr",


    ]

    main(manual_guesses, False)