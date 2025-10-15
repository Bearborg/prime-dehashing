"""
Narrows down potential filenames by finding cases where the same file was copied into multiple locations.
"""
from typing import List
import crc32_solver
import itertools
from dataclasses import dataclass

@dataclass
class Duplicate:
    goal: int
    paths: List[str]
    suffixes: List[str]


def locate_duplicates(dupes: List[Duplicate], max_depth: int = 50, min_depth: int = 1, timeout=7):
    """
    Given a list of identical assets with differing hashes, attempt to find a filename that can be matched against a
    pair of files. This is achieved by iterating through all possible pairs of files, and all possible prefixes for each
    file, and then performing brute force matching to find a string that matches the pair. If any match is found, it is
    extremely probable to be the same length as the original filename, which enables more targeted matching attempts
    using other tools.
    :param dupes: List of identical assets with different hashes.
    :param max_depth: Maximum number of characters to use in an attempted match.
    :param min_depth: Minimum number of characters to use in an attempted match.
    :param timeout: How long to run the brute forcer for each attempted match (in seconds).
    :return: None
    """
    combos = list(itertools.combinations(dupes, 2))
    for index, (dupe1, dupe2) in enumerate(combos):
        print(f'Comparing {dupe1.goal:08x} and {dupe2.goal:08x} ({index/len(combos):.2%})')

        for path1, path2 in itertools.product(dupe1.paths, dupe2.paths):
            for suf1, suf2 in itertools.product(dupe1.suffixes, dupe2.suffixes):
                if path1 == path2 and suf1 == suf2:
                    continue

                for i in range(min_depth, max_depth + 1):
                    crc32_solver.solve_pair(
                        goalchecksum1=dupe1.goal,
                        prefixstr1=path1,
                        suffixstr1=suf1,
                        goalchecksum2=dupe2.goal,
                        prefixstr2=path2,
                        suffixstr2=suf2,
                        maxunklen=i,
                        minunklen=i,
                        timeout=timeout if i > 6 else None,
                        #ctx=Context()
                    )

if __name__ == '__main__':
    input_dupes = [
        Duplicate(
            goal=0x7B2B1BD4,
            paths=[
                '$/Worlds/RuinWorld/8_courtyard/sourceimages/'.lower(),
            ],
            suffixes=[
                '.txtr'.lower()
            ]
        ),
        Duplicate(
            goal=0x5E8B1C88,
            paths=[
                '$/Worlds/RuinWorld/10_coreentrance/sourceimages/'.lower(),
                '$/Worlds/RuinWorld/common_textures/'.lower(),
                '$/Worlds/RuinWorld/common_textures/stone/'.lower(),
            ],
            suffixes=[
                '.txtr'.lower()
            ]
        ),
        Duplicate(
            goal=0x5E8B1C88,
            paths=[
                '$/Worlds/RuinWorld/11_wateryhall/sourceimages/'.lower(),
                '$/Worlds/RuinWorld/5_bathhall/sourceimages/'.lower(),
                '$/Worlds/RuinWorld/common_textures/'.lower(),
                '$/Worlds/RuinWorld/common_textures/stone/'.lower(),
            ],
            suffixes=[
                '.txtr'.lower()
            ]
        ),
    ]
    locate_duplicates(input_dupes, 20)