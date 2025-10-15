import os
import re
import json

from extrapolating.update_if_matched import update_if_matched
from utils.crc32 import crc32, remove_suffix
from typing import Dict

start_yellow = '\033[93m'
end_color = '\033[0m'

cache = set()
hash_cache = dict()
txtrs = set()
rev_match = dict()

def test_all_dirs(resource_dict: Dict[int, str], show_groups=False):
    """
    Exploits the properties of CRC hashes to efficiently test if any known partially-matched files can be fully matched
    by placing them in a known directory. Partially-matched names are derived by taking the current name of the file
    after the last '/', OR by taking the name after the first '@' (this is used as an override). Some basic
    substitutions are also performed for fuzzy matching, e.g. converting camelCase to snake_case.
    :param resource_dict: A dict of integer hashes to string filenames. Non-matching filenames should be suffixed with "!!".
    :param show_groups: When true, prints out a list of each instance where 2+ hashes appear to be located in the same
            directory (i.e. rewinding their filenames from their hashes produces the same value).
    :return: Number of newly-added filename matches, as an int.
    """
    print("Checking known directories...")
    matched = 0
    for file in resource_dict:
        if resource_dict[file].endswith('!!'):
            if '@' in resource_dict[file]:
                # "@" is the override character, so if it's present we always use the exact name after that point
                name = resource_dict[file]
                name = name[name.find('@') + 1:-2]
                rewound = remove_suffix(file, name.lower())
                hash_cache[rewound] = [name] + (hash_cache.get(rewound) or [])
                rev_match[rewound] = resource_dict[file][:resource_dict[file].find('@') + 1]
                if name.endswith('txtr'):
                    path, filename = os.path.split(resource_dict[file][:-2])
                    rewound = remove_suffix(file, filename.lower())
                    rev_match[rewound] = path + '/'
                    txtrs.add(filename)
                continue
            name = os.path.split(resource_dict[file][:-2])[1]
            rewound = remove_suffix(file, name.lower())
            hash_cache[rewound] = [name] + (hash_cache.get(rewound) or [])
            filename, ext = os.path.splitext(name)
            if filename.startswith('RS5_'):
                filename = filename[4:]
                rewound = remove_suffix(file, (filename + ext).lower())
                hash_cache[rewound] = [filename + ext] + (hash_cache.get(rewound) or [])
                # "RS5_" filenames have all spaces replaced with underscores, so try changing them all back
                filename = filename.replace('_', ' ')
                rewound = remove_suffix(file, (filename + ext).lower())
                hash_cache[rewound] = [filename + ext] + (hash_cache.get(rewound) or [])
                # Also try restoring the underscores, going from left to right
                while ' ' in filename:
                    filename = filename.replace(' ', '_', 1)
                    rewound = remove_suffix(file, (filename + ext).lower())
                    hash_cache[rewound] = [filename + ext] + (hash_cache.get(rewound) or [])
            if re.match(r'[A-Z]{4}_', filename):
                # Rename any file that starts with a fourCC, e.g. "TXTR_XRayPalette"
                filename = filename[5:]
                rewound = remove_suffix(file, (filename + ext).lower())
                hash_cache[rewound] = [filename + ext] + (hash_cache.get(rewound) or [])
            if re.match(r'.*_\d$', filename):
                # Remove suffixes like "_1" (PWE adds these to any files with identical names)
                filename = filename[:-2]
                rewound = remove_suffix(file, (filename + ext).lower())
                hash_cache[rewound] = [filename + ext] + (hash_cache.get(rewound) or [])
            if re.search(r"[a-z][A-Z]", filename) and not ext == '.ani':
                # convert camelCase to snake_case
                un_cameled_filename = re.sub(r"([a-z])([A-Z])", r"\1_\2", filename)
                rewound = remove_suffix(file, (un_cameled_filename + ext).lower())
                hash_cache[rewound] = [un_cameled_filename + ext] + (hash_cache.get(rewound) or [])
                un_cameled_filename = un_cameled_filename.replace('_', ' ')
                rewound = remove_suffix(file, (un_cameled_filename + ext).lower())
                hash_cache[rewound] = [un_cameled_filename + ext] + (hash_cache.get(rewound) or [])
            if ext == '.cmdl' or ext == '.acs':
                # try throwing "_bound" on the end of any ANCS/CMDL names
                filename = filename + '_bound'
                rewound = remove_suffix(file, (filename + ext).lower())
                hash_cache[rewound] = [filename + ext] + (hash_cache.get(rewound) or [])
        elif resource_dict[file].endswith('txtr') and not 'lightmap' in resource_dict[file]:
            # store all matched texture names to see if they're duplicated in a partially-matched folder
            filename = os.path.split(resource_dict[file])[1]
            txtrs.add(filename)
            if match := re.search(r'(_*[CcIiRr]\.txtr)$', filename):
                txtrs.add(filename[:-len(match[0])] + '.txtr')
                txtrs.add(filename[:-len(match[0])].rstrip('0123456789') + '.txtr')
                txtrs.add(filename[:-len(match[0])].rstrip('0123456789') + match[0])
    for file in resource_dict:
        if not resource_dict[file].endswith('!!') and not 'trilogy_rep' in resource_dict[file]:
            tril_name = resource_dict[file].replace('$/', '$/trilogy_rep/')
            if update_if_matched(tril_name, os.path.splitext(tril_name)[1] + '!!', resource_dict) == 1:
                matched += 1
            assert resource_dict[file].startswith('$/')
            path = resource_dict[file]
            while path != '$':
                # Iterate through path from right-to-left, trying each parent folder
                path = os.path.split(path)[0]
                if path not in cache:
                    cache.add(path)
                    crc = crc32(f'{path}/'.lower())
                    crc_rs5 = crc32(f'{path}/'.lower(), 0xab8aef08)
                    if crc in hash_cache:
                        for filename in set(hash_cache[crc]):
                            full = f'{path}/{filename}'
                            if update_if_matched(full, os.path.splitext(full)[1]+ '!!', resource_dict) == 1:
                                matched += 1
                    if crc_rs5 in hash_cache:
                        for filename in set(hash_cache[crc_rs5]):
                            full = f'{path}/{filename}'
                            trilogy_full = f'{path}/{filename}'.replace('$/', '$/trilogy_rep/')
                            if update_if_matched(full, os.path.splitext(filename)[1] + '!!', resource_dict):
                                matched += 1
                            if update_if_matched(trilogy_full, os.path.splitext(filename)[1] + '!!', resource_dict):
                                matched += 1

    unk_start = 'Unknown/'


    for key in hash_cache:
        if len(set(map(lambda x: os.path.splitext(re.sub(r'_lightmap\d+|_bound', '', x.lower()))[0], hash_cache[key]))) > 1:
            if key not in rev_match:
                rev_match[key] = unk_start
            if show_groups:
                print(sorted(set(hash_cache[key])))
    for key in rev_match:
        # Test if known texture names can be matched to the same directory as any partially-matched textures
        for txtr in txtrs:
            if (new_hash := crc32(txtr.lower(), key)) in resource_dict:
                old_name = resource_dict[new_hash]
                if old_name.endswith('txtr!!'):
                    if not (rev_match[key] == unk_start and txtr.lower() == os.path.split(old_name[:-2].lower())[1]):
                        new_name = rev_match[key] + txtr
                        if '@' not in old_name and old_name[:-2].lower() != new_name.lower():
                            print(f'{start_yellow}Partial match found, {new_hash:08x}: {new_name}{end_color}')
                            # resource_dict[new_hash] = new_name + '!!'
    return matched

if __name__ == '__main__':
    resource_file = r'../output_json/mp_resource_names.json'
    resource_obj = json.load(open(resource_file, 'r'))
    res_dict: Dict[int, str] = {int(resource_obj[path], 16): path for path in resource_obj}
    test_all_dirs(res_dict, True)