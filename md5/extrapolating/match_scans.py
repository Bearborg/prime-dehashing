import os
import re
from md5.extrapolating.update_if_matched import update_if_matched, MatchType

def match_scans(res_dict):
    """
    Attempts to match SCAN/STRG files with their respective folders.

    :param res_dict: A dict of integer hashes to string filenames. Non-matching filenames should be suffixed with "!!".
    :return: Number of newly-added filename matches, as an int.
    """
    print("Checking scan files...")
    matched = 0

    scan_dirs: set = {
        '$/strings/metroid3/creatures',
        '$/strings/metroid3/dialogue',
        '$/strings/metroid3/game_mechanics',
        '$/strings/metroid3/inventory',
        '$/strings/metroid3/lore',
        '$/strings/metroid3/scans_worlds/gf_planet'
        '$/strings/metroid3/scans_worlds/gf_ship'
        '$/strings/metroid3/scans_worlds/gf_flagship'
        '$/strings/metroid3/scans_worlds/bryyo'
        '$/strings/metroid3/scans_worlds/skytown'
        '$/strings/metroid3/scans_worlds/sp_planet'
        '$/strings/metroid3/scans_worlds/pirate'
        '$/strings/metroid3/scans_worlds/seeds'
        '$/strings/metroid3/scans_worlds/phaaze'
        '$/strings/metroid3/tutorials'
    }

    for key in res_dict:
        if res_dict[key][-7:].lower() in ['.scan!!']:
            names: list[str] = [os.path.split(res_dict[key])[1][:-2]]
            if names[0].startswith('scan_'):
                names[0] = names[0][5:]
            names.append(names[0].replace('_', ' '))
            names.extend([n.replace('.scan', '.strg') for n in names])
            for name in names:
                for scan_dir in scan_dirs:
                    new_path = f'{scan_dir}/{name}'
                    match_type = update_if_matched(new_path, os.path.splitext(new_path)[1] + '!!', res_dict)
                    if match_type == MatchType.NewMatch:
                        matched += 1
                        break
        elif res_dict[key][-5:].lower() in ['.scan']:
            new_path = res_dict[key][:-5] + '.strg'
            match_type = update_if_matched(new_path, '.strg!!', res_dict)
            if match_type == MatchType.NewMatch:
                matched += 1

    return matched