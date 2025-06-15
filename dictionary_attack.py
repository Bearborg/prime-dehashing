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
from utils.crc32 import crc32, remove_suffix
from typing import List
import string

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
ice_words = ['snow', 'frost', 'frosty', 'ice', 'icy', 'frozen', 'icicle', 'cave', 'temple', 'iced']
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
pwe_list = [word.strip().lower() for word in open(r'F:\Games\Emulation\Tools\PrimeWorldEditor\resources\WordList.txt', 'r').read().split('\n')]
flaahgra_words = [
    # 'preload',
    # 'ancs',
    # 'asset',
    # 'assets',
    # 'fight',
    # 'battle',
    # 'room',
    # 'arena',
    # 'anim',
    # 'fla',
    'flaa',
    'flaaghra',
    'flaahgra',
    'plant',
    'boss',
    'creature',
    'boss_creature',
    'plant_boss',
    'plantboss',
    # 'plant_creature',
    # 'top',
    # 'a',
    # 'g',
    # 'h',
    # 'r',
    # 's',
]
scan_tex_folders = [
    '$/ScannableObjects/Creatures/sourceimages/'.lower(),
    '$/ScannableObjects/Intro_World/sourceimages/'.lower(),
    '$/ScannableObjects/Chozo_Ruins/sourceimages/'.lower(),
    '$/ScannableObjects/Ice_World/sourceimages/'.lower(),
    '$/ScannableObjects/Overworld/sourceimages/'.lower(),
    '$/ScannableObjects/Mines/sourceimages/'.lower(),
    '$/ScannableObjects/Lava_World/sourceimages/'.lower(),
    '$/ScannableObjects/Crater/sourceimages/'.lower(),
    '$/ScannableObjects/Tests/sourceimages/'.lower(),
    '$/ScannableObjects/Game Mechanics/sourceimages/'.lower(),
]
scan_tex_suffixes = ['_l', '_r', '_2l', '_2r', '_4l', '4r']
scan_tex_suffixes_rare = [
    '_1',
    '_one',
    '_2',
    '_two',
    '_3',
    '_three',
    '_4',
    '_four',
    '_l',
    '_left',
    '_r',
    '_right',
    '_1l',
    '_2l',
    '_2la',
    '_2lb',
    '_3l',
    '_4l',
    '_half_4l',
    '_4la',
    '_4lb',
    '_4l2',
    '_1r',
    '_2r',
    '_2ra',
    '_2rb',
    '_3r',
    '_4r',
    '_half_4r',
    '_4ra',
    '_4rb',
    '_4r2',
    '_lr',
    '_quad',
    '_quad_1',
    '_quad_2',
    '_bi',
    '_bi_1',
    '_bi_2',
]
scan_tex_words = [
    'top',
    'up',
    'front',
    'frontl',
    'frontr',
    'side',
    'bottom',
    'right',
    'left',
    'back',
    'rear',
    'under',
    'persp',
    'perspective',
    'head',
    'face',
    'arm',
    'xray',
]

