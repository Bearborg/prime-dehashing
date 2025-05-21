"""
Kinda-optimized dictionary attack. Partial hashes are stored in a stack to minimize repetitive hashing. Also has a
variant that tests against multiple prefixes, which can be useful if you want to search across multiple paths at once.

Raising the recursion depth takes exponentially longer to run with each increase, so I wouldn't recommend exceeding a
depth of 5 words unless your dictionary is really small.

The dictionary of words to use is defined up at the top, and I've split some words into categories that you can merge
into a full dictionary using Python's splatting operator (*). For example, if you wanted to try guessing texture names
for Sheegoths, you might set the dictionary like so:

dictionary = ['sheegoth', 'babygoth', 'ice', *tex_words, *rare_tex_words, *char_tex_words, *spacers]
"""

import sqlite3
from utils.crc32 import crc32
from typing import List

start_green = '\033[92m'
end_color = '\033[0m'

prime_boss_words = ['metroid','prime','head','body','spider','exo','core','essence','boss','new','stage','phase','0','1','2','/',]
artifact_scan_words = [ 'chozo', 'holo', 'hologram', 'artifact', 'hint', 'space ', 'pirate', 'pirate log', '002', '003', '006', '012', '018', '019', '020', '023', 'scan']
digits = [str(n) for n in range(21)] + ['{:02}'.format(n) for n in range(1, 10)]
small_digits = ['0', '1', '2', '3', '01', '02', '03']
spacers = [' ', '_'] # '-'
tex_words = [ 'a', 'b', 'c', 'i', 'y', 's', 'color', 'reflected', 'reflectivity', 'new']
rare_tex_words = ['incan', 'incandes', 'incandescent', 'incandescence',]
colors = ['red', 'purple', 'green', 'orange', 'blue', 'white', 'black', 'grey', 'gray', 'yellow', 'brown']
world_tex_words = [
    'anim',
    'wall',
    'floor',
    'door',
    'decor',
    'crack',
    'cracked',
    'tile',
    'tiling',
    'tiled',
    'grate',
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
]
ruin_words = ['moss', 'mossy', 'chozo', 'rune', 'glyph', 'symbol', 'symbols', 'writing', 'sand', 'vine', 'tree', 'leaf', 'leaves', 'bark', 'brick', 'hieroglyph', 'heiroglyph', 'hieroglyphic', 'heiroglyphic', 'statue', 'carving', 'bronze', 'copper', 'dust']
ice_words = ['snow', 'frost', 'ice', 'frozen', 'icicle', 'cave', 'temple', 'iced']
over_words = ['canopy', 'root', 'dandelion', 'star', 'shovel', 'moss', 'vine', 'grass', 'sand', 'leaf', 'leaves', 'tree', 'trunk', 'bark', 'mossy', 'fern', 'lichen', 'ivy', 'plant', 'mud', 'wet', 'riverbed', 'sulfur', 'granite', 'limestone', 'lime', 'glow', 'foliage']
lava_words = ['lava', 'magma', 'molten', 'hot', 'heated', 'ash', 'cinder', 'cooled', 'volcanic']
mine_words = ['shaft', 'mine', 'gravel', 'track', 'cement', 'dirt', 'shroom', 'mushroom', 'fungus', 'fungal', 'phason', 'phazon', 'phas', 'phaz']
crater_words = ['web', 'webbing', 'bone', 'membrane', 'floss', 'egg', 'alive', 'dead', 'glow', 'glowing', 'vein', 'cancer', 'barnacle', 'growth', 'pale', 'sphincter', 'pucker', 'tumor', 'scab', 'flesh', 'brain', 'nub', 'organ', 'tissue', 'tooth', 'teeth', 'phazon', 'phason', 'phaz', 'phas', 'cell']
organic_words = ['paper', 'honeycomb', 'dry', 'dried', 'wood', 'war', 'wasp', 'hive', 'nest', 'water', 'toxic', 'poison', 'poisoned', 'poisonous', 'root', 'moss', 'vine', 'grass', 'leaf', 'leaves', 'tree', 'trunk', 'bark', 'mossy', 'fern', 'lichen', 'ivy', 'plant', 'glow', 'foliage']
character_words = ['alpha', 'beta', 'gamma', 'bound']
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
flaahgra_words = [
    'preload',
    'ancs',
    'asset',
    'assets',
    'fight',
    'battle',
    'room',
    'arena',
    'anim',
    'fla',
    'flaaghra',
    'flaahgra',
    'plant',
    'boss',
    'creature',
    'boss_creature',
    'plant_boss',
    'plantboss',
    'plant_creature',
    'top',
    'a',
    'g',
    'h',
    'r',
    's',
]

