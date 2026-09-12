import os
import re
from md5.extrapolating.update_if_matched import update_if_matched, MatchType

def match_audio(res_dict, deep = False):
    """
    Attempts to match CSMP/CAUD files with their respective folders.

    :param res_dict: A dict of integer hashes to string filenames. Non-matching filenames should be suffixed with "!!".
    :return: Number of newly-added filename matches, as an int.
    """
    print("Checking audio files...")
    matched = 0

    cauds = set()

    audio_dirs: set = {
        '$/audio/characters',
        '$/audio/bosses',
        '$/audio/characters/bird_boss',
        '$/audio/cinematics',
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
        "$/audio/worlds/gf_flagship",
        "$/audio/characters/eyepod",
    }

    for key in res_dict:
        if res_dict[key][-5:].lower() in ['.caud', '.csmp']:
            directory, file = os.path.split(res_dict[key])
            if res_dict[key][-5:].lower() == '.caud':
                cauds.add(f'{directory}/{file[:-5]}')
            audio_dirs.add(directory)
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
            audio_dirs.add(f'$/audio/worlds/{world_name}/{room_name}')

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
            prefs.append(names[0][:names[0].find('_', len(prefs[0]))])
            for pref in prefs:
                names = names + [f'{pref}/{n}' for n in names]
            if deep:
                sufs = ['v1', 'v2', 'v3', 'v4']
                for suf in sufs:
                    names = names + [n.replace('.', f'_{suf}.') for n in names]
            for name in names:
                for audio_dir in audio_dirs:
                    new_path = f'{audio_dir}/{name}'
                    match_type = update_if_matched(new_path, ext, res_dict)
                    if match_type == MatchType.NewMatch:
                        matched += 1
                        break

    return matched