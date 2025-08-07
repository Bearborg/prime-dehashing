"""
Sets environment values for use in generating GitHub readme badges.
"""
import os
import sqlite3
from sys import stdout
from fractions import Fraction

out_folder = 'output_gists'

def total_matched_overall(resource_db_connection: sqlite3.Connection):
    matched, total = resource_db_connection.execute(
        "select sum(path_matches), count(hash) from asset_paths"
    ).fetchone()
    return matched, total

def total_matched_per_game(resource_db_connection: sqlite3.Connection, game: str, pak: str = None):
    matched, total = resource_db_connection.execute(
        "with matches as (select ap.hash, ap.path_matches from asset_paths ap "
        "inner join asset_usages us on ap.hash = us.hash "
        "where iif(:pak is not null, us.game = :game and us.pak = :pak, 1)"
        "group by ap.hash "
        "having SUM(us.game = :game) > 0) "
        "select sum(path_matches), count(hash) from matches",
        {"game": game, "pak": pak}
    ).fetchone()
    return matched, total

def detailed_breakdown(resource_db_connection: sqlite3.Connection, game: str, pak: str = None):
    result = resource_db_connection.execute(
        "with const as (select ? as game, ? as pak), "
        "meta as ( "
            "select count(distinct(hash)) as total_assets from const, asset_usages us "
            "where us.game = const.game "
            "and iif(const.pak is not null, us.pak = const.pak COLLATE NOCASE, 1) "
        "), "
        "match_groups as ( "
            "select au.type, ap.path_matches as matches, count(distinct au.hash) as hits "
            "from const, asset_paths ap "
            "inner join asset_usages au on ap.hash = au.hash "
            "where au.game = const.game "
            "and iif(const.pak is not null, au.pak = const.pak COLLATE NOCASE, 1) "
            "group by au.type, ap.path_matches "
        ") "
        "select coalesce(unmatched.type, matched.type) as type, "
        "coalesce(matched.hits, 0) as matched, "
        "coalesce(matched.hits, 0) + coalesce(unmatched.hits, 0) as all_assets, "
        "round((100.00 * coalesce(matched.hits, 0)) / max((coalesce(matched.hits, 0) + coalesce(unmatched.hits, 0)), 1), 2) as pct_matched "
        ",round(100.00 * (coalesce(matched.hits, 0) + coalesce(unmatched.hits, 0)) / meta.total_assets, 2) as pct_of_total "
        "from ( "
            "select 2 as order_num, type, hits from match_groups where matches = 0 "
            "union all "
            "select 1 as order_num, 'Total' as type, sum(hits) as hits from match_groups where matches = 0 "
        ") as unmatched "
        "full outer join ( "
            "select 2 as order_num, type, hits from match_groups where matches = 1 "
            "union all "
            "select 1 as order_num, 'Total' as type, sum(hits) as hits from match_groups where matches = 1 "
        ") as matched on matched.type = unmatched.type "
        ", meta "
        "order by coalesce(unmatched.order_num, matched.order_num), coalesce(unmatched.type, matched.type)",
        (game,pak)
    ).fetchall()

    table  = f'|Type|Matched|Total|Percent matched|Proportion of {"game" if pak is None else "pak"}|\n'
    table += f'|----|-------|-----|---------------|----------------|\n'
    for line in result:
        (res_type, matched, total, pct_matched, pct_of_total) = line
        table += f'|{res_type}|{matched}|{total}|{pct_matched}%|{pct_of_total}%|\n'
    return table

def save_as_markdown(filename: str, title_heading: str, body: str):
    with open(f'{out_folder}/{filename}.md', 'w') as out:
        out.write(f'# {title_heading}\n\n')
        out.write(body)

if __name__ == '__main__':
    env_file = os.getenv('GITHUB_ENV')

    with open(env_file, "a") if env_file else stdout as env_out:
        asset_db_path = r'database/mp_resources.db'
        with sqlite3.connect(asset_db_path) as connection:
            mp1_stats = Fraction(*total_matched_per_game(connection, 'MP1/1.00'))
            print(f'MP1_MATCHED_PCT={100 * mp1_stats:05.2f}', file=env_out)
            mp2_stats = Fraction(*total_matched_per_game(connection, 'MP2/NTSC'))
            print(f'MP2_MATCHED_PCT={100 * mp2_stats:05.2f}', file=env_out)
            all_stats = Fraction(*total_matched_overall(connection))
            print(f'ALL_MATCHED_PCT={100 * all_stats:05.2f}', file=env_out)
            os.makedirs(out_folder, exist_ok=True)
            mp1_breakdown = detailed_breakdown(connection, 'MP1/1.00')
            save_as_markdown('mp1_breakdown', 'Metroid Prime 1 (NTSC 0-00)', mp1_breakdown)
            mp2_breakdown = detailed_breakdown(connection, 'MP2/NTSC')
            save_as_markdown('mp2_breakdown', 'Metroid Prime 2: Echoes (NTSC)', mp2_breakdown)