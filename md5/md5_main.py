import sqlite3
import json
from utils.md5 import retro_md5
import re
import os
import itertools
from md5.extrapolating.match_audio import match_audio
from md5.extrapolating.find_lightmaps import find_lightmaps

start_green = '\033[92m'
start_red = '\033[91m'
end_color = '\033[0m'

asset_db_path = r'F:\Documents\Code\prime-dehashing\md5\md5_resources.db'
resource_file = r'F:\Documents\Code\prime-dehashing\md5\md5_resources.json'

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
    # matched += match_audio(resource_dict, False)

    sorted_paths: list[str] = sorted(resource_dict.values(), key=lambda x: x.casefold())
    printed_id_dict = {'{0:016x}'.format(x): resource_dict[x] for x in resource_dict}
    flipped_dict = {printed_id_dict[x]: x for x in printed_id_dict}
    sorted_dict = {x: flipped_dict[x] for x in sorted_paths}

    real_matched = len(list(filter(lambda x: not x.endswith('!!'), resource_dict.values())))
    if real_matched != matched:
        print(f"Incorrect match total: {real_matched} != {matched}")

    print("Updating output files...")
    json.dump(sorted_dict, open(resource_file, 'w'), indent=2)
    matched_paths_for_db = [
        (sorted_dict[asset_path], asset_path.rstrip('!'), not asset_path.endswith('!!')) for asset_path in sorted_dict
    ]
    print("Updating resource DB...")
    connection.executemany('INSERT INTO asset_paths VALUES(?, ?, ?) '
                           'ON CONFLICT DO UPDATE '
                           'SET path = excluded.path, path_matches = excluded.path_matches', matched_paths_for_db)
    connection.commit()
    connection.close()

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
    #todo: ingest trilogy fe
    #todo: multithreaded brute forcer
    #todo: mock tree
    #todo: port sql queries
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
    match_case_variation('$/Audio/Characters/Hopper/Hopper_Vox_Alert.csmp', 0x42a98f56efaac8d7)
    manual_guesses = [
        *resource_obj_32.keys(),
        # *[f'$/strings/metroid3/lore/bryyo_lore/bryyo_{n:03}.{ext}' for n in range(13) for ext in ('strg','scan')],
        '$/audio/characters/hopper/hopper_vox_alert_1_v4.csmp',
        '$/audio/characters/hopper/hopper_vox_alert_2_v4.csmp',
        '$/audio/characters/hopper/hopper_vox_alert_3_v4.csmp',
        '$/audio/characters/hopper/hopper_vox_alert_4_v4.csmp',
        '$/audio/characters/hopper/hopper_vox_alert_5_v4.csmp',
        '$/audio/characters/hatcher/hatcher_vox_idle_3_v2.csmp',
        '$/audio/bosses/gandrayda/gandrayda_cloak_in.caud',
        '$/audio/worlds/skytown/global/skytown_wind_lp.caud',
        '$/audio/worlds/skytown/06_skytown_puzzle/skytown_06_blocker_fall.caud',
        '$/worlds/seeds/!seed_skytown_world/cooked/!04c_skytown_seed_master.mapw',
        '$/worlds/seeds/!seed_skytown_world/cooked/!04c_skytown_seed_master.mwld',
        '$/worlds/seeds/!seed_skytown_world/cooked/!04c_skytown_seed_master.savw',
        '$/worlds/seeds/!seed_skytown_world/cooked/00_seed_landingsite_skytown.egmc',
        '$/worlds/seeds/!seed_skytown_world/cooked/00_seed_landingsite_skytown.mapa',
        '$/worlds/seeds/!seed_skytown_world/cooked/00_seed_landingsite_skytown.mrea',
        '$/worlds/seeds/!seed_skytown_world/cooked/00_seed_landingsite_skytown.path',
        '$/worlds/seeds/!seed_skytown_world/cooked/00_seed_outofseed_dead_skytown.egmc',
        '$/worlds/seeds/!seed_skytown_world/cooked/00_seed_outofseed_dead_skytown.mapa',
        '$/worlds/seeds/!seed_skytown_world/cooked/00_seed_outofseed_dead_skytown.mrea',
        '$/worlds/seeds/!seed_skytown_world/cooked/00_seed_outofseed_dead_skytown.path',
        '$/worlds/seeds/!seed_skytown_world/cooked/02_seed_boss_skytown.egmc',
        '$/worlds/seeds/!seed_skytown_world/cooked/02_seed_boss_skytown.mapa',
        '$/worlds/seeds/!seed_skytown_world/cooked/02_seed_boss_skytown.mrea',
        '$/worlds/seeds/!seed_skytown_world/cooked/02_seed_boss_skytown.path',
        '$/worlds/seeds/!seed_skytown_world/cooked/0b_seed_skytown.egmc',
        '$/worlds/seeds/!seed_skytown_world/cooked/0b_seed_skytown.mapa',
        '$/worlds/seeds/!seed_skytown_world/cooked/0b_seed_skytown.mrea',
        '$/worlds/seeds/!seed_skytown_world/cooked/0b_seed_skytown.path',
        '$/worlds/seeds/!seed_skytown_world/cooked/defaultworldarea.egmc',
        '$/worlds/seeds/!seed_skytown_world/cooked/defaultworldarea.mapa',
        '$/worlds/seeds/!seed_skytown_world/cooked/defaultworldarea.mrea',
        '$/worlds/seeds/!seed_skytown_world/cooked/defaultworldarea.path',
        '$/worlds/seeds/00_seed_landingsite_skytown/cooked/00_seed_landingsite_skytown_lit_lightmap0.txtr',
        '$/worlds/seeds/00_seed_landingsite_skytown/cooked/00_seed_landingsite_skytown_lit_lightmap1.txtr',
        '$/worlds/seeds/00_seed_landingsite_skytown/cooked/00_seed_landingsite_skytown_lit_lightmap3.txtr',
        '$/worlds/seeds/00_seed_landingsite_skytown/cooked/00_seed_landingsite_skytown_lit_lightmap4.txtr',
        '$/worlds/seeds/00_seed_landingsite_skytown/cooked/00_seed_landingsite_skytown_lit_lightmap5.txtr',
        '$/worlds/seeds/00_seed_landingsite_skytown/cooked/00_seed_landingsite_skytown_lit_lightmap6.txtr',
        '$/worlds/seeds/00_seed_landingsite_skytown/cooked/00_seed_landingsite_skytown_lit_lightmap7.txtr',
        '$/worlds/seeds/00_seed_landingsite_skytown/cooked/00_seed_landingsite_skytown_lit_lightmap_bloom0.txtr',
        '$/worlds/seeds/00_seed_landingsite_skytown/cooked/00_seed_landingsite_skytown_lit_lightmap_bloom2.txtr',
        '$/worlds/seeds/00_seed_landingsite_skytown/cooked/00_seed_landingsite_skytown_lit_lightmap_bloom3.txtr',
        '$/worlds/seeds/00_seed_landingsite_skytown/cooked/00_seed_landingsite_skytown_lit_lightmap_bloom4.txtr',
        '$/worlds/seeds/00_seed_landingsite_skytown/cooked/00_seed_landingsite_skytown_lit_lightmap_bloom5.txtr',
        '$/worlds/seeds/00_seed_landingsite_skytown/cooked/00_seed_landingsite_skytown_lit_lightmap_bloom6.txtr',
        '$/worlds/seeds/00_seed_landingsite_skytown/cooked/00_seed_landingsite_skytown_lit_lightmap_bloom7.txtr',
        '$/worlds/seeds/02_seed_boss_skytown/cooked/02_seed_boss_skytown_lit_lightmap0.txtr',
        '$/worlds/seeds/02_seed_boss_skytown/cooked/02_seed_boss_skytown_lit_lightmap1.txtr',
        '$/worlds/seeds/02_seed_boss_skytown/cooked/02_seed_boss_skytown_lit_lightmap2.txtr',
        '$/worlds/seeds/02_seed_boss_skytown/cooked/02_seed_boss_skytown_lit_lightmap3.txtr',
        '$/worlds/seeds/02_seed_boss_skytown/cooked/02_seed_boss_skytown_lit_lightmap4.txtr',
        '$/worlds/seeds/02_seed_boss_skytown/cooked/02_seed_boss_skytown_lit_lightmap5.txtr',
        '$/worlds/seeds/02_seed_boss_skytown/cooked/02_seed_boss_skytown_lit_lightmap6.txtr',
        '$/worlds/seeds/02_seed_boss_skytown/cooked/02_seed_boss_skytown_lit_lightmap7.txtr',
        '$/worlds/seeds/02_seed_boss_skytown/cooked/02_seed_boss_skytown_lit_lightmap8.txtr',
        '$/worlds/seeds/02_seed_boss_skytown/cooked/02_seed_boss_skytown_lit_lightmap_bloom0.txtr',
        '$/worlds/seeds/02_seed_boss_skytown/cooked/02_seed_boss_skytown_lit_lightmap_bloom1.txtr',
        '$/worlds/seeds/02_seed_boss_skytown/cooked/02_seed_boss_skytown_lit_lightmap_bloom2.txtr',
        '$/worlds/seeds/02_seed_boss_skytown/cooked/02_seed_boss_skytown_lit_lightmap_bloom3.txtr',
        '$/worlds/seeds/02_seed_boss_skytown/cooked/02_seed_boss_skytown_lit_lightmap_bloom4.txtr',
        '$/worlds/seeds/02_seed_boss_skytown/cooked/02_seed_boss_skytown_lit_lightmap_bloom5.txtr',
        '$/worlds/seeds/02_seed_boss_skytown/cooked/02_seed_boss_skytown_lit_lightmap_bloom6.txtr',
        '$/worlds/seeds/02_seed_boss_skytown/cooked/02_seed_boss_skytown_lit_lightmap_bloom7.txtr',
        '$/worlds/seeds/02_seed_boss_skytown/cooked/02_seed_boss_skytown_lit_lightmap_bloom8.txtr',
        '$/worlds/seeds/0b_seed_skytown/cooked/0b_seed_skytown_lit_lightmap0.txtr',
        '$/worlds/seeds/0b_seed_skytown/cooked/0b_seed_skytown_lit_lightmap1.txtr',
        '$/worlds/seeds/0b_seed_skytown/cooked/0b_seed_skytown_lit_lightmap_bloom0.txtr',
        '$/worlds/seeds/0b_seed_skytown/cooked/0b_seed_skytown_lit_lightmap_bloom2.txtr',
    ]

    main(manual_guesses, False)