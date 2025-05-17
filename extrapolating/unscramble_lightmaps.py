from utils.crc32 import crc32

def unscramble_lightmaps(res_dict):
    """
    Attempts to correct instances where PWE's lightmap names are incorrectly paired by re-checking each
    incorrectly-matched filename as a new match.

    :param res_dict: A dict of integer hashes to string filenames. Non-matching filenames should be suffixed with "!!".
    :return: Number of newly-added filename matches, as an int.
    """
    print("Checking mismatched lightmap textures...")
    matched = 0
    new_dict = {}

    for key in res_dict:
        if 'lit_lightmap' in res_dict[key]:
            new_key = crc32(res_dict[key][:-2].lower())
            if new_key in res_dict and res_dict[new_key].endswith("!!"):
                new_dict[new_key] = res_dict[key]

    for key in new_dict:
        print(f'{res_dict[key]} -> {new_dict[key]}')
        res_dict[key] = new_dict[key]
        matched += 1

    return matched