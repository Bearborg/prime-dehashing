import os
import re
from md5.extrapolating.update_if_matched import update_if_matched, MatchType
from utils.md5 import partial_retro_md5, finalize_retro_md5

def match_audio(res_dict, deep = False):
    """
    Attempts to match CSMP/CAUD files with their respective folders.

    :param res_dict: A dict of integer hashes to string filenames. Non-matching filenames should be suffixed with "!!".
    :return: Number of newly-added filename matches, as an int.
    """
    print("Checking audio files...")
    matched = 0

    cauds = set()

    audio_dir_seeds: set = {
        '$/audio/characters',
        '$/audio/bosses',
        '$/audio/characters/bird_boss',
        '$/audio/characters/phazonleech',
        '$/audio/characters/hatcher',
        '$/audio/cinematics',
        '$/audio/cinematics/ghor_intro',
        '$/audio/cinematics/ghor_outro',
        '$/audio/cinematics/gandrayda_outro',
        '$/audio/cinematics/mogenar_intro',
        '$/audio/cinematics/mogenar_outro',
        '$/audio',
        '$/audio/worlds',
        '$/audio/worlds/generic',
        '$/audio/worlds/phaaze/global',
        '$/audio/worlds/pirate/global',
        '$/audio/worlds/bryyo/global',
        '$/audio/worlds/skytown/global',
        '$/audio/worlds/phaaze',
        '$/audio/worlds/pirate',
        '$/audio/worlds/bryyo',
        '$/audio/worlds/skytown',
        '$/audio/worlds/abandoned',
        '$/audio/voice',
        '$/audio/samus',
        "$/audio/worlds/gf_flagship",
    }

    audio_dirs: dict = {d: partial_retro_md5(d) for d in audio_dir_seeds}
    for key in res_dict:
        if res_dict[key][-5:].lower() in ['.caud', '.csmp']:
            directory, file = os.path.split(res_dict[key])
            if res_dict[key][-5:].lower() == '.caud':
                cauds.add(f'{directory}/{file[:-5]}')
            audio_dirs[directory] = partial_retro_md5(directory)
        elif res_dict[key][-5:].lower() in ['.mrea']:
            directory, file = os.path.split(res_dict[key])
            room_name, _ = os.path.splitext(file)
            world_name = directory.split('/')[2]
            if world_name == 'sp_planet':
                world_name = 'pirate'
            if world_name == 'gf_flagship':
                world_name = 'gf_ship'
            if world_name == 'abandoned_ship':
                world_name = 'abandoned'
            room_str = f'$/audio/worlds/{world_name}/{room_name}'
            audio_dirs[room_str] = partial_retro_md5(room_str)

    for caud in cauds:
        for i in range(5):
            new_path = f'{caud}_{i:02}.csmp'
            match_type = update_if_matched(new_path, '.csmp!!', res_dict)
            if match_type == MatchType.NewMatch:
                matched += 1
    for key in res_dict:
        if res_dict[key][-7:].lower() in ['.caud!!', '.csmp!!']:
            ext = res_dict[key][-7:].lower()
            names: list[str] = [os.path.split(res_dict[key])[1][:-2]]
            if match := re.match(r'(.*_)(\d+)(\.csmp)', names[0]):
                names.append(f'{match[1]}{int(match[2]) + 1}{match[3]}')
                names.append(f'{match[1]}{int(match[2]) + 1:02}{match[3]}')
            prefs = [names[0][:names[0].find('_')]]
            prefs.append(names[0][:names[0].find('_', len(prefs[0]) + 1)])
            for pref in prefs:
                names = names + [f'{pref}/{n}' for n in names]
                if "_" in pref:
                    names = names + [f'{pref.replace("_", "")}/{n}' for n in names]
            if deep:
                sufs = ['v1', 'v2', 'v3', 'v4']
                for suf in sufs:
                    names = names + [n.replace('.', f'_{suf}.') for n in names]
            for name in names:
                for audio_dir in audio_dirs:
                    hash_obj = audio_dirs[audio_dir].copy()
                    hash_obj.update(('/' + name).encode())
                    hashed_val = finalize_retro_md5(hash_obj)
                    if hashed_val in res_dict:
                        new_path = f'{audio_dir}/{name}'
                        match_type = update_if_matched(new_path, ext, res_dict)
                        if match_type == MatchType.NewMatch:
                            matched += 1
                            break

    return matched