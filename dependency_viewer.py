"""
Recursively prints all dependencies for a hash, highlighting those with unmatched names.
"""

import sqlite3
asset_db_path = r'./database/mp_resources.db'
connection = sqlite3.connect(asset_db_path)
game = 'MP1/1.00'
start_red = '\033[91m'
end_color = '\033[0m'

res_cache = set()

def color(path: str, hash_str: str):
    if path.endswith('!!'):
        return f'{start_red}{path}: {hash_str}{end_color}'
    else:
        return f'{path}: {hash_str}'

def print_self(asset_id:str, level = 0):
    result_row = connection.execute(
        "select ap.path || IIF(ap.path_matches, '', '!!') as path, ap.hash, us.type "
        "from asset_paths ap "
        "inner join asset_usages us on us.hash = ap.hash "
        "where ap.hash = ? COLLATE NOCASE "
        "and us.game = ?",
        (asset_id, game)
    ).fetchone()
    print(f'{"  " * level}{color(result_row[0], result_row[1])}')

def recurse_deps(asset_id: str, level = 1):
    resource_results = connection.execute(
        "select ap2.path || IIF(ap2.path_matches, '', '!!') as path, ap2.hash, us.type "
        "from asset_paths ap "
        "inner join asset_references ar on ar.source = ap.hash "
        "inner join asset_usages us on us.hash = ar.target "
        "inner join asset_paths ap2 on ap2.hash = ar.target "
        "where ap.hash = ? COLLATE NOCASE "
        "and us.game = ? "
        "group by ap2.hash "
        "order by us.type, ap2.path",
        (asset_id, game)
    ).fetchall()
    for row in resource_results:
        if row[1] not in res_cache:
            print(f'{"  " * level}{color(row[0], row[1])}')
            res_cache.add(row[1])
            recurse_deps(row[1], level + 1)
        else:
            print(f'{"  " * level}Duplicate asset: {row[0].rstrip('!')}')


def show_all_deps(asset_id: str):
    print_self(asset_id)
    recurse_deps(asset_id)

if __name__ == '__main__':
    show_all_deps('144778B8')