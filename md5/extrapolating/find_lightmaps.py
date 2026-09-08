import os
from md5.extrapolating.update_if_matched import update_if_matched, MatchType

def find_lightmaps(res_dict):
    """
    Attempts to find lightmaps for MREAs.

    :param res_dict: A dict of integer hashes to string filenames. Non-matching filenames should be suffixed with "!!".
    :return: Number of newly-added filename matches, as an int.
    """
    print("Checking lightmaps...")
    matched = 0

    for key in res_dict:
        if res_dict[key][-5:].lower() in ['.mrea']:
            directory, file = os.path.split(res_dict[key])
            filename, _ = os.path.splitext(file)
            directory, cooked = os.path.split(directory)
            assert cooked == "cooked"
            directory, world = os.path.split(directory)
            for i in range(40):
                new_path = f'{directory}/{filename}/cooked/{filename}_lit_lightmap{i}.txtr'
                bloom_path = f'{directory}/{filename}/cooked/{filename}_lit_lightmap_bloom{i}.txtr'
                match_type = update_if_matched(new_path, '.txtr!!', res_dict)
                bloom_match_type = update_if_matched(bloom_path, '.txtr!!', res_dict)
                if bloom_match_type == MatchType.NewMatch:
                    matched += 1
                if match_type == MatchType.NewMatch:
                    matched += 1
                elif match_type == MatchType.Unmatched:
                    break

    return matched