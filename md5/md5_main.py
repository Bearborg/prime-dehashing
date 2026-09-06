import sqlite3
import json
from utils.md5 import retro_md5

# create json
# manual guesser

asset_db_path = r'F:\Documents\Code\prime-dehashing\md5\md5_resources.db'
resource_file = r'F:\Documents\Code\prime-dehashing\md5\md5_resources.json'

def check_manual_guesses(res_dict, guesses: list[str]):
    print("Checking manual guesses...")
    matched = 0
    start_green = '\033[92m'
    start_red = '\033[91m'
    end_color = '\033[0m'
    for path in guesses:
        path = path.lower()
        key = retro_md5(path)
        if key in res_dict and res_dict[key].endswith("!!"):
            if res_dict[key].endswith(path[path.rfind('.'):] + "!!"):
                print(f'{start_green}Match: {res_dict[key]} -> {path}{end_color}')
                res_dict[key] = path
                matched += 1
            else:
                print(f'{start_red}Type mismatch: {res_dict[key]} -x> {path}{end_color}')

    return matched


def main(guesses: list[str], read_from_json=False):
    connection = sqlite3.connect(asset_db_path)

    if read_from_json:
        resource_obj = json.load(open(resource_file, 'r'))
    else:
        resource_results = connection.execute(
            r"select path || IIF(path_matches, '', '!!') as path, hash from asset_paths order by path"
        ).fetchall()
        resource_obj = {res[0]: res[1] for res in resource_results}
    resource_dict: dict[int, str] = {}
    total = 0
    matched = 0

    for path in resource_obj:
        total += 1
        key = int(resource_obj[path], 16)
        path = path.rstrip('!')
        if retro_md5(path.lower()) == key:
            matched += 1
        else:
            path += '!!'
        resource_dict[key] = path

    matched += check_manual_guesses(resource_dict, guesses)

    sorted_paths: list[str] = sorted(resource_dict.values(), key=lambda x: x.casefold())
    printed_id_dict = {'{0:016x}'.format(x): resource_dict[x] for x in resource_dict}
    flipped_dict = {printed_id_dict[x]: x for x in printed_id_dict}
    sorted_dict = {x: flipped_dict[x] for x in sorted_paths}

    real_matched = len(list(filter(lambda x: not x.endswith('!!'), resource_dict.values())))
    if real_matched != matched:
        print(f"Incorrect match total: {real_matched} != {matched}")

    print("Updating output files...")
    json.dump(sorted_dict, open(resource_file, 'w'), indent=2)
    matched_paths_for_db = [
        (sorted_dict[asset_path], asset_path.rstrip('!'), not asset_path.endswith('!!')) for asset_path in sorted_dict
    ]
    print("Updating resource DB...")
    connection.executemany('INSERT INTO asset_paths VALUES(?, ?, ?) '
                           'ON CONFLICT DO UPDATE '
                           'SET path = excluded.path, path_matches = excluded.path_matches', matched_paths_for_db)
    connection.commit()
    connection.close()

    print(f'Overall progress: {real_matched}/{total} - {real_matched / total:.2%}')


if __name__ == '__main__':
    resources32 = r'F:\Documents\Code\prime-dehashing\output_json\mp_resource_names_confirmed.json'
    resource_obj_32 = json.load(open(resources32, 'r'))

    manual_guesses = [
        *resource_obj_32.keys()
    ]
    main(manual_guesses, False)