#dictionary = ['metaree', 'ruin', 'ruins', 'alpha', 'bound', 'ice', 'iced', 'freeze', 'frozen', *spacers]
#dictionary = [*mine_words, *world_tex_words, *tex_words, *colors, *digits, *spacers]
#dictionary = ['samus', 'stonehenge', 'outro', 'end', 'intro', 'cinematic', 'cinema', *spacers]
#dictionary = ['editor', 'trigger', 'blue', 'cube', 'box', 'face', 'volume', 'border', 'outline', 'c', 'color', 'top', 'side', 'bottom', 'bot', *small_digits, *spacers]
#dictionary = ['samus', 'camera', 'actions', 'walk', 'idle', 'common', 'motion', 'base', 'left', 'right', 'gun', 'arm', 'bound', 'new', 's', *small_digits, *spacers]
#dictionary = ['samus', 'wire', 'frame', 'wireframe', 'grid', 'rim', 'trim', 'cell', 'anim', 'outline', 'line', 'edge','border', 'glow', 'amber', 'brown', 'orange', 'square', 'tile', 'gradation', 'gradient', 'holo', 'hologram', 'heat', 'gun', 's', *tex_words, *rare_tex_words, *spacers]
#dictionary = ['0', '7', 'bird', 'beak', 'chunk', 'gib', 'debris', 'piece', 'part', 'anim', 'animated', 'animating', 'bound', '0', '1', '2', '3', 'a', 'b', 'c', 's', *spacers]
#dictionary = ['15', 'ener', 'energy', 'core', 'ring', 'center', 'blade', 'top', 'anim', 'animated', 'animating', 'bound', '0', '1', '2', 's', *spacers]
#dictionary = [*character_words, 'new', 'spank', 'weed', 'spankweed', 'spank_weed', 'arm', 'tentacle', 'vine', 'reaper', 'blade', 'no', 'eye', 'eyeball', 'no_eye', 'noeye', *'012', 's', '/cooked', '/', *spacers]
#dictionary = ['light', 'grill', 'e', 'stripe', 'work', 'lamp', 'lite', 'fixture', *tex_words, *spacers]
#dictionary = ['_phasonarm', 'l', 'r', 'phason', 'left', 'right', 'arm', 'hit', 'hitbox', 'vol', 'volume', 'dynamic', 'collision', 'collide', 'collider', 'hull', 'geo', 'geometry', 'damage', 'weak', 'weakness', 'spot', 'point', 'obj', 'object', 'mesh', 'thigh', 'omega', 'pirate', 'shoulder', 'phazon', 'piece', 'part', 'leg', 'hip', 'armor',  's', '/', *'012abc', 'bound', *spacers]
#dictionary = ['line', 'lines', 'sun', 'center', 'segment', 'seg', 'orbit', 'planet', 'jupiter', 'saturn', 'uranus', 'neptune', 'ring', 'ringed', 'trajectory', 'grid', 'mesh', 'plane', 'coordinate', 'coord', 'trajectories', 'scan', 'dashed', 'dash', 'dashes', 'traj', 'holo', 'hologram', 's', 'anim', 'gradient', 'gradation', 'blue', 'light', 'lite', *'012', *tex_words, *rare_tex_words, *spacers]
#dictionary = ['ridley', 'shot', '1', 'stagger', 'back', 'stagger_back', 'staggerback', 'acting', 'fix', '-', *spacers]
#dictionary = ['visor', 'generic', 'pickupvisor', 'vizor', 'can', 'scan', 'vision', 'mode', 'view', 'vis', 'upgrade', 'power', 'suit', 'samus', 'xray', 'x-ray', 'thermal', 'ready', 'therm', 'heat', 'pickup', 'pick', 'up', 'item', 'anim', 'animated', 'new', 'bound', 's', 'working', 'work', '/', *'012', '-', *spacers]
#dictionary = ['zoomer', 'grisby', 'grizby', 'piece', 'part', 'arm', 'leg', 'hip', 'thigh', 'armor', 'armour', 'left', 'l', 'right', 'r', '/', *'012', *spacers]
#dictionary = ['new', *flaahgra_words, *character_words, 'test', 'work', 'working', 'body', 'cine', 'cinematic', 'component', 'set', 'animation', 'animated', 'anim', 'tree', 'blood_flower', 'phason', 'phazon', 'poison', 'poisonous', 'toxic', 'ruin', 'ruins', 'metroid', 'chozoruins', 'chozo_ruins', 'ruinsworld', 'ruinworld', 'flower', 'piece', 'part', 'version', 'char', 'character', 'version', 'v', '/cooked', '/scenes', '(', ')', '/', 's', '0', '1', '2', '.', '!', *spacers]
#dictionary = [*flaahgra_words, *char_tex_words, 'f', 'p', 'b', 'eye', 'eyes', 'eyeball', 'face', 'orange', 'glow', 'glowing', 's', *tex_words, *small_digits, *spacers]
#dictionary = ['wave', 'beam', 'charge', 'v', 'version', 'projectile', 'main', 'new', 'cinema', 'shot', 'weapon', '0', '1', '2', '3', '4', '/', 's', *spacers]
#dictionary = [*pwe_list, *spacers]
#dictionary = ['sapsack', 'broken', 'damaged', 'damage', 'destroyed', 'destroy', 'dead', 'exploded', 'core', 'debris', 'pit', 'sap', 'sack', 'sac', 's', *string.digits,  *spacers]
#dictionary = [*string.ascii_lowercase]
#dictionary = ['metroid', 'prime', 'swamp', 'world', *'12345!.', '/swamp_world', '/swampworld', '/', 's', *spacers]
#dictionary = ['bogus', 'phaz', 'phas', 'phase', 'veins', 'phazon', 'phason', 'gun', 'cannon', 'casing', 'incan', 'reflectivity', 'dark', 'light',  's', *spacers]
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
#dictionary = ['12', 'highlight', 'new', 'red', 'orange', 'fade', 'effect', 'small', 'big', 'large', 'glow', 'ledge', 'heated', 'molten', 'metal', 'superheated', 'tube', 'spew', 'pipe', 'lava', 'magma', 'vent', 'ventilation', 'over', 'fiery', 'firey', 'fire', 'firy', 'shore', 's', 'fieryshores', 'anim', *'012', '01', 'bound', '/', '-', *spacers]
#dictionary = ['20', '20_', 'fan_1', 'spin', 'big', 'bigger', 'air', 'large', 'metal', 'industrial', 'set', 'char', 'character', 'object', 'obj', 'turn', 'rotate', 'slow', 'fast', 'reflecting', 'pool', 'rp',  'big', 'vent', 'ventilation', 'anim', 'animation', 'animated', 'fan', 'fans', 'one', 'two', 'zero', 'first', 'second', *'012', 's', *spacers]
dictionary = ['0', '9', '09', 'over', 'artifact', 'puzzle', 'm', 't', 'obj', 'bridge', 'lava', 'object', 'part', 'piece', 'spin', 'lock', 'spinner', 'monitor', 'tower', 'monitortower', 'monitor_tower', 'tow', 'mon', 'bound', 'anim', 's', '/', '/cooked', *spacers]
def dictionary_attack(goals: List[int], prefix: str, suffix: str, depth: int):
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
    final_goals = [remove_suffix(g, suffix) for g in goals]
    print(f'Matching [{", ".join([hex(g) for g in goals])}] for "{prefix}[...]{suffix}" at depth {depth}')
    words = list(dict.fromkeys(dictionary)) # remove duplicate words while preserving order
    len_words = len(words)
    currents = [0 for _ in range(depth)]
    prefix_hash = crc32(prefix)
    guess_stack: List[int] = [crc32((words[0] * i), prefix_hash) for i in range(1, depth + 1)]

    print(words[0])

    # quick check for [0], [0][0], [0][0][0], etc., after this we only check on value change
    for k, init in enumerate(guess_stack, 1):
        if (match := crc32(suffix, init)) in final_goals:
            print(f"{start_green}Match: {hex(crc32(suffix, match))} = {prefix}{words[0] * k}{suffix}{end_color}")

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
                        #if (match := crc32('_'.join([words[z] for z in currents[:(-k + 1) or None]]), prefix_hash)) in final_goals:
                        if (match := guess_stack[-1]) in final_goals:
                            end_index = (-k + 1) or None
                            print(f"{start_green}"
                                  f"Match: {hex(crc32(suffix, match))} = "
                                  f"{prefix}{''.join([words[i] for i in currents[:end_index]])}{suffix}"
                                  f"{end_color}")
                    break

