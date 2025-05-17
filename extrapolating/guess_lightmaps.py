import os
from extrapolating.update_if_matched import update_if_matched, MatchType

def guess_lightmaps(res_dict):
    """
    Attempts to generate lightmap texture names based on the path of the corresponding MREA.

    :param res_dict: A dict of integer hashes to string filenames. Non-matching filenames should be suffixed with "!!".
    :return: Number of newly-added filename matches, as an int.
    """
    print("Checking area lightmaps...")
    matched = 0

    for key in res_dict:
        if res_dict[key].endswith('mrea'):
            world, room = os.path.split(res_dict[key])
            world = os.path.split(os.path.split(world)[0])[0]
            room = room[:-5]
            path = f'{world}/{room}/cooked/{room}_lit_lightmap'
            for i in range(0, 46):
                new_path = f'{path}{i}.txtr'
                match_type = update_if_matched(new_path, '.txtr!!', res_dict)
                if match_type == MatchType.NewMatch:
                    matched += 1
    return matched
