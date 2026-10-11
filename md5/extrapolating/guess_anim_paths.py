import os
from md5.extrapolating.update_if_matched import update_if_matched

def guess_anim_paths(res_dict):
    """
    Attempts to match any existing ANIM or EVNT filenames with a character directory in the $/AnimatedObjects or
    $/Characters folders. Mostly relies on Retro's convention of ending ANIM filenames with the character's name.

    Occasionally, it's useful to override the "actor_name" var with a known/guessed character name that does not match
    the ANIM filenames.

    :param res_dict: A dict of integer hashes to string filenames. Non-matching filenames should be suffixed with "!!".
    :return: Number of newly-added filename matches, as an int.
    """
    print("Checking character animations...")
    matched = 0
    anim_folders = set()
    anim_filenames = set()

    for key in res_dict:
        if res_dict[key].split('.')[-1] in ['evnt!!', 'ani!!']:
            filename, ext = os.path.splitext(os.path.split(res_dict[key])[-1])
            actor_names = {filename}
            if filename.endswith('_0') or filename.endswith('_1'):
                filename = filename[:-2]
            if filename.lower().endswith('_ready') or filename.lower().endswith('_anim'):
                actor_names.add(filename[:filename.rfind('_')])
            elif filename.lower().startswith('ready_'):
                actor_names.add(filename[filename.find('_'):])
            else:
                actor_names.add(filename[filename.rfind('_') + 1:])
                # prev_stop = 0
                # for i in range(4):
                #     stop = filename.find('_', prev_stop)
                #     actor_names.add(filename[:stop])
                #     prev_stop = stop + 1
                # actor_names.add(filename[filename.find('_', filename.find('_') + 1):])
            split_name = filename
            while '_' in split_name:
                split_name = '_'.join(split_name.split('_')[:-1])
                if len(split_name) > 1:
                    actor_names.add(split_name)
                    actor_names.add(split_name + 's')
            split_name = filename
            while '_' in split_name:
                split_name = '_'.join(split_name.split('_')[1:])
                if len(split_name) > 1:
                    actor_names.add(split_name)
            for actor_name in actor_names:
                for new_path in {
                    f'$/characters/{actor_name}/cooked/{filename}{ext[:-2]}',
                    f'$/cinematics/{actor_name}/cooked/{filename}{ext[:-2]}',
                    f'$/characters/samus/cooked/{filename}{ext[:-2]}',
                    f'$/animatedobjects/general/{actor_name}/cooked/{filename}{ext[:-2]}',
                    f'$/animatedobjects/general/{actor_name}/cooked/{actor_name}{ext[:-2]}',
                    f'$/animatedobjects/general/pickups/{actor_name}/cooked/{filename}{ext[:-2]}',
                    f'$/animatedobjects/general/pickups/{actor_name}/cooked/{actor_name}{ext[:-2]}',
                    f'$/worlds/abandoned_ship/objects/{actor_name}/cooked/{filename}{ext[:-2]}',
                    f'$/worlds/bryyo/objects/{actor_name}/cooked/{filename}{ext[:-2]}',
                    f'$/worlds/gf_flagship/objects/{actor_name}/cooked/{filename}{ext[:-2]}',
                    f'$/worlds/gf_planet/objects/{actor_name}/cooked/{filename}{ext[:-2]}',
                    f'$/worlds/phaaze/objects/{actor_name}/cooked/{filename}{ext[:-2]}',
                    f'$/worlds/seeds/objects/{actor_name}/cooked/{filename}{ext[:-2]}',
                    f'$/worlds/skytown/objects/{actor_name}/cooked/{filename}{ext[:-2]}',
                    f'$/worlds/sp_planet/objects/{actor_name}/cooked/{filename}{ext[:-2]}',
                    f'$/worlds/space/objects/{actor_name}/cooked/{filename}{ext[:-2]}',
                    f'$/objects/{actor_name}/cooked/{filename}{ext[:-2]}',
                    f'$/objects/_placeholder/generic/{actor_name}/cooked/{filename}{ext[:-2]}',
                    f'$/objects/_placeholder/{actor_name}/cooked/{filename}{ext[:-2]}',
                    f'$/objects/metroid_doors/{actor_name}/cooked/{filename}{ext[:-2]}',
                    f'$/characters/samus/samus_low_res/cooked/multiplayer_balltransitions/{filename}{ext[:-2]}',
                    f'$/characters/samusgun/cooked/{actor_name}/{filename}{ext[:-2]}',
                }:
                    match_result = update_if_matched(new_path, ext, res_dict)
                    if match_result.value == 1:
                        matched += 1
                        break
                anim_filenames.add(filename)
                anim_filenames.add(f'{actor_name}/{filename}')
        elif res_dict[key].endswith('.ani'):
            cooked_path = os.path.split(res_dict[key])[0]
            anim_folders.add(cooked_path)
            anim_folders.add(os.path.split(cooked_path)[0])
            anim_folders.add(cooked_path + '/cinematic')
            anim_folders.add(cooked_path + '/logbook')

            new_path = res_dict[key][:-3] + 'evnt'
            match_result = update_if_matched(new_path, 'evnt!!', res_dict)
            if match_result.value == 1:
                matched += 1
        elif res_dict[key].endswith('.char') or res_dict[key].endswith('.cmdl'):
            anim_folders.add(os.path.split(res_dict[key])[0])
        elif res_dict[key].endswith('.evnt'):
            new_path = res_dict[key][:-4] + 'ani'
            match_result = update_if_matched(new_path, 'ani!!', res_dict)
            if match_result.value == 1:
                matched += 1

    for folder in anim_folders:
        for anim in anim_filenames:
            new_path = f'{folder}/{anim}.ani'
            match_result = update_if_matched(new_path, 'ani!!', res_dict)
            if match_result.value == 1:
                matched += 1

    return matched