def dictionary_attack_multi_prefix(goals: List[int], prefixes: List[str], suffix: str, depth: int):
    """
    Basically the same as above, but takes in a list of potential prefixes instead of a single string. The code for this
    version is uglier due to the extra loops, so I've kept it as a separate function for clarity.
    :param goals: List of ints. If any of these values are matched by a guess, the match will be printed out.
    :param prefixes: List of strings, each of which will be separately prepended to all guessed strings.
    :param suffix: Suffix appended to all guessed strings.
    :param depth: Max number of words to use in a single guess.
    :return: None
    """
    final_goals = [remove_suffix(g, suffix) for g in goals]
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
            if (match := crc32(suffix, init)) in final_goals:
                print(f"{start_green}Match: {hex(crc32(suffix, match))} = {prefixes[idx]}{words[0] * k}{suffix}{end_color}")

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
                            if (match := guess_stack[-1]) in final_goals:
                                end_index = (-k + 1) or None
                                print(f"{start_green}"
                                      f"Match: {hex(crc32(suffix, match))} = "
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
    #dictionary_attack(m5_goals, "$/Worlds/Mines/common_textures/".lower(), ".txtr".lower(), 4)
    #dictionary_attack(m6_goals, "$/Worlds/Overworld/common_textures/".lower(), ".txtr".lower(), 4)
    #dictionary_attack(m4_goals, "$/Worlds/IntroUnderwater/common_textures/".lower(), ".txtr".lower(), 5)
    #dictionary_attack([0xba2e567c, 0x8d5241eb], "$/Characters/spank_weed/cooked/".lower(), "_bound.cmdl".lower(), 6)
    #dictionary_attack_multi_prefix([0xe2d76f28], ["$/AnimatedObjects/RuinsWorld/scenes/".lower(), "$/Characters/".lower(), ], "/B_shudderbase_flaaghra.ani".lower(), 7)
    #dictionary_attack_multi_prefix([0x70035854], ["$/AnimatedObjects/RuinsWorld/".lower(), "$/AnimatedObjects/RuinsWorld/scenes/".lower(), "$/Characters/".lower()], "".lower(), 5)
    #dictionary_attack_multi_prefix([0xc7a7abec], ["$/AnimatedObjects/RuinsWorld/".lower(), "$/AnimatedObjects/RuinsWorld/scenes/".lower(), "$/Characters/".lower(), "$/Characters/plant_boss/".lower()], "/".lower(), 5)
    #dictionary_attack_multi_prefix([0x10762b2e], ["$/characters/".lower(), "$/AnimatedObjects/RuinsWorld/scenes/".lower()], "/cooked/b_intoready_flaaghra.ani".lower(), 5)
    #dictionary_attack_multi_prefix([0x96324de1], ["$/Effects/particles/sam_weapon/beam/wave/".lower(), "$/Effects/particles/sam_weapon/beam/".lower(), "$/Effects/particles/sam_weapon/".lower(), "$/Characters/samusGun/cooked/effects/".lower()], ".wpsm.wpsc".lower(), 5)
    #dictionary_attack([0x22568ca0], "$/Characters/".lower(), "/B_angry4_flaaghra.ani".lower(), 6)
    #dictionary_attack([0x8033012D], "$/Characters/warwasp/sourceimages/".lower(), ".txtr".lower(), 6)
    #dictionary_attack([0x0945B1B7], "$/Characters/common_textures/samusgun/".lower(), ".txtr".lower(), 5)
    #dictionary_attack_multi_prefix([0xF7971653, 0xAD4ED949, 0x60468339, 0x8AF881A4, 0x9E628F99], ["$/characters/plant_boss_creaturencxk_rn/sourceimages/".lower()], ".txtr".lower(), 4)
    #dictionary_attack_multi_prefix([0x203B5A77], ["$/Worlds/RuinWorld/7_ruinedroof/sourceimages/".lower()], ".txtr".lower(), 5)
    #dictionary_attack([0x0c5c9c3b], "$/Characters/samusGunMotion/cooked/".lower(), ".cmdl".lower(), 5)
    #dictionary_attack_multi_prefix([0x5B81ABC1], ["$/Worlds/".lower(),"$/"], "/!Swamp_World/cooked/0q_swamp_hall_dark.mrea".lower(), 6)
    #dictionary_attack([0x0c5c9c3b, 0x9c8058b1, 0x0ef58656], "$/Characters/SamusGun/cooked/models/".lower(), ".cmdl".lower(), 5)
    # dictionary_attack_multi_prefix([0x7BDE8CD3, 0x06955FA2, 0xbee1f32f],[
    #                                 "$/editorsupport/editormodels/sourceimages/".lower(),
    #                                 "$/editorsupport/common_textures/".lower(),
    #                                 "$/Textures/defaults/".lower(),
    #                                 "$/Textures/editorsupport/".lower()
    # ], ".txtr".lower(), 5)
    #dictionary_attack([0x39fe39bc], "$/Characters/".lower(), "/R_struckBack_magdalite.ani".lower(), 8)
    #dictionary_attack([0xC22E8E2E], "$/AnimatedObjects/IceWorld/11_hologram/".lower(), "/cooked/11_trajectorylines_ready.ani".lower(), 6)
    #dictionary_attack([0xC22E8E2E], "$/AnimatedObjects/IceWorld/11_hologram/cooked/".lower(), "/11_trajectorylines_ready.ani".lower(), 6)
    #dictionary_attack([0xC22E8E2E], "$/AnimatedObjects/IceWorld/11_hologram/cooked/".lower(), "/cooked/11_trajectorylines_ready.ani".lower(), 6)
    #dictionary_attack([0x9CA3F99B], "$/".lower(), "_DGRP".lower(), 6)
    #dictionary_attack([0x74D5FE5B, 0xE6722B40, 0xBE530FCE, 0x1E0FB564], "$/Characters/elite_space_pirate/cooked/omega/".lower(), ".dcln".lower(), 6)
    #dictionary_attack_multi_prefix([0x63987781, 0x168E7672, 0x7F47633B], ["$/AnimatedObjects/IceWorld/11_trajlines/sourceimages/".lower(), "$/AnimatedObjects/IceWorld/11_hologram/sourceimages/".lower()], ".txtr".lower(), 5)
    #dictionary_attack_multi_prefix([0xF6644505], ["$/Characters/Ridley/cooked/".lower()], ".ani".lower(), 7)
    #dictionary_attack_multi_prefix([0xE135621D, 0x0D0EFC82, 0x96ABB0ED], ['$/AnimatedObjects/Overworld/12_lavaspew/cooked/'.lower(), '$/AnimatedObjects/Overworld/12_fieryshores/cooked/'.lower(), ], '.cmdl'.lower(), 5)
    #dictionary_attack_multi_prefix([0x538D3318, 0xF512C134], ['$/AnimatedObjects/RuinsWorld/scenes/20_objects/cooked/'.lower()], '.acs'.lower(), 5)
    dictionary_attack([0xA8877F06], '$/AnimatedObjects/Overworld/09_monitortower/spinner/cooked/'.lower(), '.acs'.lower(), 5)
    #dictionary_attack([0x0FE93088, 0x62DF838C, 0x949A25CD, 0x14FE72B8], '$/Worlds/Overworld/00f_over_hall/cooked/'.lower(), ".cmdl".lower(), 6)
    #dictionary_attack_multi_prefix([0xba2e567c, 0x8d5241eb], ['$/Characters/spank_weed/cooked/'.lower(),'$/AnimatedObjects/RuinsWorld/scenes/spank_weed/cooked/'.lower(),'$/Characters/tentacle/cooked/'.lower(),'$/Characters/Water_Tentacle/cooked/'.lower(), '$/Characters/spank_weed/cooked/models/'.lower(), '$/Characters/new_spank_weed/cooked/'.lower(), '$/Characters/spank_weed_alpha/cooked/'.lower(), '$/Characters/alpha_spank_weed/cooked/'.lower(), ], "_bound.cmdl".lower(), 5)