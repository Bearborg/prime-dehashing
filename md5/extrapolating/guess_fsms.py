import os
import json
from md5.extrapolating.update_if_matched import update_if_matched, MatchType, start_yellow, end_color
try:
    import tomllib
except ModuleNotFoundError:
    raise ModuleNotFoundError("Python 3.11 or greater is required")
try:
    import yaml
    import winshell
except ModuleNotFoundError:
    raise ModuleNotFoundError(
        "Required modules are missing. Please run the following command: 'pip install pyyaml"
    )

config_path = r'./config.toml'
config = tomllib.load(open(config_path, 'rb'))
mp3_mock_tree_enabled = config['features']['mp3_enable_mock_tree']
mp3_hecl_root = config['paths']['mp3_hecl_root']
mp3_tag_cache_file = r'./output_json/mp3_tag_cache.json'

def recurse_fsm(res_dict, parent_dir: str, rel_path: str):
    matched = 0
    abs_path = os.path.join(mp3_hecl_root, rel_path)
    with open(abs_path, 'r', encoding='utf8') as fsm_yaml:
        fsm = yaml.load(fsm_yaml.read(), Loader=yaml.CLoader)
    for sub_fsm in fsm['detail']['unknown3']:
        best_matched = MatchType.Unmatched
        name = sub_fsm['name']
        sub_path = sub_fsm['fsmId']
        sub_hash = sub_path[-21:-5]
        if (hash_val := int(sub_hash, 16)) in res_dict:
            if not res_dict[hash_val].endswith('!!'):
                continue
        new_paths = [
            f'$/ai/statemachines2/{parent_dir}/{name.lower()}.fsm2',
            f'$/ai/statemachines2/{parent_dir}/{parent_dir}{name.lower()}.fsm2',
        ]
        for new_path in new_paths:
            commit = True
            match_type = update_if_matched(new_path, '.fsm2!!', res_dict, commit)
            if match_type == MatchType.NewMatch and commit:
                matched += 1
                best_matched = MatchType.NewMatch
            elif match_type == MatchType.HadMatch and best_matched == MatchType.Unmatched:
                best_matched = match_type
        if best_matched == MatchType.Unmatched:
            print(f'{start_yellow}Unmatched: {parent_dir} sub-FSM {name}, hash {sub_hash}{end_color}')
        matched += recurse_fsm(res_dict, parent_dir, sub_path)
    return matched

def guess_fsms(res_dict):
    """
    Attempts to find FSM2 files by recursing through dependencies.

    :param res_dict: A dict of integer hashes to string filenames. Non-matching filenames should be suffixed with "!!".
    :return: Number of newly-added filename matches, as an int.
    """
    print("Checking FSM2 files...")
    matched = 0

    if not mp3_mock_tree_enabled:
        return matched
    mp3_tag_cache = json.load(open(mp3_tag_cache_file, 'r'))

    for key in res_dict:
        if res_dict[key][-5:].lower() in ['.fsm2']:
            key_str = f'{key:016X}'
            if key_str not in mp3_tag_cache:
                continue
            parent_dir = os.path.split(res_dict[key])[0][len('$/ai/statemachines2/'):]
            rel_path = mp3_tag_cache[key_str][1]
            matched += recurse_fsm(res_dict, parent_dir, rel_path)


    return matched