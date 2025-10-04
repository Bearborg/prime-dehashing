from utils.crc32 import crc32
from enum import IntEnum
from typing import Dict

start_red = '\033[91m'
start_yellow = '\033[93m'
start_green = '\033[92m'
end_color = '\033[0m'

class MatchType(IntEnum):
    Unmatched = 0,
    NewMatch = 1,
    HadMatch = 2


def update_if_matched(path: str, target_suffix: str, res_dict: Dict[int, str], commit=True) -> MatchType:
    """
    General-purpose function for testing whether a guessed filename matches any hash in the resource dictionary. Takes
    in a desired suffix so that false-positives with incorrect extensions can be rejected. Optionally has a "no commit"
    mode that does not update the resource dict when a match is found.

    :param path: Path we're attempting to find a match for.
    :param target_suffix: Expected file extension of the hash we're trying to match. Should typically end with "!!".
    :param res_dict: A dict of integer hashes to string filenames. Non-matching filenames should be suffixed with "!!".
    :param commit: Boolean indicating whether we should immediately update the resource dictionary when we find a match,
                    or treat it as unconfirmed.
    :return: MatchType enum indicating whether we found a new match, already had a match for this hash, or did not find
            a match.
    """
    key = crc32(path.lower())
    if key in res_dict:
        if res_dict[key].endswith(target_suffix):
            if commit:
                print(f'{start_green}Match: {res_dict[key]} -> {path}{end_color}')
                res_dict[key] = path
            else:
                print(f'{start_yellow}Potential match: {res_dict[key]} -?> {path}{end_color}')
            return MatchType.NewMatch
        elif target_suffix.endswith('!!') and res_dict[key].endswith(target_suffix[:-2]):
            # if res_dict[key].lower() != path.lower():
            #     print(f'{start_yellow}Pre-existing match: {res_dict[key]} -x-> {path}{end_color}')
            return MatchType.HadMatch
        else:
            if commit:
                print(f'{start_red}False positive: {res_dict[key]} -x-> {path}{end_color}')
            return MatchType.Unmatched
    else:
        return MatchType.Unmatched