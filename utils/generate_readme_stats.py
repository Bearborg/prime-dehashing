"""
Sets environment values for use in generating GitHub readme badges.
"""
import os
import sqlite3
from sys import stdout

env_file = os.getenv('GITHUB_ENV')

with open(env_file, "a") if env_file else stdout as env_out:
    asset_db_path = r'database/mp_resources.db'
    with sqlite3.connect(asset_db_path) as connection:
        mp1_total, mp1_matched = connection.execute(
            r"with mp1_matches as (select ap.hash, ap.path_matches from asset_paths ap "
            "inner join asset_usages us on ap.hash = us.hash "
            "group by ap.hash "
            "having SUM(us.game = 'MP1/1.00') > 0) "
            "select count(hash), sum(path_matches) from mp1_matches"
        ).fetchone()
        print(f'MP1_MATCHED_PCT={100 * mp1_matched / mp1_total:05.2f}', file=env_out)
        mp2_total, mp2_matched = connection.execute(
            r"with mp2_matches as (select ap.hash, ap.path_matches from asset_paths ap "
            "inner join asset_usages us on ap.hash = us.hash "
            "group by ap.hash "
            "having SUM(us.game = 'MP2/NTSC') > 0) "
            "select count(hash), sum(path_matches) from mp2_matches"
        ).fetchone()
        print(f'MP2_MATCHED_PCT={100 * mp2_matched / mp2_total:05.2f}', file=env_out)
        all_total, all_matched = connection.execute(
            "select count(hash), sum(path_matches) from asset_paths"
        ).fetchone()
        print(f'ALL_MATCHED_PCT={100 * all_matched / all_total:05.2f}', file=env_out)