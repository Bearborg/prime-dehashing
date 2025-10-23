import os
import re
from extrapolating.update_if_matched import update_if_matched, MatchType

def guess_frmes(res_dict):
    """
    Attempts to match FRME files by matching their PAK filenames with some common folder patterns for GUI frames.

    :param res_dict: A dict of integer hashes to string filenames. Non-matching filenames should be suffixed with "!!".
    :return: Number of newly-added filename matches, as an int.
    """
    print("Checking GUI frames...")
    matched = 0

    for key in res_dict:
        if res_dict[key].endswith('frme!!') and os.path.split(res_dict[key])[-1].startswith('FRME_'):
            filename = os.path.split(res_dict[key])[-1][5:-7]
            un_cameled_filename = re.sub(r"([a-z])([A-Z])", r"\1_\2", filename)
            new_paths = {
                f'$/GUI_ART/{un_cameled_filename}/{filename}.frme',
                f'$/GUI_ART/{un_cameled_filename}/{un_cameled_filename}.frme',
                f'$/GUI_ART/{filename}/{filename}.frme',
                f'$/GUI_ART/{filename}/{un_cameled_filename}.frme'
                f'$/GUI_ART/scene_{un_cameled_filename}/{filename}.frme',
                f'$/GUI_ART/scene_{un_cameled_filename}/{un_cameled_filename}.frme',
                f'$/GUI_ART/scene_{filename}/{filename}.frme',
                f'$/GUI_ART/scene_{filename}/{un_cameled_filename}.frme',
                f'$/mp2_interface_art/{un_cameled_filename}/{filename}.frme',
                f'$/mp2_interface_art/{un_cameled_filename}/{un_cameled_filename}.frme',
                f'$/mp2_interface_art/{filename}/{filename}.frme',
                f'$/mp2_interface_art/{filename}/{un_cameled_filename}.frme',
            }
            for new_path in new_paths:
                match_type = update_if_matched(new_path, '.frme!!', res_dict)
                if match_type == MatchType.NewMatch:
                    matched += 1
                    break
        elif res_dict[key].startswith('$/GUI_ART/'):
                new_path = res_dict[key].replace('GUI_ART', 'mp2_interface_art')
                match_type = update_if_matched(new_path, os.path.splitext(new_path)[1] + '!!', res_dict)
                if match_type == MatchType.NewMatch:
                    matched += 1
                    break
        elif res_dict[key].startswith('$/mp2_interface_art/'):
                new_path = res_dict[key].replace('mp2_interface_art', 'GUI_ART')
                match_type = update_if_matched(new_path, os.path.splitext(new_path)[1] + '!!', res_dict)
                if match_type == MatchType.NewMatch:
                    matched += 1
                    break
    return matched
