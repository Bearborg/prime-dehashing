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
        '$/strings/metroid3/area_names/bryyo/10_bryyo_pirates.strg',
        '$/strings/metroid3/area_names/bryyo/0x_bryyo_generic_02.strg',
        '$/strings/metroid3/area_names/bryyo/0x_bryyo_generic_03.strg',
        '$/strings/metroid3/area_names/bryyo/0x_bryyo_generic_04.strg',
        '$/strings/metroid3/area_names/bryyo/0x_bryyo_generic_05.strg',
        '$/strings/metroid3/area_names/bryyo/0x_bryyo_generic_06.strg',
        '$/strings/metroid3/area_names/bryyo/0x_bryyo_generic_07.strg',
        '$/audio/worlds/skytown/global/skytown_wind_lp.caud',
        '$/strings/metroid3/area_names/bryyo/0a_bryyo_bridge.strg',
        '$/strings/metroid3/area_names/phaaze/04_phaaze_auroraunit2.strg',
        '$/strings/metroid3/area_names/abandoned_ship/0b_abandoned_security_a.strg',
        '$/strings/metroid3/area_names/abandoned_ship/0i_abandoned_boardingpod_a.strg',
        '$/strings/metroid3/area_names/abandoned_ship/0j_abandoned_boardingpod_b.strg',
        '$/characters/fuse_hint_scanbot/cooked/fuse_hint_scanbot_into_outofproximity.ani',
        '$/characters/fuse_hint_scanbot/cooked/fuse_hint_scanbot_intoproximity.ani',
        '$/characters/fuse_hint_scanbot/cooked/fuse_hint_scanbot_outofproximity.ani',
        '$/characters/fuse_hint_scanbot/cooked/fuse_hint_scanbot_proximity.ani',
        '$/characters/fuse_hint_scanbot/cooked/fuse_rattle_ready.ani',
        '$/strings/metroid3/sourceimages/scans/atomic.txtr'
        '$/objects/metroid_doors/gf_door/cooked/gf_door_orangeshield.cmdl',
        '$/objects/metroid_doors/seed_door/cooked/seed_door_bound.cmdl',
        '$/characters/gandrayda/cooked/gandrayda_bound.cskr',
        '$/characters/snake_weed/cooked/snake_weed_bound.cskr',
        '$/characters/space_pirate_elite/textures/space_pirate_elite_xray.txtr',
        '$/characters/dark_samus/textures/darksamus_body_c.txtr',
        '$/characters/dark_samus/textures/darksamus_reflected.txtr',
        '$/characters/eyepod/textures/eyepod_c.txtr',
        '$/characters/eyepod/textures/eyepod_c.txtr',
        '$/characters/eyepod/textures/eyepod_i.txtr',
        '$/characters/eyepod/textures/eyepod_reflected.txtr',
        '$/characters/hatcher/cooked/hatcher_bound.cskr',
        '$/worlds/gf_flagship/textures/ship_textures/temphull_3c_low.txtr',
        '$/worlds/gf_flagship/textures/ship_textures/temphull_4c_low.txtr',
        '$/worlds/gf_flagship/textures/ship_textures/temphull_5c_low.txtr',
        '$/worlds/gf_flagship/textures/ship_textures/temphull_6c_low.txtr',
        '$/worlds/gf_flagship/textures/ship_textures/temphull_7c_low.txtr',
        '$/characters/sp_fighter/cooked/sp_fighter.cmdl',
        '$/characters/sp_fighter/cooked/sp_fighter_lr.cmdl',
        '$/animatedobjects/general/pickups/visor_combat/cooked/visor_combat.cskr',
        '$/animatedobjects/general/pickups/visor_command/cooked/visor_command.cskr',
        '$/animatedobjects/general/pickups/visor_scan/cooked/visor_scan.cskr',
        '$/characters/gandrayda/textures/gandrayda_eye_c.txtr',
        '$/characters/metaree_bryyo/cooked/metaree_bryyo_bound.cskr',
        '$/characters/sprites/textures/sprites01a.txtr',
        '$/characters/sprites/textures/sprites01a.txtr',
        '$/characters/trooper_admiral/textures/trooper_admiral_c.txtr',
        '$/characters/trooper_admiral/textures/trooper_admiral_c.txtr',
        '$/characters/trooper_admiral/textures/trooper_admiral_i.txtr',
        "$/characters/trooper_female_civilian/cooked/trooper_female_civilian_bound.cskr",
        '$/characters/trooper_female_civilian/textures/trooper_female_civilian_body_c.txtr',
        '$/characters/trooper_female_civilian/textures/trooper_female_civilian_eye_c.txtr',
        '$/characters/trooper_female_civilian/textures/trooper_female_civilian_teeth_c.txtr',
        "$/characters/korakk/cooked/korakk_bound.cmdl",
    ]

    main(manual_guesses, False)