dictionary = [*flaahgra_words, *spacers]
#dictionary = [*lava_words, *world_tex_words, *tex_words, *colors, *digits, *spacers]
#dictionary = ['/', '/sourceimages/', 'garbeetle', 'garganbeetle', 'gargantuanbeetle', 'gargantuan_beetle', 'gar_beetle', 'beetle', 'beta', 'alpha', 'gamma', *tex_words, *rare_tex_words, *char_tex_words, *small_digits, *spacers]
#dictionary = ['omega', 'omegapirate', 'omega_pirate', 'elite', 'elitepirate', 'elite_pirate', 'elitespacepirate', 'elite_space_pirate', *character_words, *char_tex_words, *tex_words, *small_digits, *spacers]
#dictionary = ['11', 'planet', 'solar', 'system', 'hologram', 'holo', 'trajectory', 'trajectories', 'line', 's', *spacers]
#dictionary = [' door', ' gate', ' super', ' missile', ' breakable',  ' destroyable', ' destructable', ' destructible', ' deactivate', ' deactivated', ' inactive', ' active', ' activate', ' activated', ' locked', ' flavor', ' scan', *small_digits, 's', ' ']
#dictionary = [' missile', ' pickup', ' phazon', ' snake', ' weed', ' red', ' poison', ' crate', ' floor', ' phason', ' radiation', ' level', ' scan', ' warning', ' alert', ' hint', 's', ' ']
#dictionary = [' unreachable', ' inaccessible',  ' crushed', ' collapsed', ' broken', ' closed', ' thermal', ' door', ' doorway', ' walkway', ' big', ' inactive', ' disabled', ' debris', ' destroyed', ' locked', ' blocked', ' scan', ' hint', 's', ' ']
#dictionary = [' artifact', ' hole', ' unstable',  ' breakable',  ' destroyable', ' destructable', ' destructible', ' floor', ' ground', ' bombable',' power', ' bomb', ' active', ' activate', ' activated', ' locked', ' blocked', ' force', 'field', ' hint', ' scan', *small_digits, 's', ' ']
#dictionary = [' mystery', ' chozo', ' artifact', ' unknown', ' item', ' super', ' missile', ' pickup', ' ammo', ' expansion', ' scan', 's', ' ']
#dictionary = [' holo', ' hologram', ' to', ' 00_', 'Mines', ' pickup', ' map', ' station', ' flavor',  ' scan', ' door', ' generator', ' deactivate', ' deactivated', ' inactive', ' active', ' activate', ' activated', ' hint', 's', ' ']
#dictionary = [' flavor', ' moving', ' geothermal', ' tube', ' fuel', ' thermal', ' floating', ' platform', ' wall', ' elev', ' elevator', ' pirate', ' space pirate', ' flame', ' fire', ' jet', ' flamethrower', ' bomb', ' breakable',  ' destroyable', ' destructable', ' destructible', ' bombable', ' lava', ' magma', ' light', ' lamp', ' fixture', ' varia', ' suit', ' scan', ' hint', 's', *small_digits, ' ']

