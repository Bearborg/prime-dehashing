import os
from extrapolating.update_if_matched import update_if_matched, start_green, end_color
from utils.crc32 import crc32

def guess_character_paths(res_dict):
    """
    Attempts to match various character-related filenames with a character directory in the $/AnimatedObjects or
    $/Characters folders. Relies on Retro's convention of models/characters/textures sharing similar names.

    Occasionally, it's useful to override the "actor_name" or "filename" vars with a known/guessed character name that
    does not match the character folder.

    :param res_dict: A dict of integer hashes to string filenames. Non-matching filenames should be suffixed with "!!".
    :return: Number of newly-added filename matches, as an int.
    """
    print("Checking character files...")
    matched = 0

    for key in res_dict:
        if res_dict[key].split('.')[-1] in ['acs!!', 'cmdl!!', 'cskr!!', 'cin!!', 'dcln!!']:
            filename, ext = os.path.splitext(os.path.split(res_dict[key])[-1])
            if filename.endswith('_0'):
                filename = filename[:-2]
            # filename = 'samusGunMotion'
            actor_name = filename
            for new_path in {
                f'$/Characters/{actor_name}/cooked/{filename}{ext[:-2]}',
                f'$/Characters/{actor_name}/cooked/{actor_name}{ext[:-2]}',
                f'$/Characters/{actor_name}/cooked/{filename}_bound{ext[:-2]}',
                f'$/Characters/{actor_name}/cooked/{actor_name}_bound{ext[:-2]}',
                f'$/Characters/{actor_name}/cooked/{filename}_frozen{ext[:-2]}',
                f'$/Characters/{actor_name}/cooked/{filename}_bound_frozen{ext[:-2]}',
                f'$/Characters/{actor_name}/cooked/{filename}_frozen_bound{ext[:-2]}',
                f'$/Characters/{actor_name}/cooked/{filename}_ice{ext[:-2]}',
                f'$/Characters/{actor_name}/cooked/{filename}_bound_ice{ext[:-2]}',
                f'$/Characters/{actor_name}/cooked/{filename}_ice_bound{ext[:-2]}',
                f'$/Characters/{actor_name}/cooked/{actor_name}_frozen{ext[:-2]}',
                f'$/Characters/{actor_name}/cooked/{actor_name}_bound_frozen{ext[:-2]}',
                f'$/Characters/{actor_name}/cooked/{actor_name}_frozen_bound{ext[:-2]}',
                f'$/Characters/{actor_name}/cooked/{actor_name}_ice{ext[:-2]}',
                f'$/Characters/{actor_name}/cooked/{actor_name}_bound_ice{ext[:-2]}',
                f'$/Characters/{actor_name}/cooked/{actor_name}_ice_bound{ext[:-2]}',
                f'$/Characters/{actor_name}/cooked/{actor_name}_xray{ext[:-2]}',
                f'$/Characters/{actor_name}/cooked/{actor_name}_bound_xray{ext[:-2]}',
                f'$/AnimatedObjects/General/{actor_name}/cooked/{filename}{ext[:-2]}',
                f'$/AnimatedObjects/General/{actor_name}/cooked/{actor_name}{ext[:-2]}',
                f'$/AnimatedObjects/General/pickups/{actor_name}/cooked/{filename}{ext[:-2]}',
                f'$/AnimatedObjects/General/pickups/{actor_name}/cooked/{actor_name}{ext[:-2]}',
                f'$/AnimatedObjects/Introlevel/{actor_name}/cooked/{filename}{ext[:-2]}',
                f'$/AnimatedObjects/Introlevel/scenes/{actor_name}/cooked/{filename}{ext[:-2]}',
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
                f'$/Characters/samusgun/cooked/{actor_name}actions/{filename}{ext[:-2]}',
                f'$/Characters/samusgun/cooked/models/{filename}{ext[:-2]}',
                f'$/Characters/Samus/samus_low_res/cooked/{actor_name}/{filename}{ext[:-2]}',
                f'$/Characters/samus_ball/{actor_name}/cooked/{filename}{ext[:-2]}',
                f'$/Characters/space_pirate/cooked/{actor_name}/{filename}{ext[:-2]}',
                f'$/Characters/Elite_Space_Pirate/cooked/{actor_name}/{filename}{ext[:-2]}',
                f'$/Characters/metroid_prime/cooked/{filename}{ext[:-2]}',
                f'$/Characters/metroid_prime/cooked/metroid_prime_body/{filename}{ext[:-2]}',
                f'$/Characters/Flying_Pirate/cooked/{actor_name}/{filename}{ext[:-2]}',
                f'$/Characters/gargantuan_beetle/cooked/{actor_name}/{filename}{ext[:-2]}',
                f'$/Characters/metaree/cooked/{actor_name}/{filename}{ext[:-2]}',
                f'$/Characters/ice_sheegoth/cooked/{actor_name}/{filename}{ext[:-2]}',
                # f'$/AnimatedObjects/General/Chozo_Artifacts/cooked/{actor_name}/{filename}{ext[:-2]}'

            }:
                if crc32(new_path.lower()) == key:
                    print(f'{start_green}Match: {res_dict[key]} -> {new_path}{end_color}')
                    res_dict[key] = new_path
                    matched += 1
                else:
                    update_if_matched(new_path, ext, res_dict, False)
        elif res_dict[key].split('.')[-1] == 'ani':
            cooked_dir = os.path.split(res_dict[key])[0]
            name = res_dict[key].split('/')[-3]
            new_path = f'{cooked_dir}/{name}.acs'
            match_result = update_if_matched(new_path, 'acs!!', res_dict)
            if match_result.value == 1:
                matched += 1
        elif res_dict[key].split('.')[-1] == 'acs' and 'Swimmer_Swarm' not in res_dict[key]:
            # Swimmer_Swarm is excluded here to avoid constant false positives from a match in MP2.
            path, filename = os.path.split(res_dict[key][:-4])
            # filename = filename.replace('_','')
            # filename = re.sub(r"([a-z])([A-Z])", r"\1_\2", filename)
            # path = '$/Characters/spank_weed/cooked'
            # filename = 'petals'
            possible_paths = [
                f'{path}/{filename}.cmdl',
                f'{path}/{filename}.cskr',
                f'{path}/{filename}.cin',
                f'{path}/{filename}_bound.cmdl',
                f'{path}/{filename}_bound.cskr',
                f'{path}/{filename}_bound.cin',
                f'{path}/{filename}bound.cmdl',
                f'{path}/{filename}bound.cskr',
                f'{path}/{filename}bound.cin',
                f'{path}/{filename}_frozen.cmdl',
                f'{path}/{filename}_frozen.cskr',
                f'{path}/{filename}_frozen.cin',
                f'{path}/{filename}_frozen_bound.cmdl',
                f'{path}/{filename}_ice_bound.cmdl',
                f'{path}/{filename}_ice_bound.cskr',
                f'{path}/{filename}_ice_bound.cin',
                f'{path}/{filename}_ice.cmdl',
                f'{path}/{filename}_ice.cskr',
                f'{path}/{filename}_ice.cin',
                f'{path}/{filename}_frozen_bound.cskr',
                f'{path}/{filename}_frozen_bound.cin',
                f'{path}/{filename}_bound_frozen.cmdl',
                f'{path}/{filename}_bound_frozen.cskr',
                f'{path}/{filename}_bound_frozen.cin',
                f'{path}/frozen_{filename}.cmdl',
                f'{path}/frozen_{filename}.cskr',
                f'{path}/frozen_{filename}.cin',
                f'{path}/frozen_{filename}_bound.cmdl',
                f'{path}/frozen_{filename}_bound.cskr',
                f'{path}/frozen_{filename}_bound.cin',
                f'{path}/{filename}_bound_xray.cmdl',
                f'{path}/{filename}_bound_xray.cskr',
                f'{path}/{filename}_bound_xray.cin',
                f'{path}/{filename}_xray_bound.cmdl',
                f'{path}/{filename}_xray_bound.cskr',
                f'{path}/{filename}_xray_bound.cin',
                f'{path}/{filename}_xray.cmdl',
                f'{path}/{filename}_xray.cskr',
                f'{path}/{filename}_xray.cin',
                f'{path}/xray_{filename}.cmdl',
                f'{path}/xray_{filename}.cskr',
                f'{path}/xray_{filename}.cin',
                f'{path}/xray_{filename}_bound.cmdl',
                f'{path}/xray_{filename}_bound.cskr',
                f'{path}/xray_{filename}_bound.cin',
            ]
            tex_dirs = [f'{path[:-7]}/sourceimages/', f'{path[:-7]}/textures/', '$/Characters/common_textures/']
            tex_names = [
                f'limbs.txtr',
                f'body.txtr',
                f'head.txtr',
                f'heart.txtr',
                f'brain.txtr',
                f'torso.txtr',
                f'eye.txtr',
                f'eyeball.txtr',
                f'eyes.txtr',
                f'teeth.txtr',
                f'neck.txtr',
                f'skin.txtr',
                f'shell.txtr',
                f'metal.txtr',
                f'main.txtr',
                f'reflected.txtr',
                f'highlight_reflected.txtr',
                f'reflectivity.txtr',
                f'arm.txtr',
                f'arms.txtr',
                f'leg.txtr',
                f'legs.txtr',
                f'mouth.txtr',
                f'wing.txtr',
                f'wings.txtr',
                f'chin.txtr',
                f'bottom.txtr',
                f'top.txtr',
                f'Xray.txtr',
                f'chest.txtr',
                f'leg_arm.txtr',
                f'glow.txtr',
                f'base.txtr',
                f'{filename}_limbs.txtr',
                f'{filename}_body.txtr',
                f'{filename}_head.txtr',
                f'{filename}_heart.txtr',
                f'{filename}_brain.txtr',
                f'{filename}_torso.txtr',
                f'{filename}_eye.txtr',
                f'{filename}_eyeball.txtr',
                f'{filename}_eyes.txtr',
                f'{filename}_teeth.txtr',
                f'{filename}_neck.txtr',
                f'{filename}_skin.txtr',
                f'{filename}_shell.txtr',
                f'{filename}_shell_incan.txtr',
                f'{filename}_metal.txtr',
                f'{filename}_metal_incan.txtr',
                f'{filename}_main.txtr',
                f'{filename}_organs.txtr',
                f'{filename}_arm.txtr',
                f'{filename}_arms.txtr',
                f'{filename}_leg.txtr',
                f'{filename}_legs.txtr',
                f'{filename}_mouth.txtr',
                f'{filename}_wing.txtr',
                f'{filename}_wings.txtr',
                f'{filename}_chin.txtr',
                f'{filename}_bottom.txtr',
                f'{filename}_top.txtr',
                f'{filename}_chest.txtr',
                f'{filename}_leg_arm.txtr',
                f'{filename}_base.txtr',
                f'{filename}.txtr',
                f'{filename}1.txtr',
                f'{filename}2.txtr',
                f'{filename}01.txtr',
                f'{filename}02.txtr',
                f'{filename}01a.txtr',
                f'{filename}02a.txtr',
                f'{filename}01aC.txtr',
                f'{filename}02aC.txtr',
                f'{filename}01aI.txtr',
                f'{filename}02aI.txtr',
                f'{filename}_parts.txtr',
                f'parts/{filename}_parts.txtr',
                f'{filename}_partsC.txtr',
                f'{filename}_partsI.txtr',
                f'{filename}_parts_incan.txtr',
                f'{filename}_parts_color.txtr',
                f'{filename}_incan.txtr',
                f'{filename}_incandes.txtr',
                f'{filename}_incandescence.txtr',
                f'{filename}C.txtr',
                f'{filename}_C.txtr',
                f'{filename}_color.txtr',
                f'{filename}I.txtr',
                f'{filename}_I.txtr',
                f'{filename}_reflected.txtr',
                f'{filename}_reflectivity.txtr',
                f'reflected_{filename}.txtr',
                f'reflectivity_{filename}.txtr',
                f'{filename}_Xray.txtr',
                f'{filename}Xray.txtr',
                f'{filename}_glow.txtr',
                f'{filename}.txtr',
            ]
            for directory in tex_dirs:
                possible_paths.extend([directory + name for name in tex_names])
                possible_paths.extend([directory + name.replace('_', '') for name in tex_names])
            for new_path in possible_paths:
                match_result = update_if_matched(new_path, new_path.split('.')[-1] + '!!', res_dict)
                if match_result.value == 1:
                    matched += 1
        elif res_dict[key].split('.')[-1] == 'cmdl' and res_dict[key].startswith('$/Characters/'):
            path, filename = os.path.split(res_dict[key][:-5])
            possible_paths = [
                f'{path}/{filename}.cskr',
                f'{path}/{filename}.cin',
                f'{path}/{filename}_frozen.cmdl',
                f'{path}/{filename}_frozen.cskr',
                f'{path}/{filename}_frozen.cin',
                f'{path}/{filename}_frozen_bound.cmdl',
                f'{path}/{filename}_ice_bound.cmdl',
                f'{path}/{filename}_ice_bound.cskr',
                f'{path}/{filename}_ice_bound.cin',
                f'{path}/{filename}_ice.cmdl',
                f'{path}/{filename}_ice.cskr',
                f'{path}/{filename}_ice.cin',
                f'{path}/{filename}_frozen_bound.cskr',
                f'{path}/{filename}_frozen_bound.cin',
                f'{path}/{filename}_bound_frozen.cmdl',
                f'{path}/{filename}_bound_frozen.cskr',
                f'{path}/{filename}_bound_frozen.cin',
                f'{path}/frozen_{filename}.cmdl',
                f'{path}/frozen_{filename}.cskr',
                f'{path}/frozen_{filename}.cin',
                f'{path}/frozen_{filename}_bound.cmdl',
                f'{path}/frozen_{filename}_bound.cskr',
                f'{path}/frozen_{filename}_bound.cin',
                f'{path}/{filename}_bound_xray.cmdl',
                f'{path}/{filename}_bound_xray.cskr',
                f'{path}/{filename}_bound_xray.cin',
                f'{path}/{filename}_xray_bound.cmdl',
                f'{path}/{filename}_xray_bound.cskr',
                f'{path}/{filename}_xray_bound.cin',
                f'{path}/{filename}_xray.cmdl',
                f'{path}/{filename}_xray.cskr',
                f'{path}/{filename}_xray.cin',
                f'{path}/xray_{filename}.cmdl',
                f'{path}/xray_{filename}.cskr',
                f'{path}/xray_{filename}.cin',
                f'{path}/xray_{filename}_bound.cmdl',
                f'{path}/xray_{filename}_bound.cskr',
                f'{path}/xray_{filename}_bound.cin',
            ]
            for new_path in possible_paths:
                match_result = update_if_matched(new_path, new_path.split('.')[-1] + '!!', res_dict)
                if match_result.value == 1:
                    matched += 1
    return matched

