import string

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
        filename, ext = os.path.splitext(res_dict[key])
        if len(os.path.splitext(filename)[1]) == 5:
            filename, ext2 = os.path.splitext(filename)
            ext = ext2 + ext
        if not res_dict[key].endswith('!!'):
            hash_without_ext = remove_suffix(key, ext)
            if hash_without_ext not in matched_files:
                matched_files[hash_without_ext] = filename
            elif matched_files[hash_without_ext].lower() != filename.lower():
                print(f'Collision: "{matched_files[hash_without_ext]}" != "{filename}"')
            while filename[-1] in string.digits:
                hash_without_ext = remove_suffix(hash_without_ext, filename[-1])
                filename = filename[:-1]
                if hash_without_ext not in matched_files:
                    matched_files[hash_without_ext] = filename
        else:
            unmatched_files[key] = res_dict[key]
            # for num in string.digits:
            #     unnumbered = remove_suffix(key, num + ext)
            #     if unnumbered not in unmatched_files:
            #         unmatched_files[unnumbered] = filename + num + ext
            #     else:
            #         print(hex(key), res_dict[key], unmatched_files[unnumbered])

    for key in unmatched_files:
        filename, ext = os.path.splitext(unmatched_files[key][:-2])
        if len(os.path.splitext(filename)[1]) == 5:
            filename, ext2 = os.path.splitext(filename)
            ext = ext2 + ext
        for num in [''] + [*'0123456789']:
            hash_without_ext = remove_suffix(key, num + ext.lower())
            if hash_without_ext in matched_files:

                match_type = update_if_matched(f"{matched_files[hash_without_ext]}{num}{ext}", ext + "!!", res_dict)
                if match_type == MatchType.NewMatch:
                    matched += 1

    return matched