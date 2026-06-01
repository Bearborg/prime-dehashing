import os
import string
from typing import Set
import utils.crc32
from extrapolating.update_if_matched import update_if_matched, MatchType

def guess_textures(res_dict, deep_search: bool = False):
    """
    Attempts to match texture files by testing if known texture filenames were reused in other texture folders.
    Optionally, the deep_search parameter will attempt fuzzy matching by adding/removing digits and other common
    prefixes/suffixes (this is disabled by default, as it can be very slow and generates many false positives).

    Due to a high rate of false positives, this function does not automatically add matches to the DB, and treats them
    only as potentially correct.

    :param res_dict: A dict of integer hashes to string filenames. Non-matching filenames should be suffixed with "!!".
    :param deep_search: A boolean determining whether to use computationally costlier matching techniques.
    :return: Number of newly-added filename matches, as an int.
    """
    print("Checking textures...")
    matched = 0

    tex_folders: Set[str] = set()
    tex_folders.update([
        '$/AnimatedObjects/Introlevel/sourceimages',
        '$/AnimatedObjects/IceWorld/sourceimages',
        '$/AnimatedObjects/MinesWorld/sourceimages',
        '$/AnimatedObjects/Overworld/sourceimages',
        '$/AnimatedObjects/RuinsWorld/sourceimages',
        '$/AnimatedObjects/General/pickups/powerbomb/sourceimages',
        '$/Worlds/Mines/connect_x/sourceimages',
        '$/Worlds/Crater/connect_x/sourceimages',
        '$/Worlds/IntroUnderwater/connect_x/sourceimages',
        '$/Worlds/IceWorld/connect_x/sourceimages',
        '$/Worlds/Overworld/connect_x/sourceimages',
        '$/Worlds/LavaWorld/common_textures',
        '$/Worlds/RuinWorld/pickuproom/sourceimages',
        '$/Worlds/RuinWorld/pickuproom_2/sourceimages',
        '$/Worlds/RuinWorld/pickuproom_3/sourceimages',
        '$/Worlds/RuinWorld/pickuproom_4/sourceimages',
    ])
    tex_names: Set[str] = set()
    tex_names.update([
        'redfloornewc.txtr',
        'redfloornew_c.txtr',
        'redfloornew.txtr',
        'redfloorc.txtr',
        'redfloor.txtr',
        'g2j9tdvod8jj3i.txtr', #pickup room floor
        'g2j9tdvod8jj3c.txtr',
        #'vvstsvlkdvqesjocc.txtr', # vine
        '12_plants_vin128C.txtr', # vine
        'tuwugkdtofyzgpzdyfc.txtr', # ice wall section
        'yc2eut_h1sb4hc.txtr', # orange metal square
        'gdcusamllaaknnblc.txtr', #  small tiled grating
        'ms_morphballtubeC.txtr',
        'ms_morphballtube2C.txtr',
        'ms_morphballtubeI.txtr',
        'wall0alt2.txtr',
        'wall0alt2c.txtr',
        'mud06C.txtr',
        'brace2c.txtr',
        'brace2.txtr',
        'cylinder1.txtr',
        'cylinder1c.txtr'
        'cylinder.txtr',
        'verticalbraceC.txtr',
        'enspikec.txtr',
        'enspikesmallc.txtr',
        'enspikecsmall.txtr',
        'enspike.txtr',
        'spike.txtr',
        'spikec.txtr',
        'enspikesmall.txtr',
        'pipe_r.txtr',
        '02circletC.txtr'
        'rbrace_r.txtr',
        'spout3c.txtr',
        'spout3.txtr',
        'roc_r.txtr',
        'stonepipes4.txtr',
        'stonepipes3.txtr',
        'stonepipes2.txtr',
        'stonepipes1.txtr',
        'stonepipes.txtr',
        'x_ragbcdirty.txtr',
        'x_ragbcdirtyc.txtr',
        'sismopor_ev.txtr',
        '_blobsr02c.txtr',
        '_blobsr01c.txtr',
        'mossrockdirt.txtr',
        'brockblendC.txtr',
        'brockblend.txtr',
        'platebracesC.txtr',
        'fountainnecc.txtr',
        'conc128C.txtr',
        '_walR.txtr',
        '_floB.txtr',
        'rubleC.txtr',
        'ruble.txtr',
        'rubble.txtr',
        'rubbleC.txtr',
        'tingC.txtr',
        'ting.txtr',
        '_latch13_r.txtr',
        '_latch2_r.txtr',
        '_latch3_r.txtr',
        '_trimtest.txtr',
        'rockbaseD_r.txtr',
        'rbrace_r.txtr',
        'toppanel2C.txtr',
        'normsh1.txtr',
        'normsh2.txtr',
        'normsh3.txtr',
        'bug7.txtr',
        'newgrateyc.txtr',
        'stthing_r.txtr',
        'build_3Cr.txtr',
        'zwwpmeb01_rc.txtr',
        'zwwpmeb02C.txtr',
        'globe.txtr',
        'res_drips_2_snowC.txtr',
        'hummyd_nc.txtr',
        'budend1c.txtr',
        'budendc.txtr',
        'budend3c.txtr',
        'budend4c.txtr',
        'wraprocks.txtr',
        'wraprocks_md1.txtr',
        'wraprocks_sm1.txtr',
        'wraprocks_lg1.txtr',
        'wraprocks_lg2.txtr',
        'wraprocks_lg.txtr',
        'lichen6C.txtr',
        'lichen7C.txtr',
        'lichen5I.txtr',
        'lichen5C.txtr',
        'birdbath.txtr',
        'tunnel_metal.txtr',
        'tunnel_metal2.txtr',
        'generic_metal.txtr',
        'e_vineblend03c.txtr',
        'lockpillar01C.txtr',
        'flatrock.txtr',
        'tableC.txtr',
        'cliffer.txtr',
        'cliffer2.txtr',
        'chainsC.txtr',
        'component_large.txtr',
        'grnd1C.txtr',
        'grnd2C.txtr',
        'rippageC.txtr',
        'mothtopC.txtr',
        'mothhighC.txtr',
        'e_mothmetal4c.txtr',
        'e_slab01C.txtr',
        'cliff_cube_1C.txtr',
        'cliff_cube_1I.txtr',
        'cliff_cube_2C.txtr',
        'iconssm2.txtr',
        'back_guard.txtr',
        'metal128_C.txtr',
        'mothroundrt1.txtr',
        'blackphazonR.txtr',
        'statuereflect.txtr',
        'statueincand_1.txtr',
        'spmonitor_balony72.txtr',
        'infect3_C.txtr',
        'infect2_C.txtr',
        'infect_C.txtr',
        'hammerR.txtr',
        'demo.txtr',
        'demo_I.txtr',
        'free1C.txtr',
        'free2C.txtr',
        'free4C.txtr',
        'upwall01C.txtr',
        'e_vinepoddC.txtr',
        'ric_trim.txtr',
        '_ricplate4.txtr',
        'tobath_2.txtr',
        'tobath_1.txtr',
        'tobath.txtr',
        'wall0design.txtr',
        'wall0design1.txtr',
        'wall0design2.txtr',
        'wall0design3.txtr',
        '_ricplate2.txtr',
        'rock_layerlakes_1C.txtr',
        'cap_texC.txtr',
        '12es01C.txtr',
        '12es01I.txtr',
        '11f11bnew1C.txtr',
        'f_furnace2C.txtr',
        'f_furnace3C.txtr',
        'f_furnace4C.txtr',
        'f_furnace6C.txtr',
        'f_furnace9C.txtr',
        'f_hell2C.txtr',
        'ry_plant_c.txtr',
        'ry_plant.txtr',
        'merge_ry_plant_c!ry_plant_A.txtr',
        'merge_ry_plant_c!ry_plant_T.txtr',
    ])

    for key in res_dict:
        if (deep_search
                and (res_dict[key].endswith('cmdl') or res_dict[key].endswith('ani'))
                and (cooked_i := res_dict[key].find('/cooked/')) != -1
        ):
            tex_folders.add(res_dict[key][:cooked_i] + '/sourceimages')
        if res_dict[key].endswith('txtr'):
            tex_folder, tex_name = os.path.split(res_dict[key])
            if 'lightmap' in tex_name:
                if '$/Worlds/' in tex_folder:
                    tex_folders.add(os.path.split(tex_folder)[0] + '/sourceimages')
            else:
                tex_folders.add(tex_folder)
                if tex_folder.lower().startswith('$/worlds') and tex_folder.lower().endswith('common_textures'):
                    for suf in ['/Work/', '/Working/']:
                        tex_folders.add(tex_folder + suf + 'Ryan')
                        tex_folders.add(tex_folder + suf + 'Teague')
                        tex_folders.add(tex_folder + suf + 'Alejandro')
                        tex_folders.add(tex_folder + suf + 'Luis')
                        tex_folders.add(tex_folder + suf + 'Danny')
                        tex_folders.add(tex_folder + suf + 'Daniel')
                        tex_folders.add(tex_folder + suf + 'Dan')
                        tex_folders.add(tex_folder + suf + 'Benjamin')
                        tex_folders.add(tex_folder + suf + 'Ben')
                        tex_folders.add(tex_folder + suf + 'Chuck')
                        tex_folders.add(tex_folder + suf + 'Don')
                        tex_folders.add(tex_folder + suf + 'Beth')
                        tex_folders.add(tex_folder + suf + 'Lee')
                        tex_folders.add(tex_folder + suf + 'Elben')
                        tex_folders.add(tex_folder + suf + 'Chris')
                        tex_folders.add(tex_folder + suf + 'Nicholas')
                        tex_folders.add(tex_folder + suf + 'Nick')
                        tex_folders.add(tex_folder + suf + 'Todd')
                tex_names.add(tex_name)
                tex_names.add(tex_name.lstrip('_0123456789'))

                if tex_name[-6].lower() in ('c', 'i', *string.digits):
                    variants = set()
                    if tex_name[-6].lower() in ('c', 'i',):
                        variants.add(res_dict[key][:-6] + 'I' + res_dict[key][-5:])
                        variants.add(res_dict[key][:-6] + 'C' + res_dict[key][-5:])
                        variants.add(res_dict[key][:-6] + 'R' + res_dict[key][-5:])
                        if tex_name[-7].isdigit():
                            variants.update([res_dict[key][:-7] + n + res_dict[key][-6:] for n in string.digits])
                            variants.add(res_dict[key][:-7] + res_dict[key][-6:])
                    elif tex_name[-6].isdigit():
                        variants.update([res_dict[key][:-6] + n + res_dict[key][-5:] for n in string.digits])
                        variants.add(res_dict[key][:-6] + res_dict[key][-5:])
                    for tex in sorted(variants):
                        full_hash = utils.crc32.crc32(tex.lower())
                        if full_hash in res_dict:
                            commit = True  # r'/RuinWorld/' in folder
                            match_type = update_if_matched(tex, '.txtr!!', res_dict, commit)
                            if match_type == MatchType.NewMatch and commit:
                                matched += 1

                if deep_search:
                    alpha_num = set()
                    alpha_num.update(['a', 'b', 'c', 'd'])
                    for i in range(10):
                        for x in ['', 'a', 'b', 'c', 'd']:
                            alpha_num.add(f'{i}{x}')

                    tex_names.add('r1_c_' + tex_name)
                    tex_names.add(tex_name[:-5] + 'copy.txtr')
                    tex_names.add(tex_name[:-5] + '64.txtr')
                    tex_names.add(tex_name[:-5] + '128.txtr')
                    tex_names.add(tex_name[:-5] + '256.txtr')
                    tex_names.add(tex_name[:-5] + 'small.txtr')
                    tex_names.add(tex_name[:-5] + '_small.txtr')
                    tex_names.add(tex_name[:-5] + 'half.txtr')
                    tex_names.add(tex_name[:-5] + '_half.txtr')
                    tex_names.add(tex_name[:-5] + 'r.txtr')
                    if  0 < tex_name.find('_') < 3:
                        tex_names.add(tex_name[tex_name.find('_') + 1:])
                    if tex_name[-6].isdigit():
                        tex_names.update([tex_name[:-6] + n + '.txtr' for n in alpha_num])
                        tex_names.add(tex_name[:-6] + '.txtr')
                    if tex_name[-7].isdigit() and tex_name[-6].lower() in ('c', 'i'):
                        tex_names.update([tex_name[:-7] + n + tex_name[-6:] for n in alpha_num])
                        tex_names.add(tex_name[:-7] + tex_name[-6:])
                    if tex_name.lower().endswith('i.txtr'):
                        tex_names.add(tex_name[:-6] + 'C.txtr')
                        tex_names.add(tex_name[:-6] + '.txtr')
                    elif tex_name.lower().endswith('c.txtr'):
                        tex_names.add(tex_name[:-6] + 'I.txtr')
                        tex_names.add(tex_name[:-6] + '_I.txtr')
                        tex_names.add(tex_name[:-6] + '_r.txtr')
                        tex_names.add(tex_name[:-6] + '_incan.txtr')
                        tex_names.add(tex_name[:-6] + '_reflectivity.txtr')
                        tex_names.add(tex_name[:-6] + '_reflected.txtr')
                        tex_names.add(tex_name[:-6] + 'smallC.txtr')
                        tex_names.update([tex_name[:-6] + n + 'C.txtr' for n in alpha_num])
                        tex_names.update([tex_name[:-6] + '0' + n + 'C.txtr' for n in alpha_num])
                    else:
                        tex_names.add(tex_name[:-5] + 'I.txtr')
                        tex_names.add(tex_name[:-5] + '_I.txtr')
                        tex_names.add(tex_name[:-5] + '_r.txtr')
                        tex_names.add(tex_name[:-5] + '_incan.txtr')
                        tex_names.add(tex_name[:-5] + 'incan.txtr')
                        tex_names.add(tex_name[:-5] + 'inc.txtr')
                        tex_names.add(tex_name[:-5] + '_reflectivity.txtr')
                        tex_names.add(tex_name[:-5] + '_reflected.txtr')
                        tex_names.update([tex_name[:-5] + n + 'C.txtr' for n in alpha_num])
                        tex_names.update([tex_name[:-5] + n + '.txtr' for n in alpha_num])
                        tex_names.update([tex_name[:-5] + '0' + n + 'C.txtr' for n in alpha_num])

    sorted_tex_names = sorted(tex_names)
    for folder in sorted(tex_folders):
        folder_hash = utils.crc32.crc32(folder.lower() + '/')
        for tex in sorted_tex_names:
            full_hash = utils.crc32.crc32(tex.lower(), folder_hash)
            if full_hash in res_dict:
                commit = False #r'/RuinWorld/' in folder
                match_type = update_if_matched(f'{folder}/{tex}', '.txtr!!', res_dict, commit)
                if match_type == MatchType.NewMatch and commit:
                    matched += 1

    return matched
