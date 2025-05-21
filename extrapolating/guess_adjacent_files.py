from utils.crc32 import remove_suffix
from extrapolating.update_if_matched import update_if_matched, MatchType
import os

def guess_adjacent_files(res_dict):
    """
    Attempts to match any files that are named identically to a nearby file, but with a different file extension.

    :param res_dict: A dict of integer hashes to string filenames. Non-matching filenames should be suffixed with "!!".
    :return: Number of newly-added filename matches, as an int.
    """
    print("Checking adjacent files...")
    matched = 0

    matched_files = dict()
    unmatched_files = dict()

    for key in res_dict:
        if not res_dict[key].endswith('!!'):
            filename, ext = os.path.splitext(res_dict[key])
            hash_without_ext = remove_suffix(key, ext)
            if hash_without_ext not in matched_files:
                matched_files[hash_without_ext] = filename
            elif matched_files[hash_without_ext].lower() != filename.lower():
                print(f'Collision: "{matched_files[hash_without_ext]}" != "{filename}"')
        else:
            unmatched_files[key] = res_dict[key]

    for key in unmatched_files:
        filename, ext = os.path.splitext(unmatched_files[key][:-2])
        hash_without_ext = remove_suffix(key, ext.lower())
        if hash_without_ext in matched_files:

            match_type = update_if_matched(f"{matched_files[hash_without_ext]}{ext}", ext + "!!", res_dict)
            if match_type == MatchType.NewMatch:
                matched += 1

    return matched