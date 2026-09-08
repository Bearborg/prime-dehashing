import string
from utils.md5 import retro_md5
import itertools
import ctypes

start_green = '\033[92m'
start_red = '\033[91m'
end_color = '\033[0m'

pwe_list = [word.strip().lower() for word in open(r'../word_lists/PWE_WordList.txt', 'r').read().split('\n')]
pwe_huge_list = [word.strip().lower() for word in open(r'../word_lists/PWE_WordList_large.txt', 'r').read().split('\n')]
pwe_bad_list = [word.strip().lower() for word in open(r'../word_lists/PWE_WordList_old.txt', 'r').read().split('\n')]
scan_list = [word.strip().lower() for word in open(r'../word_lists/scan_names.txt', 'r').read().split('\n')]
world_words = [word.strip().lower() for word in open(r'../word_lists/world_tex_words.txt', 'r').read().split('\n')]
property_words = [word.strip() for word in open(r'../word_lists/property_names.txt', 'r').read().split('\n')]
digits = [str(n) for n in range(21)] + ['{:02}'.format(n) for n in range(1, 10)]
small_digits = ['0', '1', '2', '3', '01', '02', '03']
spacers = [' ', '_'] # '-'
tex_words = [ 'a', 'b', 'c', 'i', 'y', 's', 'color', 'reflected', 'reflectivity', 'new']
rare_tex_words = ['incan', 'incandes', 'incandescent', 'incandesant', 'incandescence', 'refl', 'reflect', 'reflectance', 'reflective', 'reflection']
colors = ['red', 'purple', 'green', 'orange', 'blue', 'cyan', 'amber', 'white', 'black', 'grey', 'gray', 'yellow', 'brown']
world_tex_words = [
    'chozoglyphics',
    'new',
    'bracket',
    'ceiling',
    'arch',
    'sediment',
    'skirt',
    'pillar',
    'column',
    'glow',
    'en',
    'joint',
    'side',
    'root',
    'roots',
    'anim',
    'base',
    'deco',
    'wall',
    'floor',
    'ground',
    'door',
    'decor',
    'crack',
    'cracked',
    'tile',
    'tiling',
    'tiled',
    'grate',
    'grating',
    'pipe',
    'hose',
    'vent',
    'rock',
    'stone',
    'block',
    'glass',
    'metal',
    'metel',
    'trim',
    'edge',
    'border',
    'back',
    'part',
    'piece',
    'mini',
    'grill',
    'roof',
    'generic',
    'buffer',
    'hole',
    'small',
    'big',
    'end',
    'panel',
    'pan',
    'plate',
    'circle',
    'ring',
    'triangle',
    'square',
    'box',
    'rect',
    'hex',
    'hexagon',
    'monitor',
    'hydrolic',
    'light',
    'dark',
    'lite',
    'fan',
    'truss',
    'bracing',
    'tube',
    'beam',
    'rib',
]
char_tex_words = [
    'limbs',
    'body',
    'head',
    'heart',
    'brain',
    'torso',
    'eye',
    'eyeball',
    'eyes',
    'teeth',
    'neck',
    'skin',
    'shell',
    'metal',
    'main',
    'highlight_reflected',
    'arm',
    'arms',
    'leg',
    'legs',
    'mouth',
    'wing',
    'wings',
    'chin',
    'bottom',
    'top',
    'bot',
    'xray',
    'chest',
    'leg_arm',
    'glow',
    'base',
]

