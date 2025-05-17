import os
from sqlite3 import Connection
from typing import Dict

from utils.crc32 import crc32
from extrapolating.update_if_matched import update_if_matched, MatchType


def guess_scan_images(res_dict, connection: Connection):
    """
    Attempts to match scan images by testing several known suffix combinations against variations of the scan's
    filename. This function is disabled by default, since it tests a large number of variations and is consequently very
    slow.

    If no match is found for a texture, it is still renamed to a non-matching filename in a subfolder of the scan file,
    for later investigation.

    :param res_dict: A dict of integer hashes to string filenames. Non-matching filenames should be suffixed with "!!".
    :param connection: Opened connection to mp_resources.db
    :return: Number of newly-added filename matches, as an int.
    """
    print("Checking scan images...")
    matched = 0

    narrow_textures: Dict[int, str] = {}

    scan_results = connection.execute("select ap.hash, group_concat(ar.target, ',') from asset_paths ap "
                                        "inner join asset_references ar on ap.hash = ar.source "
                                        "inner join asset_paths ap2 on ap2.hash = ar.target "
                                        "where ap.path like '%.scan' "
                                            "and ar.game = 'MP1/1.00' "
                                            "and ap.path_matches = 1 "
                                            "and ap2.path like '%.txtr' "
                                        "group by ar.source").fetchall()
    scans = {int(res[0], 16): [int(n, 16) for n in res[1].split(',')] for res in scan_results}

    for key in res_dict:
        if key in scans:
            textures = scans[key]
            textures = list(filter(lambda texture: res_dict[texture].endswith('!!'), textures))
            if len(textures) == 0:
                continue

            filepath, filename = os.path.split(res_dict[key])
            filename_candidates = {
                filename[:-5],
                ' '.join(filename[:-5].split(' ')[-1:]),
                ' '.join(filename[:-5].split(' ')[-2:]),
                ' '.join(filename[:-5].split(' ')[-3:]),
                ' '.join(filename[:-5].split(' ')[:1]),
                ' '.join(filename[:-5].split(' ')[:2]),
                ' '.join(filename[:-5].split(' ')[:3]),
            }
            temp_candidates = set()
            for item in filename_candidates:
                temp_candidates.update({
                    item + ' top',
                    item + ' up',
                    item + ' front',
                    item + ' frontL',
                    item + ' frontR',
                    item + ' side',
                    item + ' bottom',
                    item + ' right',
                    item + ' left',
                    item + ' back',
                    item + ' rear',
                    item + ' under',
                    item + ' persp',
                    item + ' perspective',
                    item + ' head',
                    item + ' face',
                    item + ' arm',
                    item + ' xray',
                })
            filename_candidates.update(temp_candidates)
            temp_candidates = set()
            for item in filename_candidates:
                temp_candidates.update({
                    item + ' 1',
                    item + ' one',
                    item + ' 2',
                    item + ' two',
                    item + ' 3',
                    item + ' three',
                    item + ' 4',
                    item + ' four',
                    item + ' L',
                    item + ' left',
                    item + ' R',
                    item + ' right',
                    item + ' 1L',
                    item + ' 2L',
                    item + ' 2La',
                    item + ' 2Lb',
                    item + ' 3L',
                    item + ' 4L',
                    item + ' half 4L',
                    item + ' 4La',
                    item + ' 4Lb',
                    item + ' 4L2',
                    item + ' 1R',
                    item + ' 2R',
                    item + ' 2Ra',
                    item + ' 2Rb',
                    item + ' 3R',
                    item + ' 4R',
                    item + ' half 4R',
                    item + ' 4Ra',
                    item + ' 4Rb',
                    item + ' 4R2',
                    item + ' LR',
                    item + ' quad',
                    item + ' quad 1',
                    item + ' quad 2',
                    item + ' bi',
                    item + ' bi 1',
                    item + ' bi 2',
                })
            filename_candidates.update(temp_candidates)
            temp_candidates = set()
            for candidate in filename_candidates:
                temp_candidates.update([candidate.replace(" ", "_"), candidate.replace(" ", "")])
            filename_candidates.update(temp_candidates)
            new_paths = set()
            for candidate in filename_candidates:
                new_paths.update({
                f'{filepath}/sourceimages/{candidate}.txtr',
                f'{filepath[:filepath.rfind("/")]}/sourceimages/{candidate}.txtr',
                f'{filepath[:filepath.rfind("/")]}/sourceimages/{candidate}.txtr',
                f'$/ScannableObjects/Creatures/sourceimages/{candidate}.txtr',
                f'$/ScannableObjects/Intro_World/sourceimages/{candidate}.txtr',
                f'$/ScannableObjects/Chozo_Ruins/sourceimages/{candidate}.txtr',
                f'$/ScannableObjects/Ice_World/sourceimages/{candidate}.txtr',
                f'$/ScannableObjects/Overworld/sourceimages/{candidate}.txtr',
                f'$/ScannableObjects/Mines/sourceimages/{candidate}.txtr',
                f'$/ScannableObjects/Lava_World/sourceimages/{candidate}.txtr',
                f'$/ScannableObjects/Crater/sourceimages/{candidate}.txtr',
                f'$/ScannableObjects/Tests/sourceimages/{candidate}.txtr',
                f'$/ScannableObjects/Game Mechanics/sourceimages/{candidate}.txtr',
            })
            for new_path in new_paths:
                if crc32(new_path.lower()) in textures:
                    match_type = update_if_matched(new_path,'.txtr!!', res_dict)
                    if match_type == MatchType.NewMatch:
                        matched += 1

            for tex in textures:
                narrow_textures[tex] = f'{filepath}/sourceimages/{filename[:-5]} {tex:08X}.txtr'
    for tex in narrow_textures:
        if res_dict[tex].endswith('!!') and res_dict[tex] != (narrow_textures[tex] + '!!'):
            print(f'{res_dict[tex]} -> {narrow_textures[tex]}')
            res_dict[tex] = narrow_textures[tex] + '!!'

    return matched