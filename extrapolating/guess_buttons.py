import os
from extrapolating.update_if_matched import update_if_matched, MatchType

def guess_buttons(res_dict):
    """
    Attempts to match GUI button textures by matching their PAK filenames with some common folders for GUI elements.

    :param res_dict: A dict of integer hashes to string filenames. Non-matching filenames should be suffixed with "!!".
    :return: Number of newly-added filename matches, as an int.
    """
    print("Checking button icon textures...")
    matched = 0

    for key in res_dict:
        if res_dict[key].endswith('txtr!!') and res_dict[key].startswith('$/GGuiSys'):
            filename = os.path.split(res_dict[key])[-1]
            new_paths = [
                f'$/Strings/English/SourceImages/{filename[:-2]}',
                f'$/Strings/English/SourceImages/HUD_Messages/SourceImages/{filename[:-2]}',
                f'$/Strings/English/SourceImages/HUD_Messages/Tutorials/SourceImages/{filename[:-2]}',
            ]
            for new_path in new_paths:
                match_type = update_if_matched(new_path,'.txtr!!', res_dict)
                if match_type == MatchType.NewMatch:
                    matched += 1
                    break
    return matched