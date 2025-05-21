import os
from typing import Set
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
        '$/AnimatedObjects/General/pickups/powerbomb/sourceimages'
    ])
    tex_names: Set[str] = set()
    tex_names.update([
        'ballight3C', 'ballight3I', 'jomama' 'jomama1'
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
                        tex_names.add(tex_name[:-6] + '_incan.txtr')
                        tex_names.add(tex_name[:-6] + '_reflectivity.txtr')
                        tex_names.add(tex_name[:-6] + '_reflected.txtr')
                        tex_names.update([tex_name[:-6] + n + 'C.txtr' for n in alpha_num])
                        tex_names.update([tex_name[:-6] + '0' + n + 'C.txtr' for n in alpha_num])
                    else:
                        tex_names.add(tex_name[:-5] + 'I.txtr')
                        tex_names.add(tex_name[:-5] + '_I.txtr')
                        tex_names.add(tex_name[:-5] + '_incan.txtr')
                        tex_names.add(tex_name[:-5] + '_reflectivity.txtr')
                        tex_names.add(tex_name[:-5] + '_reflected.txtr')
                        tex_names.update([tex_name[:-5] + n + 'C.txtr' for n in alpha_num])
                        tex_names.update([tex_name[:-5] + '0' + n + 'C.txtr' for n in alpha_num])

    for folder in tex_folders:
        for tex in tex_names:
            commit = False #r'/RuinWorld/' in folder
            match_type = update_if_matched(f'{folder}/{tex}', '.txtr!!', res_dict, commit)
            if match_type == MatchType.NewMatch and commit:
                matched += 1

    return matched
