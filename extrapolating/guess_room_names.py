import os
from extrapolating.update_if_matched import update_if_matched, MatchType

def guess_room_names(res_dict):
    """
    Attempts to match room name STRGs by reusing the MREA filename in the appropriate string folder.

    :param res_dict: A dict of integer hashes to string filenames. Non-matching filenames should be suffixed with "!!".
    :return: Number of newly-added filename matches, as an int.
    """
    print("Checking area name strings...")
    matched = 0

    world_map = {
        'IntrolLevel': ['IntroLevel'],
        'RuinWorld': ['RuinsWorld'],
        'Overworld': ['Overworld', 'LavaWorld', 'CrashedShip'],
        'Mines': ['Crater']
    }

    for key in res_dict:
        if res_dict[key].endswith('mrea'):
            world, room = os.path.split(res_dict[key])
            world = os.path.split(os.path.split(os.path.split(world)[0])[0])[1]
            room = room[:-5]
            if world in world_map:
                world_lookup = world_map[world]
            else:
                world_lookup = [world]
            for final_world in world_lookup:
                new_path = f'$/Strings/English/Worlds/{final_world}/{room}.strg'
                match_type = update_if_matched(new_path, '.strg!!', res_dict)
                if match_type == MatchType.NewMatch:
                    matched += 1
    return matched