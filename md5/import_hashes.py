import invoke
import os
import shutil
import sqlite3
from typing import List, Tuple, Dict


asset_db_path = r'F:\Documents\Code\prime-dehashing\md5\md5_resources.db'
connection = sqlite3.connect(asset_db_path)

dolphin_tool = r'F:\Games\Emulation\Dolphin\DolphinTool.exe'
paktool = r'H:\Backup from Previous PC\Users\Wyatt\Documents\My Games\Emulation\Tools\Paktool\PakTool.exe'
images = {
    'MP3P': r'E:\Emulated Games\GCN\Metroid Prime 3 Demo\Metroid Prime 3 Beta.gcm',
    'MP3/NTSC': r'E:\Emulated Games\Wii\Metroid Prime 3; Corruption\Metroid Prime 3 (NTSC).wbfs',
    'MP3/PAL': r'E:\Emulated Games\Wii\Metroid Prime 3; Corruption\Metroid Prime 3 (PAL).iso',
    'MP3/Japan': r'E:\Emulated Games\Wii\Metroid Prime 3; Corruption\Metroid Prime 3 (Japan).wbfs',
    'MP3/TrilogyNTSC': r'E:\Emulated Games\Wii\Metroid Prime Trilogy\Metroid Prime Trilogy (NTSC).wbfs',
    'MP3/TrilogyPAL': r'E:\Emulated Games\Wii\Metroid Prime Trilogy\Metroid Prime Trilogy (PAL).iso',
    'TrilogyFE/NTSC': r'E:\Emulated Games\Wii\Metroid Prime Trilogy\Metroid Prime Trilogy (NTSC).wbfs',
    'TrilogyFE/PAL': r'E:\Emulated Games\Wii\Metroid Prime Trilogy\Metroid Prime Trilogy (PAL).iso',
    'DKCR/NTSC': r'E:\Emulated Games\Wii\Donkey Kong Country Returns\Donkey Kong Country Returns.iso',
}

scratch_folder = r'F:\Documents\Code\msr-dehashing\scratch'

def extract_file(filename: str, single_file: str, out_folder: str) -> None:
    invoke.run(f'"{dolphin_tool}" extract -g -i "{filename}" -s "{single_file}" -o "{out_folder}"', hide=True)

def list_files(filename: str) -> List[str]:
    tree = invoke.run(f'"{dolphin_tool}" extract -g -i "{filename}" -l', hide=True)
    return tree.stdout.split()

def dump_assets(filename: str) -> bool:
    out = invoke.run(f'"{paktool}" -d "{filename}"', hide=True)
    return not 'Pak contains 0 filenames' in out.stdout

def read_assets(game_id: str, pak_path:str, filename: str):
    usages: Dict[str, Tuple[str, str, str, str, str]] = {}

    for line in open(filename, 'r'):
        if len(line.strip()) > 0:
            assert len(line.strip()) == 21 or (len(line.strip()) > 21 and line[21] == ' '), '32-bit IDs are not supported'
            asset = line[:16]
            asset_type = line[17:21]
            name = None
            if ' ' in line:
                name = line[22:].strip()
            if asset not in usages:
                usages[asset] = (asset, game_id, pak_path, asset_type, name)

    cur = connection.cursor()
    cur.executemany('INSERT INTO assets VALUES(?) ON CONFLICT DO NOTHING',[(x,) for x in usages.keys()])
    cur.executemany('INSERT INTO asset_usages(hash, game, pak, type, name) VALUES(?, ?, ?, ?, ?)',
                    usages.values())
    cur.close()
    connection.commit()


def clean_scratch_folder() -> None:
    for root, dirs, files in os.walk(scratch_folder):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))

def ingest_pak(game_id: str, game_path: str, pak_path: str) -> None:
    print(f'Reading pak {game_id}/{pak_path}...')
    clean_scratch_folder()
    extract_file(game_path, pak_path, scratch_folder)
    extracted_path = os.path.join(scratch_folder, 'files', pak_path)
    if not os.path.isfile(extracted_path):
        extracted_path = os.path.join(scratch_folder, 'DATA', 'files', pak_path)
    assert os.path.isfile(extracted_path), "Could not find extracted pak"
    if dump_assets(os.path.abspath(extracted_path)):
        read_assets(game_id, pak_path, os.path.abspath(extracted_path[:-4] + '-pak.txt'))
    clean_scratch_folder()

def ingest_game(game_id: str) -> None:
    for file in list_files(images[game_id]):
        if file.lower().endswith('.pak'):
            if '/' in file:   # Only Trilogy and DKCR put paks deeper than root
                if game_id.lower()[:3] == file.lower()[:3] or 'DKCR' in game_id or (file.lower()[:3] == 'fe/' and game_id.startswith('Trilogy')):
                    ingest_pak(game_id, images[game_id], file)
            else:
                ingest_pak(game_id, images[game_id], file)

def setup_db():
    cur = connection.cursor()
    cur.execute('CREATE TABLE assets(hash TEXT PRIMARY KEY)')
    cur.execute('CREATE TABLE asset_usages(id INTEGER PRIMARY KEY, hash TEXT, game TEXT, pak TEXT, type TEXT, name TEXT, FOREIGN KEY (hash) REFERENCES assets(hash))')
    cur.execute('CREATE TABLE asset_paths(hash TEXT PRIMARY KEY, path TEXT NOT NULL,  FOREIGN KEY (hash) REFERENCES assets(hash))')
    cur.close()
    connection.commit()

def main():
    # setup_db()
    for k in ['TrilogyFE/NTSC', 'TrilogyFE/PAL']:
        ingest_game(k)

if __name__ == '__main__':
    main()