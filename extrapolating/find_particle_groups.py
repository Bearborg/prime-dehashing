import os
import re
import json
import itertools
from typing import Set, Dict, List
import utils.crc32
from extrapolating.update_if_matched import update_if_matched, MatchType

def find_particle_groups(res_dict):
    """

    :param res_dict: A dict of integer hashes to string filenames. Non-matching filenames should be suffixed with "!!".
    """
    print("Identifying particle groups...")
    matched = 0

    part_names: Set[str] = set()
    part_names.update([
        'pollen.gpsm.part',
        'pollen1.gpsm.part',
        'int1.gpsm.part',
        'fa___2____xf.gpsm.part',
        'hblastsnow.gpsm.part',
    ])
    for key in res_dict:
        if res_dict[key][-4:] in ['part']:
            part_folder, part_name = os.path.split(res_dict[key])
            part_names.add(part_name)

    groups: Dict[int, List[str]] = dict()
    lowered_part_names = {n.lower() for n in filter(lambda p: p.endswith(".part"), part_names)}
    for key in res_dict:
        if res_dict[key].endswith('!!') and res_dict[key][-6:-2].lower() in ['part']:
            for name in lowered_part_names:
                rewound = utils.crc32.remove_suffix(key, name)
                groups[rewound] = (groups.get(rewound) or []) + [name]

    for key, group in groups.items():
        if len(group) > 1:
            group.sort()
            should_print = True
            # filter out groups with <3 characters difference, excluding outliers
            for sub_group in [group[1:], group[:-1]]:
                common_prefix = os.path.commonprefix(sub_group)
                if max([len(p) for p in sub_group]) - len(common_prefix) <= 3 + len('.gpsm.part'):
                    should_print = False
            if should_print:
                labeled_group = {f'{utils.crc32.crc32(p, key):08x}': p for p in group}
                print(f'Group: {labeled_group}')

    return matched

if __name__ == '__main__':
    resource_file = r'../output_json/mp_resource_names.json'
    resource_obj = json.load(open(resource_file, 'r'))
    resource_dict: Dict[int, str] = {int(resource_obj[path], 16): path for path in resource_obj}
    find_particle_groups(resource_dict)
