import os
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
        '$/Worlds/LavaWorld/common_textures'
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
        'kmnqvwa0vv2d4c.txtr', # mines greeble
        'kmnqvwa0vv2d4i.txtr',
        #'vvstsvlkdvqesjocc.txtr', # vine
        'sjxpzopaglatowroc.txtr', # vine
        'mnngoudvrzmtbtabc.txtr', # ridged brown metal
        'jxqyuxmaryziwtc.txtr', # mossy striated rock
        'jxqyuxmaryziwtcc.txtr', # mossy striated rock
        'jxqyuxmaryziwt.txtr', # mossy striated rock
        'gbliwebbaftxvqhnc.txtr', # rock mud blend
        'gbliwebbaftxvqhn.txtr', # rock mud blend
        'gbliwebbaftxvqhncc.txtr', # rock mud blend
        'f_balljrnb60hp38c.txtr', # mirror
        'nceotfbsbjzrntgmc.txtr', # tube
        'tuwugkdtofyzgpzdyfc.txtr', # ice wall section
        'nbbovbxpdktettc.txtr', # chozo text wall
        'yc2eut_h1sb4hc.txtr', # orange metal square
        'ms_morphballtubeC.txtr',
        'ms_morphballtube2C.txtr',
        'ms_morphballtubeI.txtr',
        'wall0alt2.txtr',
        'wall0alt2c.txtr',
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
        'archc.txtr',
        'mossrockdirt.txtr',
        'brockblendC.txtr',
        'brockblend.txtr',
        'platebracesC.txtr',
        'fountainnecc.txtr',
        'conc128C.txtr',
        'flo_R.txtr',
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
                tex_folders.add(os.path.split(tex_folder)[0] + '/sourceimages')
            else:
                tex_folders.add(tex_folder)
                tex_names.add(tex_name)
                tex_names.add(tex_name.lstrip('_0123456789'))
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