def dictionary_attack(in_words: list[str], goals: list[int], prefixes: list[str], suffixes: list[str], depth: int):
    """
    :param in_words: List of strings. The dictionary to use when brute-forcing.
    :param goals: List of ints. If any of these values are matched by a guess, the match will be printed out.
    :param prefixes: List of strings, each of which will be separately prepended to all guessed strings.
    :param suffixes: List of strings, each of which will be separately appended to all guessed strings.
    :param depth: Max number of words to use in a single guess.
    :return: None
    """
    printed = set()

    final_goals = set(goals)
    print(f'Matching [{", ".join([hex(g) for g in goals])}]')
    print(f'for prefixes {prefixes}')
    print(f'and suffixes {suffixes}')
    print(f'at depth {depth}')
    words = list(dict.fromkeys(in_words))
    prefs = list(dict.fromkeys(prefixes))
    sufs = list(dict.fromkeys(suffixes))

    for d in range(1, depth + 1):
        print(f"Testing sequences of length {d}")
        for seq in itertools.product(*[*itertools.repeat(words, d)]):
            guess_words = ''.join(seq)
            for pref in prefs:
                for suf in sufs:
                    full_guess = pref + guess_words + suf
                    if (guess := retro_md5(full_guess)) in final_goals:
                        if full_guess not in printed:
                            print(f"{start_green}Match: 0x{guess:016x} = {full_guess}{end_color}")
                            printed.add(full_guess)

def dictionary_attack_cpp(
        in_words: list[str], goals: list[int],
        prefixes: list[str], suffixes: list[str],
        depth: int, verbose: bool = True
):
    if len(goals) == 0:
        print(f"{start_red}No goals to match.{end_color}")
        return

    dll = ctypes.CDLL(r"C:\Users\Wyatt\source\repos\BruteForcer\x64\Release\BruteForcer.dll")

    words = list(dict.fromkeys(in_words))  # remove duplicates while keeping sort order
    prefs = list(dict.fromkeys(prefixes))
    sufs = list(dict.fromkeys(suffixes))

    dictionary_cpp = (ctypes.c_char_p * len(words))()
    dictionary_cpp[:] = [word.encode() for word in words]
    goals_cpp = (ctypes.c_uint64 * len(goals))()
    goals_cpp[:] = goals
    prefixes_cpp = (ctypes.c_char_p * len(prefs))()
    prefixes_cpp[:] = [pref.encode() for pref in prefs]
    suffixes_cpp = (ctypes.c_char_p * len(sufs))()
    suffixes_cpp[:] = [suf.encode() for suf in sufs]
    depth_cpp = ctypes.c_uint(depth)
    verbose_cpp = ctypes.c_uint8(verbose)

    dll.dictionaryAttackMD5.argtypes = [ctypes.POINTER(ctypes.c_char_p), ctypes.c_size_t,
                                          ctypes.POINTER(ctypes.c_uint64), ctypes.c_size_t,
                                          ctypes.POINTER(ctypes.c_char_p), ctypes.c_size_t,
                                          ctypes.POINTER(ctypes.c_char_p), ctypes.c_size_t,
                                          ctypes.c_uint32,
                                          ctypes.c_uint8]
    dll.dictionaryAttackMD5.restype = None

    dll.dictionaryAttackMD5(
        dictionary_cpp, len(words),
        goals_cpp, len(goals),
        prefixes_cpp, len(prefixes),
        suffixes_cpp, len(suffixes),
        depth_cpp,
        verbose_cpp
    )

def add_delimiters(words: list[str], delimiters: list[str]):
    return list(itertools.chain(*[[word, *[word + delimiter for delimiter in delimiters]] for word in words]))


if __name__ == '__main__':
    dictionary = ['main', 'skytown','skytown_main','fire','bryyo_fire','ice', '!','gfplanet','gf','world', '_06','pod','skytown_pod','main', 'skytown_main','elysia', 'ambient','weather',]#*pwe_huge_list]
    dictionary = add_delimiters(dictionary, [*'_/'])
    # dictionary = [*string.ascii_lowercase, *string.digits, *'_/']
    # dictionary_attack_cpp(dictionary, [0xede179121627ed3f],
    #                   ['$/worlds/','$/worlds/skytown','$/worlds/elysia',],
    #                   ['/00_skytown_save_a/cooked/00_skytown_save_a_lit_lightmap0.txtr','/00_skytown_save_a/cooked/00_skytown_save_a_lit_lightmap1.txtr'], 2, False)
    dictionary_attack_cpp(dictionary, [0x2213f2ba3ec9096b],
                      ['$/worlds/','$/worlds/skytown/!', ],
                      ['/cooked/09_skytown_observation.mrea','world/cooked/09_skytown_observation.mrea','main/cooked/09_skytown_observation.mrea'], 4, False)