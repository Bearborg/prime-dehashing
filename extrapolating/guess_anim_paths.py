import os
from extrapolating.update_if_matched import update_if_matched

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
            if filename.endswith('_0'):
                filename = filename[:-2]
            if filename.lower().endswith('_ready') or filename.lower().endswith('_anim'):
                actor_names.add(filename[:filename.rfind('_')])
            elif filename.lower().startswith('ready_'):
                actor_names.add(filename[filename.find('_'):])
            else:
                actor_names.add(filename[filename.rfind('_') + 1:])
            actor_names.add('07_blocks')
            split_name = filename
            while '_' in split_name:
                split_name = '_'.join(split_name.split('_')[:-1])
                if len(split_name) > 1:
                    actor_names.add(split_name)
            split_name = filename
            while '_' in split_name:
                split_name = '_'.join(split_name.split('_')[1:])
                if len(split_name) > 1:
                    actor_names.add(split_name)
            for actor_name in actor_names:
                for new_path in {
                    f'$/Characters/{actor_name}/cooked/{filename}{ext[:-2]}',
                    f'$/Characters/Samus/cooked/{filename}{ext[:-2]}',
                    f'$/Characters/metroid/cooked/{actor_name}/{filename}{ext[:-2]}',
                    f'$/Characters/metroid_prime/cooked/{actor_name}/{filename}{ext[:-2]}',
                    f'$/AnimatedObjects/General/{actor_name}/cooked/{filename}{ext[:-2]}',
                    f'$/Worlds2/Animated_Objects/General/{actor_name}/cooked/{filename}{ext[:-2]}',
                    f'$/Worlds2/Animated_Objects/General/{actor_name}/cooked/{actor_name}{ext[:-2]}',
                    f'$/Worlds2/Animated_Objects/General/pickups/cooked/{filename}{ext[:-2]}',
                    f'$/Worlds2/Animated_Objects/General/pickups/cooked/{actor_name}{ext[:-2]}',
                    f'$/Worlds2/Animated_Objects/Sandlands/{actor_name}/cooked/{filename}{ext[:-2]}',
                    f'$/Worlds2/Animated_Objects/Sandlands/{actor_name}/cooked/{actor_name}{ext[:-2]}',
                    f'$/Worlds2/Animated_Objects/Swamplands/{actor_name}/cooked/{filename}{ext[:-2]}',
                    f'$/Worlds2/Animated_Objects/Swamplands/{actor_name}/cooked/{actor_name}{ext[:-2]}',
                    f'$/Worlds2/Animated_Objects/Cliffside/{actor_name}/cooked/{filename}{ext[:-2]}',
                    f'$/Worlds2/Animated_Objects/Cliffside/{actor_name}/cooked/{actor_name}{ext[:-2]}',
                    f'$/Worlds2/Animated_Objects/Temple/{actor_name}/cooked/{filename}{ext[:-2]}',
                    f'$/Worlds2/Animated_Objects/Temple/{actor_name}/cooked/{actor_name}{ext[:-2]}',
                    f'$/AnimatedObjects/General/{actor_name}/cooked/{actor_name}{ext[:-2]}',
                    f'$/AnimatedObjects/General/pickups/{actor_name}/cooked/{filename}{ext[:-2]}',
                    f'$/AnimatedObjects/General/pickups/{actor_name}/cooked/{actor_name}{ext[:-2]}',
                    f'$/AnimatedObjects/Introlevel/{actor_name}/cooked/{filename}{ext[:-2]}',
                    f'$/AnimatedObjects/Introlevel/scenes/{actor_name}/cooked/{filename}{ext[:-2]}',
                    f'$/AnimatedObjects/IntroUnderwater/{actor_name}/cooked/{filename}{ext[:-2]}',
                    f'$/AnimatedObjects/IntroUnderwater/scenes/{actor_name}/cooked/{filename}{ext[:-2]}',
                    f'$/AnimatedObjects/RuinsWorld/{actor_name}/cooked/{filename}{ext[:-2]}',
                    f'$/AnimatedObjects/RuinsWorld/scenes/{actor_name}/cooked/{filename}{ext[:-2]}',
                    f'$/AnimatedObjects/IceWorld/{actor_name}/cooked/{filename}{ext[:-2]}',
                    f'$/AnimatedObjects/IceWorld/scenes/{actor_name}/cooked/{filename}{ext[:-2]}',
                    f'$/AnimatedObjects/Overworld/{actor_name}/cooked/{filename}{ext[:-2]}',
                    f'$/AnimatedObjects/Overworld/scenes/{actor_name}/cooked/{filename}{ext[:-2]}',
                    f'$/AnimatedObjects/MinesWorld/{actor_name}/cooked/{filename}{ext[:-2]}',
                    f'$/AnimatedObjects/MinesWorld/scenes/{actor_name}/cooked/{filename}{ext[:-2]}',
                    f'$/AnimatedObjects/LavaWorld/{actor_name}/cooked/{filename}{ext[:-2]}',
                    f'$/AnimatedObjects/LavaWorld/scenes/{actor_name}/cooked/{filename}{ext[:-2]}',
                    f'$/AnimatedObjects/CraterWorld/{actor_name}/cooked/{filename}{ext[:-2]}',
                    f'$/AnimatedObjects/CraterWorld/scenes/{actor_name}/cooked/{filename}{ext[:-2]}',
                    f'$/AnimatedObjects/Crater/{actor_name}/cooked/{filename}{ext[:-2]}',
                    f'$/AnimatedObjects/Crater/scenes/{actor_name}/cooked/{filename}{ext[:-2]}',
                    f'$/Characters/Samus/samus_low_res/cooked/multiplayer_balltransitions/{filename}{ext[:-2]}',
                    f'$/Characters/samusGun/cooked/{actor_name}/{filename}{ext[:-2]}',
                }:
                    match_result = update_if_matched(new_path, ext, res_dict)
                    if match_result.value == 1:
                        matched += 1
                        break
                anim_filenames.add(filename)
        elif res_dict[key].endswith('.ani'):
            anim_folders.add(os.path.split(res_dict[key])[0])

            new_path = res_dict[key][:-3] + 'evnt'
            match_result = update_if_matched(new_path, 'evnt!!', res_dict)
            if match_result.value == 1:
                matched += 1
        elif res_dict[key].endswith('.acs'): # or res_dict[key].endswith('.cmdl'):
            anim_folders.add(os.path.split(res_dict[key])[0])
        elif res_dict[key].endswith('_lightmap0.txtr') and 'Worlds2' in res_dict[key]:
            room_path = os.path.split(res_dict[key])[0].replace('Worlds2/', 'Worlds2/Animated_Objects/')
            anim_folders.add(room_path)
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