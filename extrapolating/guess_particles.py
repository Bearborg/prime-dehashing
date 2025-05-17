import os
from typing import Set
from extrapolating.update_if_matched import update_if_matched, MatchType


def guess_particles(res_dict, deep_search: bool = False):
    """
    Attempts to match several types of particle effect files by testing if known particle filenames were reused in other
    particle effect folders. Optionally, the deep_search parameter will attempt fuzzy matching by adding/removing digits
    and other common suffixes (this is disabled by default, as it can be very slow and generates many false positives).

    Due to a high rate of false positives, this function does not automatically add matches to the DB, and treats them
    only as potentially correct.

    :param res_dict: A dict of integer hashes to string filenames. Non-matching filenames should be suffixed with "!!".
    :param deep_search: A boolean determining whether to use computationally costlier matching techniques.
    :return: Number of newly-added filename matches, as an int.
    """
    print("Checking particles...")
    matched = 0

    part_folders: Set[str] = set()
    part_folders.update([
        '$/Effects/particles/ruins/Group01/A',
        '$/Effects/particles/ruins/Group02/A',
        '$/Effects/particles/ruins/Group02/B',
        '$/Effects/particles/mines',
        '$/Effects/particles/lava',
        '$/Effects/particles/crater',
        '$/Effects/particles/introunderwater',
        '$/Effects/particles/intro_underwater',
        '$/Effects/particles/introunder',
        '$/Effects/particles/intro_under',
        '$/Effects/particles/characters/Bloodflower',
        '$/Effects/particles/characters/Blood_Flower',
        '$/Effects/particles/characters/Burrower',
        '$/Effects/particles/characters/Burrowers',
        '$/Effects/particles/enemy_weapons/Burrower',
        '$/Effects/particles/enemy_weapons/Burrowers',
        '$/Effects/particles/enemy_weapons/Sheegoth',
        '$/Effects/particles/enemy_weapons/Sheegoths',
        '$/Effects/particles/characters/garganBeetleBeta',
        '$/Effects/particles/characters/garganBeetle_Beta',
        '$/Effects/particles/characters/FireFlea',
        '$/Effects/particles/characters/FireFlee',
        '$/Effects/particles/characters/Fire_Flea',
        '$/Effects/particles/characters/Fire_Flee',
        '$/Effects/particles/characters/Flickerbat',
        '$/Effects/particles/characters/Flicker_bat',
        '$/Effects/particles/characters/Geemer',
        '$/Effects/particles/characters/Lumigek',
        '$/Effects/particles/bosses/MetroidPrime',
        '$/Effects/particles/bosses/Metroid_Prime',
        '$/Effects/particles/characters/PuddleToad',
        '$/Effects/particles/characters/Puddle_Toad',
        '$/Effects/particles/characters/PuddleToadGamma',
        '$/Effects/particles/characters/Puddle_Toad_Gamma',
        '$/Effects/particles/characters/Puffer',
        '$/Effects/particles/characters/Ripper',
        '$/Effects/particles/characters/Scarab',
        '$/Effects/particles/characters/Scarabs',
        '$/Effects/particles/characters/Seedling',
        '$/Effects/particles/characters/Seedlings',
        '$/Effects/particles/enemy_weapons/Seedling',
        '$/Effects/particles/enemy_weapons/Seedlings',
        '$/Effects/particles/characters/Sova',
        '$/Effects/particles/bosses/Thardus',
        '$/Effects/particles/characters/Tryclops',
        '$/Effects/particles/characters/Triclops',
        '$/Effects/particles/characters/WarWasp',
        '$/Effects/particles/characters/WarWasps',
        '$/Effects/particles/characters/War_Wasp',
        '$/Effects/particles/characters/War_Wasps',
        '$/Effects/particles/characters/Wasp',
        '$/Effects/particles/characters/Wasps',
        '$/Effects/particles/characters/Zoomer',
        '$/Effects/particles/sam_weapon/beam/power',
        '$/Effects/particles/sam_weapon/beam/power/elem',
        '$/Effects/particles/sam_weapon/beam/plasma',
        '$/Effects/particles/sam_weapon/beam/plasma/elem',
        '$/Effects/particles/sam_weapon/beam/plasma/2ndaryfx',
        '$/Effects/particles/sam_weapon/beam/wave',
        '$/Effects/particles/sam_weapon/beam/wave/elem',
        '$/Effects/particles/sam_weapon/beam/wave/2ndaryfx',
        '$/Effects/particles/sam_weapon/beam/ice/2ndaryfx',
        '$/Effects/particles/sam_weapon/icecombo',
    ])
    part_names: Set[str] = set()
    part_names.update([
        'pollen'
        'pollen1'
    ])
    alpha_num = set()
    alpha_num.update(['a', 'b', 'c', 'd'])
    for i in range(10):
        for x in ['', 'a', 'b', 'c', 'd']:
            alpha_num.add(f'{i}{x}')
            alpha_num.add(f'0{i}{x}')

    for key in res_dict:
        if res_dict[key][-4:] in ['part', 'swhc', 'elsc', 'wpsc', 'crsc', 'dpsc']:
            part_folder, part_name = os.path.split(res_dict[key])
            part_folders.add(part_folder)
            part_names.add(part_name)
            part_names.add(part_name[:-10] + '.crsm.crsc')
            part_names.add(part_name[:-10] + '.wpsm.wpsc')
            if deep_search:
                if part_name[-11].isdigit():
                    part_names.update([part_name[:-11] + n + part_name[-10:] for n in alpha_num])
                    part_names.add(part_name[:-11] + part_name[-10:])
                else:
                    part_names.update([part_name[:-10] + n + part_name[-10:] for n in alpha_num])

    for folder in part_folders:
        for part in part_names:
            commit = False #r'/RuinWorld/' in folder
            match_type = update_if_matched(f'{folder}/{part}', part[-5:] + "!!", res_dict, commit)
            if match_type == MatchType.NewMatch and commit:
                matched += 1

    return matched
