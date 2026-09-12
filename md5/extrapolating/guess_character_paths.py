import os
import re
from md5.extrapolating.update_if_matched import update_if_matched, start_green, end_color
from utils.md5 import retro_md5

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
        if res_dict[key].split('.')[-1] in ['char!!', 'cmdl!!', 'cskr!!', 'cin!!', 'dcln!!']:
            filename, ext = os.path.splitext(os.path.split(res_dict[key])[-1])
            if re.match(r'.*_\d$', filename):
                filename = filename[:-2]
            #filename = 'Samus_Morphball_Cinematic'
            actor_name = filename #'perch'
            for new_path in {
                f'$/characters/{actor_name}/cooked/{filename}{ext[:-2]}',
                f'$/characters/{actor_name}/cooked/{actor_name}{ext[:-2]}',
                f'$/characters/{actor_name}/cooked/{filename}_bound{ext[:-2]}',
                f'$/characters/{actor_name}/cooked/{actor_name}_{filename}{ext[:-2]}',
                f'$/characters/{actor_name}/cooked/b_bind_{actor_name}{ext[:-2]}',
                f'$/characters/{actor_name}/cooked/b_bind_{filename}{ext[:-2]}',
                f'$/characters/{actor_name}/cooked/{actor_name}_bound{ext[:-2]}',
                f'$/characters/{actor_name}/cooked/dark_{filename}{ext[:-2]}',
                f'$/characters/{actor_name}/cooked/dark_{actor_name}{ext[:-2]}',
                f'$/characters/{actor_name}/cooked/dark_{filename}_bound{ext[:-2]}',
                f'$/characters/{actor_name}/cooked/dark_{actor_name}_bound{ext[:-2]}',
                f'$/characters/{actor_name}/cooked/{filename}_frozen{ext[:-2]}',
                f'$/characters/{actor_name}/cooked/{filename}_bound_frozen{ext[:-2]}',
                f'$/characters/{actor_name}/cooked/{filename}_frozen_bound{ext[:-2]}',
                f'$/characters/{actor_name}/cooked/{filename}_ice{ext[:-2]}',
                f'$/characters/{actor_name}/cooked/{filename}_bound_ice{ext[:-2]}',
                f'$/characters/{actor_name}/cooked/{filename}_ice_bound{ext[:-2]}',
                f'$/characters/{actor_name}/cooked/{actor_name}_frozen{ext[:-2]}',
                f'$/characters/{actor_name}/cooked/frozen_{actor_name}{ext[:-2]}',
                f'$/characters/{actor_name}/cooked/frozen_{actor_name}_bound{ext[:-2]}',
                f'$/characters/{actor_name}/cooked/frozen_{filename}{ext[:-2]}',
                f'$/characters/{actor_name}/cooked/frozen_{filename}_bound{ext[:-2]}',
                f'$/characters/{actor_name}/cooked/{actor_name}_bound_frozen{ext[:-2]}',
                f'$/characters/{actor_name}/cooked/{actor_name}_frozen_bound{ext[:-2]}',
                f'$/characters/{actor_name}/cooked/{actor_name}_ice{ext[:-2]}',
                f'$/characters/{actor_name}/cooked/{actor_name}_bound_ice{ext[:-2]}',
                f'$/characters/{actor_name}/cooked/{actor_name}_ice_bound{ext[:-2]}',
                f'$/characters/{actor_name}/cooked/{actor_name}_xray{ext[:-2]}',
                f'$/characters/{actor_name}/cooked/{actor_name}_bound_xray{ext[:-2]}',
                f'$/animatedobjects/general/{actor_name}/cooked/{filename}{ext[:-2]}',
                f'$/animatedobjects/general/{actor_name}/cooked/{actor_name}{ext[:-2]}',
                f'$/animatedobjects/general/pickups/{actor_name}/cooked/{filename}{ext[:-2]}',
                f'$/animatedobjects/general/pickups/{actor_name}/cooked/{actor_name}{ext[:-2]}',
                f'$/animatedobjects/introlevel/{actor_name}/cooked/{filename}{ext[:-2]}',
                f'$/animatedobjects/introlevel/scenes/{actor_name}/cooked/{filename}{ext[:-2]}',
                f'$/animatedobjects/introunderwater/{actor_name}/cooked/{filename}{ext[:-2]}',
                f'$/animatedobjects/introunderwater/scenes/{actor_name}/cooked/{filename}{ext[:-2]}',
                f'$/animatedobjects/ruinsworld/{actor_name}/cooked/{filename}{ext[:-2]}',
                f'$/animatedobjects/ruinsworld/scenes/{actor_name}/cooked/{filename}{ext[:-2]}',
                f'$/animatedobjects/iceworld/{actor_name}/cooked/{filename}{ext[:-2]}',
                f'$/animatedobjects/iceworld/scenes/{actor_name}/cooked/{filename}{ext[:-2]}',
                f'$/animatedobjects/overworld/{actor_name}/cooked/{filename}{ext[:-2]}',
                f'$/animatedobjects/overworld/scenes/{actor_name}/cooked/{filename}{ext[:-2]}',
                f'$/animatedobjects/minesworld/{actor_name}/cooked/{filename}{ext[:-2]}',
                f'$/animatedobjects/minesworld/scenes/{actor_name}/cooked/{filename}{ext[:-2]}',
                f'$/animatedobjects/lavaworld/{actor_name}/cooked/{filename}{ext[:-2]}',
                f'$/animatedobjects/lavaworld/scenes/{actor_name}/cooked/{filename}{ext[:-2]}',
                f'$/animatedobjects/craterworld/{actor_name}/cooked/{filename}{ext[:-2]}',
                f'$/animatedobjects/craterworld/scenes/{actor_name}/cooked/{filename}{ext[:-2]}',
                f'$/animatedobjects/crater/{actor_name}/cooked/{filename}{ext[:-2]}',
                f'$/animatedobjects/crater/scenes/{actor_name}/cooked/{filename}{ext[:-2]}',
                f'$/characters/samusgun/cooked/{actor_name}actions/{filename}{ext[:-2]}',
                f'$/characters/samusgun/cooked/models/{filename}{ext[:-2]}',
                f'$/characters/samus/samus_low_res/cooked/{actor_name}/{filename}{ext[:-2]}',
                f'$/characters/samus/samus_high_res/cooked/{filename}{ext[:-2]}',
                f'$/characters/samus_ball/{actor_name}/cooked/{filename}{ext[:-2]}',
                f'$/characters/space_pirate/cooked/{actor_name}/{filename}{ext[:-2]}',
                f'$/characters/elite_space_pirate/cooked/{actor_name}/{filename}{ext[:-2]}',
                f'$/characters/metroid_prime/cooked/{filename}{ext[:-2]}',
                f'$/characters/metroid_prime/cooked/metroid_prime_body/{filename}{ext[:-2]}',
                f'$/characters/flying_pirate/cooked/{actor_name}/{filename}{ext[:-2]}',
                f'$/characters/gargantuan_beetle/cooked/{actor_name}/{filename}{ext[:-2]}',
                f'$/characters/metaree/cooked/{actor_name}/{filename}{ext[:-2]}',
                f'$/characters/ice_sheegoth/cooked/{actor_name}/{filename}{ext[:-2]}',
                # f'$/animatedobjects/general/chozo_artifacts/cooked/{actor_name}/{filename}{ext[:-2]}'

            }:
                if retro_md5(new_path.lower()) == key:
                    print(f'{start_green}Match: {res_dict[key]} -> {new_path}{end_color}')
                    res_dict[key] = new_path
                    matched += 1
                else:
                    update_if_matched(new_path, ext, res_dict, False)
        elif res_dict[key].split('.')[-1] == 'ani':
            cooked_dir, filename = os.path.split(res_dict[key])
            base_name: str = res_dict[key].split('/')[-3]
            names = {
                base_name,
                base_name.lstrip('1234567890_'),
                base_name[base_name.find('_') + 1:],
                base_name.replace('_', ''),
                base_name.lstrip('1234567890_').replace('_', ''),
                base_name[base_name.find('_') + 1:].replace('_', ''),
            }
            # if filename.lower().endswith("_ready.ani"):
            #     names.add(filename[:-10])
            # if filename.lower().endswith("_anim.ani"):
            #     names.add(filename[:-9])
            # if filename.lower().endswith("_bound.ani"):
            #     names.add(filename[:-10])
            split_name = base_name
            while '_' in split_name:
                split_name = '_'.join(split_name.split('_')[:-1])
                if len(split_name) > 1:
                    names.add(split_name)
            split_name = base_name
            while '_' in split_name:
                split_name = '_'.join(split_name.split('_')[1:])
                if len(split_name) > 1:
                    names.add(split_name)
            new_paths = []
            for name in names:
                new_paths.extend([
                f'{cooked_dir}/{name}.char',
                f'{cooked_dir}/{name}_samus.char',
                f'{cooked_dir}/samus_{name}.char',
                f'{cooked_dir}/samus_{name}_cinematic.char',
                f'{cooked_dir}/{name}_cinematic.char',
                f'{cooked_dir}/{name}_samus_cinematic.char',
                f'{cooked_dir}/{name}_cinematic_samus.char',
                f'{cooked_dir}/{name}_logbook.char',
                f'{cooked_dir}/{name}_bound.char',
                f'{cooked_dir}/{name}.cmdl',
                f'{cooked_dir}/{name}_bound.cmdl',
                f'{cooked_dir}/b_bind_{name}.cmdl',
                f'{cooked_dir}/{name}.cin',
                f'{cooked_dir}/{name}_bound.cin',
                f'{cooked_dir}/{name}_anim.char',
                f'{cooked_dir}/{name}_animation.char',
                f'{cooked_dir}/{name}anim.char',
                f'{cooked_dir}/{name}animation.char',
            ])
            for new_path in new_paths:
                match_result = update_if_matched(new_path, new_path.split('.')[-1] + '!!', res_dict)
                if match_result.value == 1:
                    matched += 1
        elif res_dict[key].split('.')[-1] == 'char' or res_dict[key].split('.')[-1] == 'cmdl' or res_dict[key].split('.')[-1] == 'ani':
            path, fname = os.path.split(res_dict[key][:-4])
            # fname = filename.replace('_','')
            # fname = re.sub(r"([a-z])([A-Z])", r"\1_\2", filename)
            # path = '$/Characters/spank_weed/cooked'
            # filename = 'war_wasp'
            char_names = {fname}
            if path.endswith('/cooked'):
                char_names.add(os.path.split(os.path.split(path)[0])[1])
            for name in char_names.copy():
                char_names.add(name.replace('_', ''))
                char_names.add(re.sub(r"([a-z])([A-Z])", r"\1_\2", name))
            for filename in char_names:
                possible_paths = [
                    f'{path}/{filename}_logbook.char',
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
                tex_dirs = [
                    f'{path[:-7]}/sourceimages/',
                    f'{path[:-7]}/textures/',
                    f'$/characters/common_textures/',
                    f'$/characters/common_textures/{filename}/'
                ]
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
                    f'xray.txtr',
                    f'chest.txtr',
                    f'leg_arm.txtr',
                    f'glow.txtr',
                    f'base.txtr',
                    f'limbs_c.txtr',
                    f'body_c.txtr',
                    f'head_c.txtr',
                    f'heart_c.txtr',
                    f'brain_c.txtr',
                    f'torso_c.txtr',
                    f'eye_c.txtr',
                    f'eyeball_c.txtr',
                    f'eyes_c.txtr',
                    f'teeth_c.txtr',
                    f'neck_c.txtr',
                    f'skin_c.txtr',
                    f'shell_c.txtr',
                    f'metal_c.txtr',
                    f'main_c.txtr',
                    f'reflected_c.txtr',
                    f'highlight_reflected_c.txtr',
                    f'reflectivity_c.txtr',
                    f'arm_c.txtr',
                    f'arms_c.txtr',
                    f'leg_c.txtr',
                    f'legs_c.txtr',
                    f'mouth_c.txtr',
                    f'wing_c.txtr',
                    f'wings_c.txtr',
                    f'chin_c.txtr',
                    f'bottom_c.txtr',
                    f'top_c.txtr',
                    f'xray_c.txtr',
                    f'chest_c.txtr',
                    f'leg_arm_c.txtr',
                    f'glow_c.txtr',
                    f'base_c.txtr',
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
                    f'{filename}_limbs_c.txtr',
                    f'{filename}_body_c.txtr',
                    f'{filename}_head_c.txtr',
                    f'{filename}_heart_c.txtr',
                    f'{filename}_brain_c.txtr',
                    f'{filename}_torso_c.txtr',
                    f'{filename}_eye_c.txtr',
                    f'{filename}_eyeball_c.txtr',
                    f'{filename}_eyes_c.txtr',
                    f'{filename}_teeth_c.txtr',
                    f'{filename}_neck_c.txtr',
                    f'{filename}_skin_c.txtr',
                    f'{filename}_shell_c.txtr',
                    f'{filename}_metal_c.txtr',
                    f'{filename}_main_c.txtr',
                    f'{filename}_organs_c.txtr',
                    f'{filename}_arm_c.txtr',
                    f'{filename}_arms_c.txtr',
                    f'{filename}_leg_c.txtr',
                    f'{filename}_legs_c.txtr',
                    f'{filename}_mouth_c.txtr',
                    f'{filename}_wing_c.txtr',
                    f'{filename}_wings_c.txtr',
                    f'{filename}_chin_c.txtr',
                    f'{filename}_bottom_c.txtr',
                    f'{filename}_top_c.txtr',
                    f'{filename}_chest_c.txtr',
                    f'{filename}_leg_arm_c.txtr',
                    f'{filename}_base_c.txtr',
                    f'{filename}.txtr',
                    f'{filename}1.txtr',
                    f'{filename}2.txtr',
                    f'{filename}01.txtr',
                    f'{filename}02.txtr',
                    f'{filename}01a.txtr',
                    f'{filename}02a.txtr',
                    f'{filename}01a_c.txtr',
                    f'{filename}02a_c.txtr',
                    f'{filename}01ai.txtr',
                    f'{filename}02ai.txtr',
                    f'{filename}_parts.txtr',
                    f'parts/{filename}_parts.txtr',
                    f'{filename}_parts_c.txtr',
                    f'{filename}_partsi.txtr',
                    f'{filename}_parts_incan.txtr',
                    f'{filename}_parts_color.txtr',
                    f'{filename}_incan.txtr',
                    f'{filename}_incandes.txtr',
                    f'{filename}_incandescence.txtr',
                    f'{filename}_c.txtr',
                    f'{filename}c_low.txtr',
                    f'{filename}_c.txtr',
                    f'{filename}_c_low.txtr',
                    f'{filename}_low.txtr',
                    f'{filename}_color.txtr',
                    f'{filename}_dark_color.txtr',
                    f'{filename}_color_dark.txtr',
                    f'{filename}i.txtr',
                    f'{filename}_i.txtr',
                    f'{filename}_reflected.txtr',
                    f'{filename}_reflectivity.txtr',
                    f'reflected_{filename}.txtr',
                    f'reflectivity_{filename}.txtr',
                    f'{filename}_xray.txtr',
                    f'{filename}xray.txtr',
                    f'{filename}_glow.txtr',
                    f'{filename}.txtr',
                ]
                for directory in tex_dirs:
                    possible_paths.extend([directory + name for name in tex_names])
                    possible_paths.extend([directory + name.replace('_', '') for name in tex_names])
                for new_path in possible_paths:
                    commit = False
                    match_result = update_if_matched(new_path, new_path.split('.')[-1] + '!!', res_dict, commit)
                    if match_result.value == 1 and commit:
                        matched += 1
        if res_dict[key].split('.')[-1] == 'cmdl' and res_dict[key].startswith('$/characters/'):
            path, fname = os.path.split(res_dict[key][:-5])
            if fname.lower().endswith('_bound'):
                fname = fname[:-6]
            char_names = {fname}
            if path.endswith('/cooked'):
                char_names.add(os.path.split(os.path.split(path)[0])[1])
            for name in char_names.copy():
                char_names.add(name.replace('_', ''))
                char_names.add(re.sub(r"([a-z])([A-Z])", r"\1_\2", name))
            for filename in char_names:
                possible_paths = [
                    f'$/ai/statemachines2/{filename}/{filename}.fsm2',
                    f'{path}/{filename}.cskr',
                    f'{path}/{filename}.char',
                    f'{path}/{filename}_{filename}.char',
                    f'{path}/{filename}_anim.sand',
                    f'{path}/{filename}.sand',
                    f'{path}/{filename}.cin',
                    f'{path}/{filename}_frozen.cmdl',
                    f'{path}/{filename}_frozen.cskr',
                    f'{path}/{filename}_frozen.cin',
                    f'{path}/{filename}_frozen_bound.cmdl',
                    f'{path}/{filename}_ice_bound.cmdl',
                    f'{path}/{filename}_ice_bound.cskr',
                    f'{path}/{filename}_ice_bound.cin',
                    f'{path}/{filename}_entangle_bound.cmdl',
                    f'{path}/{filename}_entangle_bound.cskr',
                    f'{path}/{filename}_entangle_bound.cin',
                    f'{path}/{filename}_bound_entangle.cmdl',
                    f'{path}/{filename}_bound_entangle.cskr',
                    f'{path}/{filename}_bound_entangle.cin',
                    f'{path}/{filename}_entangle.cmdl',
                    f'{path}/{filename}_entangle.cskr',
                    f'{path}/{filename}_entangle.cin',
                    f'{path}/{filename}_entangled_bound.cmdl',
                    f'{path}/{filename}_entangled_bound.cskr',
                    f'{path}/{filename}_entangled_bound.cin',
                    f'{path}/{filename}_bound_entangled.cmdl',
                    f'{path}/{filename}_bound_entangled.cskr',
                    f'{path}/{filename}_bound_entangled.cin',
                    f'{path}/{filename}_entangler_bound.cmdl',
                    f'{path}/{filename}_entangler_bound.cskr',
                    f'{path}/{filename}_entangler_bound.cin',
                    f'{path}/{filename}_bound_entangler.cmdl',
                    f'{path}/{filename}_bound_entangler.cskr',
                    f'{path}/{filename}_bound_entangler.cin',
                    f'{path}/{filename}_entangled.cmdl',
                    f'{path}/{filename}_entangled.cskr',
                    f'{path}/{filename}_entangled.cin',
                    f'{path}/{filename}_entangler.cmdl',
                    f'{path}/{filename}_entangler.cskr',
                    f'{path}/{filename}_entangler.cin',
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
                    f'{path}/{filename}_anim.char',
                    f'{path}/{filename}_animation.char',
                    f'{path}/{filename}anim.char',
                    f'{path}/{filename}animation.char',
                ]
                for new_path in possible_paths:
                    match_result = update_if_matched(new_path, new_path.split('.')[-1] + '!!', res_dict)
                    if match_result.value == 1:
                        matched += 1
    return matched

