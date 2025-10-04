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
    suffix: str


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

        for path1 in dupe1.paths:
            for path2 in dupe2.paths:
                if path1 == path2 and dupe1.suffix == dupe2.suffix:
                    continue

                for i in range(min_depth, max_depth + 1):
                    crc32_solver.solve_pair(
                        goalchecksum1=dupe1.goal,
                        prefixstr1=path1,
                        suffixstr1=dupe1.suffix,
                        goalchecksum2=dupe2.goal,
                        prefixstr2=path2,
                        suffixstr2=dupe2.suffix,
                        maxunklen=i,
                        minunklen=i,
                        timeout=timeout if i > 6 else None,
                        #ctx=Context()
                    )

if __name__ == '__main__':
    input_dupes = [
        Duplicate(
            goal=0x903FB0D3,
            paths=[
                '$/Worlds/RuinWorld/common_textures/metal/'.lower(),
            ],
            suffix='.txtr'.lower()
        ),
        Duplicate(
            goal=0xF05CED73,
            paths=[
                '$/Worlds/IceWorld/11_ice_observatory/sourceimages/'.lower(),
                '$/Worlds/IceWorld/common_textures/'.lower(),
            ],
            suffix='.txtr'.lower()
        ),
    ]
    locate_duplicates(input_dupes, 20)