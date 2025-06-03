# Metroid Prime dehashing scripts
![MP1 badge](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/Bearborg/ee95a1c1692c93f03ccf1fc684583c7a/raw/mp1_progress.json)
![MP2 badge](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/Bearborg/ee95a1c1692c93f03ccf1fc684583c7a/raw/mp2_progress.json)
![All hashes badge](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/Bearborg/ee95a1c1692c93f03ccf1fc684583c7a/raw/all_progress.json)

This is a collection of scripts and resources I've used while attempting to match the filename hashes found in the PAK
files of Metroid Prime 1 and 2.

Since CRC32 hashes are extremely prone to false positives, there isn't a simple brute forcer that can correctly
generate every hash; instead, this repo includes a variety of different tools which can be useful in finding certain
types of matches. 

Additionally, `mock_tree.py` contains functionality for mapping extracted [HECL](https://github.com/AxioDL/hecl) files to their original filepaths using
Windows shortcuts, essentially creating a browseable version of Metroid Prime's original asset tree.

## Setup
I recommend running these scripts using [PyCharm](https://www.jetbrains.com/pycharm/), and querying the included SQLite
DB using [DB Browser for SQLite](https://sqlitebrowser.org/). 

### Dependencies
* Python 3.x, ideally 3.11 or greater (for TOML config file parsing). Versions <3.11 will still work for most scripts in
this repo, but will gracefully error out of `mock_tree.py` code.

The following external libraries are also required:
* [z3-solver](https://pypi.org/project/z3-solver/)
* [PyYAML](https://pypi.org/project/PyYAML/)
* [pywin32](https://pypi.org/project/pywin32/)
* [winshell](https://pypi.org/project/winshell/)

To install all dependencies, you can use this command: `pip install z3-solver<4.14 pyyaml pywin32 winshell`

> [!NOTE]
> At time of writing, I've encountered significant performance regressions with `z3-solver` in versions 4.14.0.0 and
later. For this reason I recommend using build 4.13.4.0 when running the `decrc32.py` script.

## Credits
* Thanks to MrCheeze for [his work on matching Dread's hashes](https://github.com/MrCheeze/dread-tools/), which was very 
  helpful as a reference.
* Huge thanks to the [Metaforce](https://github.com/AxioDL/metaforce/) team, and the rest of the Metroid Prime Modding
  Discord.

