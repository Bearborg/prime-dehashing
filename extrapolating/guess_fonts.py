import os
from extrapolating.update_if_matched import update_if_matched, MatchType


def guess_fonts(res_dict):
    """
    Attempts to match FONT files by matching their PAK filenames with some common folders for fonts.

    :param res_dict: A dict of integer hashes to string filenames. Non-matching filenames should be suffixed with "!!".
    :return: Number of newly-added filename matches, as an int.
    """
    print("Checking fonts...")
    matched = 0

    for key in res_dict:
        if res_dict[key].rstrip('!').endswith('rpff'):
            filename = os.path.split(res_dict[key].rstrip('!'))[-1]
            new_paths = [
                f'$/GUI_ART/Common_Fonts/{filename}',
                f'$/GUI_ART/Common_Fonts/{filename[:-5]}_tex.txtr',
                f'$/fonts/{filename}',
                f'$/fonts/{filename[:-5]}_tex.txtr',
            ]
            for new_path in new_paths:
                match_type = update_if_matched(new_path, os.path.splitext(new_path)[1] + "!!", res_dict)
                if match_type == MatchType.NewMatch:
                    matched += 1
                    break
    return matched