def dictionary_attack(goals, prefix, suffix, depth):
    """
    Performs dictionary attacks with a fixed prefix and suffix, any number of goal hashes, and an arbitrary depth.

    To avoid repeatedly hashing the same text, partial hashes are stored in a stack, meaning only the last word needs to
    be freshly hashed.
    :param goals: List of ints. If any of these values are matched by a guess, the match will be printed out.
    :param prefix: Prefix prepended to all guessed strings.
    :param suffix: Suffix appended to all guessed strings.
    :param depth: Max number of words to use in a single guess.
    :return: None
    """
    print(f'Matching [{", ".join([hex(g) for g in goals])}] for "{prefix}[...]{suffix}" at depth {depth}')
    words = list(dict.fromkeys(dictionary)) # remove duplicate words while preserving order
    len_words = len(words)
    currents = [0 for _ in range(depth)]
    prefix_hash = crc32(prefix)
    guess_stack: List[int] = [crc32((words[0] * i), prefix_hash) for i in range(1, depth + 1)]

    print(words[0])

    # quick check for [0], [0][0], [0][0][0], etc., after this we only check on value change
    for k, init in enumerate(guess_stack, 1):
        if (match := crc32(suffix, init)) in goals:
            print(f"{start_green}Match: {hex(match)} = {prefix}{words[0] * k}{suffix}{end_color}")

    for i in range(pow(len_words, depth)):
        if i % 1000000 == 0:
            print(f'{(i * 100 / pow(len_words, depth)):.2f}%')

        for j, place_val in enumerate(range(depth), 1):
            place = pow(len_words, place_val)
            if ((i % place) // place) == 0:
                currents[-j] = (currents[-j] + 1) % len_words
                guess_stack.pop()
                if currents[-j] != 0:
                    for k in range(j, 0, -1):
                        if len(guess_stack):
                            guess_stack.append(crc32(words[currents[-k]], guess_stack[-1]))
                        else:
                            print(words[currents[-k]])
                            guess_stack.append(crc32(words[currents[-k]], prefix_hash))
                        if (match := crc32(suffix, guess_stack[-1])) in goals:
                            end_index = (-k + 1) or None
                            print(f"{start_green}"
                                  f"Match: {hex(match)} = "
                                  f"{prefix}{''.join([words[i] for i in currents[:end_index]])}{suffix}"
                                  f"{end_color}")
                    break

def dictionary_attack_multi_prefix(goals, prefixes, suffix, depth):
    """
    Basically the same as above, but takes in a list of potential prefixes instead of a single string. The code for this
    version is uglier due to the extra loops, so I've kept it as a separate function for clarity.
    :param goals: List of ints. If any of these values are matched by a guess, the match will be printed out.
    :param prefixes: List of strings, each of which will be separately prepended to all guessed strings.
    :param suffix: Suffix appended to all guessed strings.
    :param depth: Max number of words to use in a single guess.
    :return: None
    """
    for prefix in prefixes:
        print(f'Matching [{", ".join([hex(g) for g in goals])}] for "{prefix}[...]{suffix}" at depth {depth}')
    words = list(dict.fromkeys(dictionary))
    len_words = len(words)
    currents = [0 for _ in range(depth)]
    prefix_hashes: List[int] = [crc32(prefix) for prefix in prefixes]
    guess_stacks: List[List[int]] = [
        [crc32((words[0] * i), prefix_hash) for i in range(1, depth + 1)] for prefix_hash in prefix_hashes
    ]

    print(words[0])

    for idx, guess_stack in enumerate(guess_stacks):
        # quick check for [0], [0][0], [0][0][0], etc., after this we only check on value change
        for k, init in enumerate(guess_stack, 1):
            if (match := crc32(suffix, init)) in goals:
                print(f"{start_green}Match: {hex(match)} = {prefixes[idx]}{words[0] * k}{suffix}{end_color}")

    for i in range(pow(len_words, depth)):
        if i % (1000000 // len(prefixes)) == 0:
            print(f'{(i * 100 / pow(len_words, depth)):.2f}%')

        for j, place_val in enumerate(range(depth), 1):
            place = pow(len_words, place_val)
            if ((i % place) // place) == 0:
                currents[-j] = (currents[-j] + 1) % len_words
                for guess_stack in guess_stacks:
                    guess_stack.pop()
                if currents[-j] != 0:
                    for k in range(j, 0, -1):
                        if len(guess_stacks[0]):
                            for guess_stack in guess_stacks:
                                guess_stack.append(crc32(words[currents[-k]], guess_stack[-1]))
                        else:
                            print(words[currents[-k]])
                            for l, guess_stack in enumerate(guess_stacks):
                                guess_stack.append(crc32(words[currents[-k]], prefix_hashes[l]))
                        for m, guess_stack in enumerate(guess_stacks):
                            if (match := crc32(suffix, guess_stack[-1])) in goals:
                                end_index = (-k + 1) or None
                                print(f"{start_green}"
                                      f"Match: {hex(match)} = "
                                      f"{prefixes[m]}{''.join([words[i] for i in currents[:end_index]])}{suffix}"
                                      f"{end_color}")
                    break

def fetch_unmatched_assets(pak_name: str, asset_type: str):
    asset_db_path = r'./database/mp_resources.db'
    connection = sqlite3.connect(asset_db_path)
    resource_results = connection.execute(
        f"select ap.hash from asset_paths ap "
        f"inner join asset_usages us on ap.hash = us.hash "
        f"where ap.path_matches = 0 "
        f"and us.game like 'MP1/1.00' "
        f"and us.pak = '{pak_name}.pak' COLLATE NOCASE "
        f"and us.type = '{asset_type}' "
        f"and not ap.path like '$/Scannable%' "
        f"and not ap.path like '%lightmap%' "
        f"group by ap.hash "
        f"order by ap.path "
    ).fetchall()
    return [int(row[0], 16) for row in resource_results]

if __name__ == '__main__':
    m2_goals = fetch_unmatched_assets('Metroid2', 'TXTR')
    m3_goals = fetch_unmatched_assets('Metroid3', 'TXTR')
    m4_goals = fetch_unmatched_assets('Metroid4', 'TXTR')
    m5_goals = fetch_unmatched_assets('Metroid5', 'TXTR')
    m6_goals = fetch_unmatched_assets('Metroid6', 'TXTR')
    m7_goals = fetch_unmatched_assets('Metroid7', 'TXTR')
    slideshow_goals = fetch_unmatched_assets('Slideshow', 'TXTR')
    m2_prefixes = [
        "$/Worlds/RuinWorld/common_textures/".lower(),
        "$/Worlds/RuinWorld/common_textures/stone/".lower(),
        "$/Worlds/RuinWorld/common_textures/metal/".lower(),
        "$/Worlds/RuinWorld/common_textures/organic/".lower(),
    ]
    #dictionary_attack_multi_prefix(m3_goals, m3_prefixes, ".txtr".lower(), 4)
    #dictionary_attack_multi_prefix([0x8B802D22], ['$/Worlds/RuinWorld/common_textures/organic/', '$/Worlds/RuinWorld/common_textures/'], ".txtr".lower(), 4)
    #dictionary_attack(m2_goals, "$/Worlds/RuinWorld/common_textures/".lower(), ".txtr".lower(), 4)
    #dictionary_attack([0x693D8E22, 0xEEA26B3D, 0x0DB82983, 0x38B6B3D1, 0x7A30AAB8, 0x8C016008], "$/Characters/gargantuan_beetle/sourceimages/".lower(), ".txtr".lower(), 4)
    #dictionary_attack([0x24B75052, 0x750EDEB3, 0x68919D46, 0x05368239, 0xF9563AF9, 0x69B2F842], "$/Characters/elite_space_pirate/sourceimages/omega_pirate/".lower(), ".txtr".lower(), 4)
    #dictionary_attack(m2_goals, "$/Worlds/RuinWorld/common_textures/metal/".lower(), ".txtr".lower(), 4)
    #dictionary_attack(m3_goals, "$/Worlds/IceWorld/common_textures/".lower(), ".txtr".lower(), 4)
    #dictionary_attack(m4_goals, "$/Worlds/Overworld/common_textures/".lower(), ".txtr".lower(), 4)
    #dictionary_attack(m4_goals, "$/Worlds/IntroUnderwater/common_textures/".lower(), ".txtr".lower(), 4)
    #dictionary_attack(m6_goals, "$/Worlds/Overworld/common_textures/".lower(), ".txtr".lower(), 4)
    #dictionary_attack(m7_goals, "$/Worlds/Crater/common_textures/".lower(), ".txtr".lower(), 4)
    #dictionary_attack(m4_goals, "$/Worlds/IntroUnderwater/common_textures/".lower(), ".txtr".lower(), 5)
    #dictionary_attack([0x83cc051f], "$/Characters/alpha_drone/cooked/".lower(), ".cskr".lower(), 6)
    #dictionary_attack([0x10762b2e], "$/characters/".lower(), "/cooked/b_intoready_flaaghra.ani".lower(), 5)
    #dictionary_attack([0x22568ca0], "$/Characters/".lower(), "/B_angry4_flaaghra.ani".lower(), 6)
    #dictionary_attack([0x8033012D], "$/Characters/warwasp/sourceimages/".lower(), ".txtr".lower(), 6)
    #dictionary_attack([0x39fe39bc], "$/Characters/".lower(), "/R_struckBack_magdalite.ani".lower(), 8)
    #dictionary_attack([0xC22E8E2E], "$/AnimatedObjects/IceWorld/11_hologram/".lower(), "/cooked/11_trajectorylines_ready.ani".lower(), 6)
    #dictionary_attack([0xC22E8E2E], "$/AnimatedObjects/IceWorld/11_hologram/cooked/".lower(), "/11_trajectorylines_ready.ani".lower(), 6)
    #dictionary_attack([0xC22E8E2E], "$/AnimatedObjects/IceWorld/11_hologram/cooked/".lower(), "/cooked/11_trajectorylines_ready.ani".lower(), 6)
    dictionary_attack([0x9CA3F99B], "$/".lower(), "_DGRP".lower(), 6)