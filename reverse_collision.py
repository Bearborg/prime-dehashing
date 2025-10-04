"""
Detects partial matches between two hashes that share a common starting path (i.e. files that are known to be in the
same folder, but the path of folder itself is not known).
"""

import string
import os
import json
from utils.crc32 import remove_suffix, crc32
from typing import List, Tuple

start_green = '\033[92m'
end_color = '\033[0m'

def generate_all_reverse_hashes(starting_hash: int, dictionary: List[str], suffix: str, depth: int):
    """
    Based on dictionary_attack, but performs hash-rewinding rather than hashing. Outputs a dictionary of all generated
    rewound hashes, mapped to the text that was rewound out of the hash.
    """
    print(f'Generating reverse hashes for {hex(starting_hash)}, pattern "[...]{suffix}" at depth {depth}')
    words = list(dict.fromkeys(dictionary)) # remove duplicate words while preserving order
    len_words = len(words)
    currents = [0 for _ in range(depth)]
    base_hash = remove_suffix(starting_hash, suffix)
    guess_stack: List[int] = [remove_suffix(base_hash, (words[0] * i)) for i in range(1,  depth + 1)]
    output_dict = {base_hash: suffix}

    print(words[0])

    # quick check for [0], [0][0], [0][0][0], etc., after this we only check on value change
    for k, init in enumerate(guess_stack, 1):
        full_str = words[0] * k
        curr_hash = remove_suffix(base_hash, full_str)
        output_dict[curr_hash] = full_str + suffix

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
                            guess_stack.append(remove_suffix(guess_stack[-1], words[currents[-k]]))
                        else:
                            print(words[currents[-k]])
                            guess_stack.append(remove_suffix(base_hash, words[currents[-k]]))
                        #if (match := crc32('/'.join([words[z] for z in currents[:(-k + 1) or None]]), prefix_hash)) in final_goals:
                        end_index = (-k + 1) or None
                        output_dict[guess_stack[-1]] = f'{''.join([words[i] for i in currents[:end_index][::-1]])}{suffix}'
                    break
    return output_dict

def find_middle(start1: int, start2: int, dictionary: List[str], prefix1: str, suffix1: str, prefix2: str, suffix2: str, depth: int):
    """
    Matches two hashes with differing suffixes, and identical but unknown prefixes. Haven't found many
    practical uses for this.
    """
    #print(f'Generating reverse hashes for {hex(starting_hash)}, pattern "[...]{suffix}" at depth {depth}')
    words = list(dict.fromkeys(dictionary)) # remove duplicate words while preserving order
    len_words = len(words)
    currents = [0 for _ in range(depth)]
    base1 = remove_suffix(start1, suffix1)
    base2 = remove_suffix(start2, suffix2)
    guess_stack: List[Tuple[int, int]] = [(remove_suffix(base1, (words[0] * i)), remove_suffix(base2, (words[0] * i))) for i in range(1, depth + 1)]

    print(words[0])

    # quick check for [0], [0][0], [0][0][0], etc., after this we only check on value change
    for k, init in enumerate(guess_stack, 1):
        full_str = words[0] * k
        hash1 = remove_suffix(base1, prefix1 + full_str)
        hash2 = remove_suffix(base2, prefix1 + full_str)
        if hash1 == hash2:
            print(f"{start_green}Match: {prefix1}{full_str}{suffix1}{end_color}")

    for i in range(pow(len_words, depth)):
        if i % 100000 == 0:
            print(f'{(i * 100 / pow(len_words, depth)):.2f}%')

        for j, place_val in enumerate(range(depth), 1):
            place = pow(len_words, place_val)
            if ((i % place) // place) == 0:
                currents[-j] = (currents[-j] + 1) % len_words
                guess_stack.pop()
                if currents[-j] != 0:
                    for k in range(j, 0, -1):
                        if len(guess_stack):
                            guess_stack.append(
                                (remove_suffix(guess_stack[-1][0], words[currents[-k]]),
                                 remove_suffix(guess_stack[-1][1], words[currents[-k]]))
                            )
                        else:
                            print(words[currents[-k]])
                            guess_stack.append(
                                (remove_suffix(base1, words[currents[-k]]),
                                 remove_suffix(base2, words[currents[-k]]))
                            )
                        if remove_suffix(guess_stack[-1][0], prefix1) == remove_suffix(guess_stack[-1][1], prefix2):
                            end_index = (-k + 1) or None
                            print(f"{start_green}Match: {prefix1}{''.join([words[i] for i in currents[:end_index][::-1]])}{suffix1}{end_color}")
                    break

def get_all_dirs():
    resource_obj = json.load(open('./output_json/mp_resource_names_confirmed.json', 'r'))
    cache = dict()

    for file in resource_obj:
        path = os.path.split(file)[0]
        while path != '$':
            path = os.path.split(path)[0]
            if (hashed_path := crc32(f'{path}/'.lower())) not in cache:
                cache[hashed_path] = path + '/'
    return cache

spacers = [' ', '_'] # '-'
gallery_words = ['resized', 'letterbox', 'letterboxed', 'ingame', 'scaled', 'downscale', 'downscaled', 'thumb', 'thumbnail', 'rescaled', 'scale', 'square', 'crop', 'cropped', '1024', 'test', '/common_textures', 'artgallery', 'art_gallery',  'artgalleries', 'art_galleries', '50', '25', '75', '100', '%', 'percent', 'one', 'two', 'three', 'txtrs', 'files', 'work', 'piece', 'pieces', 'working', 'collection', 'group', 'set', 'gal','album', 'pics', 'slide', 'slides', 'slideshow', 'slide_show', 'bonus', 'gallery','galery', 'galleries', 'concept','concepts', 'art', 'artwork', 'concept_art', 'conceptart', 'image', 'images', '/cooked', '/sourceimages','/source_images', 'textures', 'assets', *'01234abcd', '01', '02', '03', '00', '04']
env_dictionary = ['tallon', 'talloniv', 'tallon_iv', 'env', 'environment', 'enviroment', 'enviorment', 'environments', 'room', 'world', 'worlds', *gallery_words, '/', 's', *spacers]
samus_dictionary = ['gallery1', 'gallery_1','gallery0', 'gallery_0',  'player', 'suit', 'power_suit', 'varia_suit', 'powersuit', 'variasuit', 'samus', 'sam', 'samusaran', 'samus_aran', *gallery_words, '/', 's', *spacers]
creatures_dictionary = ['gallery2', 'gallery_2','gallery1', 'gallery_1',  'creatures', 'creature', 'tallon', 'talloniv', 'tallon_iv', 'biology', 'characters', 'character', 'enemies', 'enemy', 'species', 'aliens', 'alien', 'monsters', 'monster', 'critter', 'critters', *gallery_words, '/', 's', *spacers]
f1_dictionary = ['fusion', 'fusionsuit', 'fusion_suit', 'morphball', 'morph_ball', 'ball', 'maru_mari', 'marumari', *'12', '01', '02', '03', '00', *spacers]
f2_dictionary = ['fusion', 'fusionsuit', 'fusion_suit', 'gun', 'cannon', 'armcannon', 'arm_cannon', 'beam', *'12', '01', '02', '03', '00', *spacers]
mp_dictionary = ['met', 'metroid', 'prime','prime_', 'metroidprime','metroid_prime_','met_prime_', 'body', 'head', 'concept', *spacers]
flaa_words = ['flaaghra', 'flaahgra', 'flaagrah', 'flaahgraa', 'flagra', 'flaa', 'plantboss', 'plant_boss', 'plant_boss_creature', 'plant', 'boss', 'creature']
flaa_dir_words = [*flaa_words,  'work', 'working', 'anim', 'model', 'piece', 'part', 'top', 'cooked/', '/', 's', *spacers]
tex_words = [*'abc012345', 'color', 'col']
flaa_tex_words = [*flaa_words, *tex_words]

def main():
    """
    This is a big mess of all the partial hash matches I've attempted. Too lazy to clean it up currently.
    """
    depth = 4

    #set1 = generate_all_reverse_hashes(0x87185BA5, env_dictionary, '/stonehendge.txtr', depth)
    #set1 = generate_all_reverse_hashes(0x58152E28, samus_dictionary, '/x_ray_hand.txtr', depth)
    #set1 = generate_all_reverse_hashes(0x58152E28, samus_dictionary, '/x_ray_hand.txtr', depth)
    #set2 = generate_all_reverse_hashes(0x4eda49bc, ['/sourceimages', '/textures', '/', '/images',], '', depth)
    #set2 = generate_all_reverse_hashes(0x525C36BB, creatures_dictionary, '/triclops.txtr', depth)
    #set1 = generate_all_reverse_hashes(0x525C36BB, [*gallery_words, '/', 's', *spacers], 'triclops.txtr', depth)
    #set2 = generate_all_reverse_hashes(0xFBA0B516, [*gallery_words, '/', 's', *spacers], 'prime_front.txtr', depth)
    # set1 = generate_all_reverse_hashes(0xA753DBCD, ['darksamus', 'appears','_appears_', 'part','part1', 'part_1', 'ds', 'i', '1', 'one', 'dark_samus', 'storyboard', 'sb', 'story_board', *spacers], '1.txtr'.lower(), depth)
    # set2 = generate_all_reverse_hashes(0xEC8978B2, ['open', 'opening', 'intro', 'game', 'start', 'storyboard', 'sb', 'story_board', *spacers], '1.txtr'.lower(), depth)
    #set1 = generate_all_reverse_hashes(0x92BACDF5, ['grench', 'grenchler','s', 'art', 'concept', 'ingame', 'side', '0', '1', *spacers], '.txtr'.lower(), depth)
    #set1 = generate_all_reverse_hashes(0xCD098970, ['dark', 'suit', 'darksuit', 'dark_suit', '_1', 's', 'art', 'concept', '0', '1', 'ingame', *spacers], '.txtr'.lower(), depth)
    # set1 = generate_all_reverse_hashes(0x6703329F, ['screwattack', 'screw_attack', 's', '_1', '0', '1',  'art', 'concept', 'ingame', 'painting', 'color', *spacers], '.txtr'.lower(), depth)
    # set2 = generate_all_reverse_hashes(0x129EEA99, ['space', 'pirate', 'spacepirate', 'space_pirate', 's', '_1', '0', '1',  'art', 'concept', 'ingame', 'painting', 'color', *spacers], '.txtr'.lower(), depth)
    #set2 = generate_all_reverse_hashes(0x959F236E, ['space', 'flying', 'pirate', 'flying_pirate', 'flying_pirate', 's', '_1', '0', '1',  'art', 'concept', 'ingame', 'painting', 'color', *spacers], '.txtr'.lower(), depth)

    #set2 = generate_all_reverse_hashes(0x8AF881A4, ['face', 'head', 's', *flaa_tex_words, *spacers], 'flaahgraa_head.txtr', depth)
    #set2 = generate_all_reverse_hashes(0x9E628F99, ['blade', 'arm', 'scythe', 'sword', 'claw', 's', *flaa_tex_words, *spacers], '.txtr', depth)
    #set1 = generate_all_reverse_hashes(0x60468339, [*flaa_dir_words, 'sourceimages/'], 'flaahgraa_wings.txtr', depth)
    #set1 = generate_all_reverse_hashes(0xAD4ED949, [*flaa_dir_words, 'sourceimages/', 'textures/', 'common_textures/'], 'eyec.txtr', depth)
    #set2 = generate_all_reverse_hashes(0xbf5f05cd, [*flaa_dir_words, 'creature/'], 'cooked/plant_boss_creature.acs', depth)
    #set2 = generate_all_reverse_hashes(0xc0618706, [*flaa_dir_words, 'bottom/'], 'cooked/plant_boss_bottom.acs', depth)
    #set1 = generate_all_reverse_hashes(0x36AC7BBB, [*flaa_tex_words, *spacers, 'l', 'left', 'r', 'right', 'stem', 'trunk', 'tentacle', 'part', 'plant', 'root', 's'], '.txtr', depth)
    #set1 = generate_all_reverse_hashes(0x537D6747, [*flaa_tex_words, *spacers, 'stem', 'bomb_slot', 'bomb', 'slot', 'trunk', 'tentacle', 'part', 'plant', 'root', 's'], '.txtr', depth)
    #set2 = generate_all_reverse_hashes(0xBF097D30, [*flaa_tex_words, *spacers, 'l', 'left', 'r', 'right',  'stem', 'trunk', 'tentacle', 'part', 'plant', 'root', 's'], '.txtr', depth)
    #set1 = generate_all_reverse_hashes(0xBE226B20, [*flaa_tex_words, *spacers, 'base', 'ground', 'dirt', 'soil', 'floor', 's'], '.txtr', depth)
    #set2 = generate_all_reverse_hashes(0x9FB095D0, [*flaa_dir_words, *tex_words, 'sourceimages/', 'textures/', 'common_textures/', *spacers, 'pedal', 'bottom', 'base', 'claw', 'petal', 'very', 'top', 'flower', 'flesh', 's'], '.txtr', depth)
    #set2 = generate_all_reverse_hashes(0xB22871B2, ['reflected', 'refl', 'highlight_reflected', 'highlight', 'body', 'shell', *string.digits, 's', *flaa_tex_words, *spacers], '.txtr', depth)
    #set2 = generate_all_reverse_hashes(0xF7971653, ['spine', 'flsaghra_', 'torso', 'middle', 'mid', 'body', 'shell', 's', *flaa_tex_words, *spacers], 'flashgraa_torso.txtr', depth)

    #set1 = generate_all_reverse_hashes(0x309CC437, ['earth', 'mars', 'jupiter', 'red', 'orange', 'brown', 'gas', 'planet', 'plan', 'scan', '_left', '_right', '_l', '_r', '_4l', '_4r', '_2l', '_2r', 's', *'abc0123456789', *spacers], '.txtr', depth)
    #set2 = generate_all_reverse_hashes(0xE017773E, ['earth', 'mars', 'jupiter', 'red', 'orange', 'brown', 'gas', 'planet', 'plan', 'scan', '_left', '_right', '_l', '_r', '_4l', '_4r', '_2l', '_2r', 's', *'abc0123456789', *spacers], '.txtr', depth)

    # set1 = generate_all_reverse_hashes(0x71c6a9f5, ['concept', 'gesture', 'pose', 'poses', 'art', 'artwork', 'line', 'samus', 'pose', 'sketches', 'sketch', 'rough', 'doodle',  *'abcs01234', *spacers], '.txtr', depth)
    # set2 = generate_all_reverse_hashes(0x05c498f4, ['concept', 'gesture', 'pose', 'poses', 'art', 'artwork', 'line', 'samus', 'pose', 'sketches', 'sketch', 'rough', 'doodle', *'abcs01234', *spacers], '.txtr', depth)

    # set1 = generate_all_reverse_hashes(0x9666c937, ['block', 's', '/cooked', '1', *spacers], '/block1_moving.ani', depth)
    # set2 = generate_all_reverse_hashes(0x13aff63f, ['block', 's', '/cooked', '2', *spacers], '/block2_moving.ani', depth)

    #set1 = generate_all_reverse_hashes(0x5C111B00, ['jellyzap', 'jelly_zap', 'head', 'body', 'jaw', 'critter', 'u', 'upper', 'up', 'top', 'half', 'piece', 'chunk', 'gib', 's', 'bound', *'012abc', '/', *spacers], '.cmdl', depth)
    #set2 = generate_all_reverse_hashes(0x4D136895, ['jellyzap', 'jelly_zap', 'body', 'jaw', 'critter', 'l', 'lower', 'low', 'bottom', 'bot', 'half', 'piece', 'chunk', 'gib', 's', 'bound', *'012abc', '/', *spacers], '.cmdl', depth)

    #set1 = generate_all_reverse_hashes(0x706bd2cd, ['flame', 'jet', 'flamejet', 'nozzle', 'bound', 's', *spacers], '.cmdl', depth)
    #set2 = generate_all_reverse_hashes(0x092ffc78, ['flame', 'jet', 'flamejet', 'frozen', 'ice', 'bound', 's', *spacers], '.cmdl', depth)

    #set1 = generate_all_reverse_hashes(0x77EF87EC, ['tent', 'tentacle', 'arm', 'melee', 'attack', 'medium', 'med', 'ing', *'s/', '/cooked', *spacers], 'tentacle/B_ready_tent_medIng.ani'.lower(), depth)
    #set2 = generate_all_reverse_hashes(0x78CB664A, ['body', 'main', 'ball', 'sphere', 'orb', 'medium', 'med', 'ing', *'s/', '/cooked', *spacers], '/B_roar_medIng.ani'.lower(), depth)

    #set1 = generate_all_reverse_hashes(0x726fb01a, ['light', 'suit', 'samus', 'bound', '_bound', '_high_res', '_hi_res', '_hi_rez', '_high_rez', 'singleplayer', 'cine', 'cinematic', *'s/', '/cooked/', *spacers], '.cmdl'.lower(), depth)
    #set1 = generate_all_reverse_hashes(0x379527c0, ['dark', 'suit', 'samus', 'bound', '_bound', 'high', 'hi', 'rez', 'res', 'singleplayer', 'cine', 'cinematic', *'s/', '/cooked/', *spacers], '.cmdl'.lower(), depth)
    #set2 = generate_all_reverse_hashes(0x3a93b6f2, ['dark', 'grav', 'gravity', 'suit', 'samus', 'bound', '_bound', 'high', 'hi', 'rez', 'res', 'singleplayer', 'cine', 'cinematic', *'s/', '/cooked/', *spacers], '.cmdl'.lower(), depth)

    #set1 = generate_all_reverse_hashes(0x52f9b74d, ['head', 'core', 'essence', 'face', 'metroid', 'prime', 'boss', 'phase', 'stage', 'form', 'alpha', 'beta', 'gamma', 'new', *'012s', 'second', 'final', *spacers], '.afsm', depth)
    #set2 = generate_all_reverse_hashes(0x09689750, ['body', 'spider', 'crab', 'metroid', 'prime', 'boss', 'phase', 'stage', 'form', 'alpha', 'beta', 'gamma', 'new', *'012s', 'first', *spacers], '.afsm', depth)

    #set1 = generate_all_reverse_hashes(0x62c70ba2, [*spacers], 'Sand Temple Meeting 1.strg'.lower(), depth)
    #set2 = generate_all_reverse_hashes(0xae3c57d9, [*spacers], 'Trooper Dialog 1.strg'.lower(), depth)

    #set1 = generate_all_reverse_hashes(0x1BB549FB, ['medium', 'high', 'hi', 'large', 'pickup', *'s012', *spacers], '.rule'.lower(), depth)
    #set2 = generate_all_reverse_hashes(0x11497D6F, ['medium', 'low', 'lo', 'small', 'pickup', *'s012', *spacers], '.rule'.lower(), depth)

    #set1 = generate_all_reverse_hashes(0xBC5BC9FB, ['powerbomb', 'power bomb', 'wall', 'bomb', 'destructible', 'destructable', 'destroyable', 'breakable', 'scan', 'hint', 'new', *'012s', 'first', *spacers], '.strg', depth)
    #set2 = generate_all_reverse_hashes(0x6B8F94A6, ['dead', 'space pirate', 'pirate', 'corpse', 'log', 'commando', 'scan','new', *'012s', *spacers], '.strg', depth)

    #set1 = generate_all_reverse_hashes(0x118a0532, ['playergun', 'playergun/', 'samusarm', 'samus_arm', 'fsm', 'patterned/', 'player', 'player/', 'gun', 'samus', 'arm', 'player', 'anim', 'ctrl', 'control', 'controller', 'singleplayer', *'012/', 's', *spacers], '.afsm', depth)
    #set2 = generate_all_reverse_hashes(0x94d64095, ['playergun', 'playergun/', 'samusarm', 'samus_arm', 'fsm', 'patterned/', 'player', 'player/', 'gun', 'samus', 'arm', 'player', 'anim', 'ctrl', 'control', 'controller', 'singleplayer', *'012/', 's', *spacers], '.afsm', depth)

    #set1 = generate_all_reverse_hashes(0xab8473a5, ['metroid', '1', 'english', '/', 'copy', '(', ')', 'rs5', 's', *spacers], '/scan_data/!scans_intro_level/00g entrance to 00g begin.strg', depth)
    #set2 = generate_all_reverse_hashes(0x0444efed, ['metroid', '2', 'metroid2', '/', 'copy', '(', ')', 'rs5', 's', *spacers], '/ingame/completionscreen.strg', depth)

    # set1 = generate_all_reverse_hashes(0xc9a2a301, [*string.ascii_lowercase, *string.digits, *spacers], '', 1)
    # set2 = generate_all_reverse_hashes(0x57c636a2, [*string.ascii_lowercase, *string.digits, *spacers], '', 1)

    # set1 = generate_all_reverse_hashes(0x4739EE21, [*'0123abc', *spacers], '.txtr', depth)
    # set2 = generate_all_reverse_hashes(0xC9B6E9C2, [*'0123abc', *spacers], '.txtr', depth)
    # set3 = generate_all_reverse_hashes(0x051CE95C, [*'0123abc', *spacers], '.txtr', depth)

    #set1 = generate_all_reverse_hashes(0x7C934EC5, ['metroid', 'base', 'alpha', 'new', 'beta', 'gamma', 'red', 'plasma', '/sourceimages/', 'brain', 's', *spacers], 'brain.txtr', depth)
    #set1 = generate_all_reverse_hashes(0x667F6BE6, ['metroid', 'base', 'membrane', 'reflected', 'alpha', 'new', 'beta', 'gamma', '/sourceimages/', 's', *spacers], 'membrane_reflected.txtr', depth)
    #set2 = generate_all_reverse_hashes(0xD5C17775, ['metroid', 'base', 'membrane', 'reflected', 'alpha', 'new', 'beta', 'gamma', '/sourceimages/', 's', *spacers], 'membrane.txtr', depth)
    #set1 = generate_all_reverse_hashes(0xAA198954, ['metroid', 'base', 'beta', 'gamma', 'red', 'plasma', '/sourceimages/', 's', *spacers], 'plasma_base.txtr', depth)
    #set2 = generate_all_reverse_hashes(0xCE586110, ['metroid', 'base', 'refl', 'reflect', 'reflective', 'reflectivity', 'beta', 'gamma', 'generic', 'gray', '/sourceimages/', 's', *spacers], 'metroid_base_reflectivity.txtr', depth)
    #set2 = generate_all_reverse_hashes(0x7C934EC5, ['metroid', 'head', 'ball', 'reflected', 'refl', 'i', 'incan', 'beta', 'gamma', 'red', 'plasma', '/sourceimages/', 's', *spacers], '.txtr', depth)
    #set2 = generate_all_reverse_hashes(0x6037449E, ['metroid', 'base', 'gamma', 'yellow', 'power', '/sourceimages/', 's', *spacers], 'power_base.txtr', depth)

    #set1 = generate_all_reverse_hashes(0xA773BBFF, ['health', 'icon', 'i', 'healthicon', 'healthiconi', 'purple', 'wave', 'combo', 'beam', 'pickup', '/sourceimages/', '/', 's', *'w01234', *spacers], '.txtr', depth)
    #set2 = generate_all_reverse_hashes(0xB4AFD8E6, ['rocket', 'metal', 'icon', 'i', 'rocketicon', 'rocketiconi', 'purple', 'wave', 'combo', 'beam', 'pickup', '/sourceimages/', '/', 's', *'w01234', *spacers], '.txtr', depth)
    #set2 = generate_all_reverse_hashes(0xC35CF119, ['health', 'icon', 'i', 'healthicon', 'healthiconi', 'yellow', 'power', 'combo', 'beam', 'pickup', '/sourceimages/', '/', 's', *spacers], '.txtr', depth)

    #set1 = generate_all_reverse_hashes(0x5AA26425, ['eye', 'head', '2r', '2l', 'bi', 'r', 'l', 'persp', 'right', 'left', 'close', 'top', 'front', 's', *spacers], '.txtr', depth)
    #set2 = generate_all_reverse_hashes(0xAB39F694, ['body', 'full', '4r', '4l', 'quad', 'r', 'l', 'persp', 'right', 'left', 'top', 'front', 's', *spacers], '.txtr', depth)

    #set1 = generate_all_reverse_hashes(0x57D88247, ['pil', 'pillar', 'puzzle', 'central', 's', 'level','0', *spacers], '3.dcln', depth)
    #set2 = generate_all_reverse_hashes(0xA023FA97, ['debris', 'rubble', 's', 'blocker', 'wreckage', 'breakable', 'bombable', 'destructible', 'destructable', 'destroyable', 'p', 'power', 'bomb', 'powerbomb', 'power_bomb', 'bomb', *spacers], '.dcln', depth)
    #set2 = generate_all_reverse_hashes(0x387C670D, ['holo', 'hologram', 'pillar', 's', 'level', *'0123', *spacers], '3_hologram.cmdl', depth)

    #set1 = generate_all_reverse_hashes(0xAD54EC24, [''], 'fusion_gravity_head_chest.txtr', depth)
    #set1 = generate_all_reverse_hashes(0x4DBEBDB0, ['samus', 'e', 'face', 'head', 'eye', 'eyeball', 's', *'012abc', *spacers], '.txtr', depth)
    #set2 = generate_all_reverse_hashes(0x35A5F831, ['samus', 'e', 'face', 'head', 'eye', 'eyeball', 'reflectivity', 'refl', 'reflect', 's', *'012abc', *spacers], '.txtr', depth)
    #set2 = generate_all_reverse_hashes(0xA37FFBCF, ['samus', 'e', 'face', 'head', 'ponytail', 'pony', 'tail', 'hair', 's', *'012abc', *spacers], '.txtr', depth)

    #set1 = generate_all_reverse_hashes(0x77927F42, ['c', 'leg', 'arm', 'leg_arm', *'012abc', *spacers], 'leg_arm02.txtr', depth)
    #set2 = generate_all_reverse_hashes(0x757617A6, ['c', 'chozo', 'ghost', 'blue', *'012abc', 's', *spacers], 'chest.txtr', depth)
    #set1 = generate_all_reverse_hashes(0x9BFF8194, ['c', 'chozo', 'ghost', 'cloud', 'fog', 'glow', 'noise', 'smoke', 'blue',  *'012abcy', 's', *spacers], '.txtr', depth)

    #set1 = generate_all_reverse_hashes(0x8E03806F, ['4l', '4r', *spacers], '.txtr', depth)
    #set2 = generate_all_reverse_hashes(0xB7DFE384, ['4l', '4r', *spacers], '.txtr', depth)

    # set1 = generate_all_reverse_hashes(0x4A15F683, ['front', 'face', '4l', '4r', *spacers], '.txtr', depth)
    # set2 = generate_all_reverse_hashes(0x30FB9196, ['front', 'face', '4l', '4r', *spacers], '.txtr', depth)

    #set1 = generate_all_reverse_hashes(0x15CDCF8A, ['front', 'face', '4l', '4r', *spacers], '.txtr', depth)
    #set2 = generate_all_reverse_hashes(0x2C11AC61, ['front', 'face', '4l', '4r', *spacers], '.txtr', depth)

    #set1 = generate_all_reverse_hashes(0xD0556937, ['front', 'face', '4l', '4r', *spacers], '.txtr', depth)
    #set2 = generate_all_reverse_hashes(0xE9890ADC, ['front', 'face', '4l', '4r', *spacers], '.txtr', depth)

    # set1 = generate_all_reverse_hashes(0xDBF9EDD7, ['front', 'side', '4l', '4r', *spacers], '.txtr', depth)
    # set2 = generate_all_reverse_hashes(0xE2258E3C, ['front', 'side', '4l', '4r', *spacers], '.txtr', depth)
    #
    #set1 = generate_all_reverse_hashes(0x6F73821A, ['block', '4r', *spacers], '.cmdl', depth)
    #set1 = generate_all_reverse_hashes(0x9248589A, ['block', '14', 'tower', 'base', 'bound', 'static', 'tl', 'light', '/cooked/', *spacers], '_cracked.cmdl', depth)
    #set2 = generate_all_reverse_hashes(0x24445DFC, ['ring', '1' 'ring1' '14', 'tower', 'base', 'bound', 'static', 'tl', 'light', '/cooked/', *spacers], '.cmdl', depth)
    #set2 = generate_all_reverse_hashes(0x4AF88270, ['block', 'big', 'crack', 'cracked', 'color', 'col', '256', *'012cs', 'sourceimages/', *spacers], '.txtr', depth)
    #set1 = generate_all_reverse_hashes(0x4AF88270, ['block', 'big', 'crack', 'cracked', 'color', 'col', '256', *'012cs', *spacers], '.txtr', depth)
    #set2 = generate_all_reverse_hashes(0xF0CCE9A4, ['block', 'big', 'crack', 'cracked', 'color', 'col', '256', 'top', *'012cs', *spacers], '.txtr', depth)

    #set1 = generate_all_reverse_hashes(0xDE1EACC9, ['lock', 'door', 'new', 'metroid', *'012s/', *spacers], '/cooked/into_open_lock.ani', depth)
    #set2 = generate_all_reverse_hashes(0x2CAB87C6, ['lock', 'door', 'new', 'metroid', *'012s/', *spacers], '/cooked/into_open_door.ani', depth)

    #set1 = generate_all_reverse_hashes(0x959F236E, ['space', 'pirate', 'sp', 'space_pirate', 'elite', 'flying', 'aero', 'trooper', 'commando', 'dark', 'light', 'render', 'art', 'sketch', 'rough', 'concept', *'s012345', '-', *spacers], '.txtr', depth)
    #set2 = generate_all_reverse_hashes(0x2CAB87C6, ['space', 'pirate', 'sp', 'space_pirate', 'elite', 'flying', 'aero', 'trooper', 'commando', 'dark', 'light', 'render', 'art', 'sketch', 'rough', 'concept', *'s012345', '-', *spacers], '.txtr', depth)

    #set1 = generate_all_reverse_hashes(0x0151FA12, ['ing', 'warrior', 'minor', 'medium', 'large', 'render', 'art', 'concept', *'s012345', '-', *spacers], '02.txtr', depth)
    #set2 = generate_all_reverse_hashes(0x9049CB6B, ['ing', 'warrior', 'minor', 'medium', 'large', 'render', 'art', 'concept', *'s012345', '-', *spacers], '.txtr', depth)
    #set2 = generate_all_reverse_hashes(0x0CBB418E, ['ing', 'warrior', 'minor', 'medium', 'large', 'render', 'art', 'concept', *'s012345', '-', *spacers], '1.txtr', depth)
    #set1 = generate_all_reverse_hashes(0x806C74C9, ['luminoth', 'moth', 'lord', 'u-mos', 'umos', 'light', 'render', 'art','concept', *'s012345', '-', *spacers], '_04.txtr', depth)
    #set2 = generate_all_reverse_hashes(0x440A7105, ['luminoth', 'moth', 'lord', 'u-mos', 'umos', 'light', 'render', 'art','concept', *'s012345', '-', *spacers], '.txtr', depth)

    #set1 = generate_all_reverse_hashes(0xfd37b1da, ['lava_burningtrail', 'burningtrail','burning', 'trail', 'over', 'lava', '_over_', '_lava_', 'world',  '23', '/work', '/working' '/sourceimages', *string.digits, *spacers], '/lavaground1c.txtr', depth)
    #set2 = generate_all_reverse_hashes(0xd7619569, ['lava_pickup', 'pickup','over', 'lava', '_over_', '_lava_', 'world', '09', '/work', '/working', '/sourceimages', *string.digits, *spacers], '/lavaground1c.txtr', depth)

    set1 = generate_all_reverse_hashes(0x43D80592, ['/cooked/', 'ice', 'glow', 'static', 'bound', 'static', 'iceglow', 'ice_glow', *spacers], '.cmdl', depth)
    set2 = generate_all_reverse_hashes(0xB64EDA45, ['/cooked/', 'crack', 'cracked', 'crackedstalactite', 'cracked_stalactite', 'ice', 'icicle', 'icecle', 'stalactite', 'bound', 'static', *spacers], '.cmdl', depth)

    #set1 = generate_all_reverse_hashes(0x67990498, ['monitortower','monitor', 'tower', 'over', 'lava', '_over_', '_lava_',  '09', *string.digits, *spacers], '/sourceimages/cable02c.txtr', depth)
    #set2 = generate_all_reverse_hashes(0x6612DB50, ['pickup','over', 'lava', '_over_', '_lava_', '09', *string.digits, *spacers], '/sourceimages/cable02c.txtr', depth)
    #set2 = generate_all_reverse_hashes(0xECCB2D72, ['lavahole', 'c', 'i', 'light', *spacers], '.txtr', 4)

    #set1 = generate_all_reverse_hashes(0x5b915c78, ['02_drawbridge', '02', 'temple', 'exploration', '02_exploration', '02_temple_exploration', 'area', 'drawbridge', 'bound', *'012s/', '/cooked', '/objects', *spacers], '/cooked/02_drawbridge_ready.ani', depth)
    #set2 = generate_all_reverse_hashes(0xe1ba6d6e, ['03_crate_cable', '03_crate', '03_temple_combattraining', '03_combattraining', '03', 'temple', 'combattraining', 'combat', 'training', 'area', 'crate_cable', 'crate', 'cable', '/objects', '/cooked', *'0123s/', *spacers], '/cooked/03_crate_cable_snap.ani', depth)

    #set1 = generate_all_reverse_hashes(0xA6B99BA3, ['randomizer', 'random', 'pickup', 'base', 'bound', 'static', '_bound', 'platform', 'multi', 'multiplayer', *'0126s/', '/cooked/', *spacers], '.dcln'.lower(), depth)
    #set1 = generate_all_reverse_hashes(0xC2E755BF, ['manned', 'bound', '_bound', 'turet', 'anim', 'samus', 'pirate', 'top', 'gun', 'turret', 'turret_ball', 'ball', 'player', 'hologram', 'holo', 'multi', 'multiplayer','/cooked', *'012s', *spacers], '/holo_spin.ani'.lower(), depth)
    #set2 = generate_all_reverse_hashes(0x893CAD1C, ['manned', 'bound', '_bound', 'turet', 'anim', 'samus', 'pirate', 'top', 'gun', 'turret', 'turret_ball', 'ball', 'player', 'multi', 'multiplayer', *'012s','/cooked', *spacers], '/turret_90_down_additive.ani'.lower(), depth)

    # set1 = generate_all_reverse_hashes(0xCB2D7AE0, ['06_ice_temple/06_ice_temple.','06_ice_temple/cooked/06_ice_temple.', '06_ice_temple.', *string.ascii_lowercase, *spacers], '', depth)
    # set2 = generate_all_reverse_hashes(0x2987144D, ['generic_z6/generic_z6.', 'generic_z6/cooked/generic_z6.', 'generic_z6.', *string.ascii_lowercase, *spacers], '', depth)

    # set0 = generate_all_reverse_hashes(0xe9b1a835, [*'012345'], '.txtr', depth)
    # set1 = generate_all_reverse_hashes(0x22ed7b90, [*'012345'], '.txtr', depth)
    # set2 = generate_all_reverse_hashes(0x3fe84b28, [*'012345'], '.txtr', depth)
    # set3 = generate_all_reverse_hashes(0xb97c3986, [*'012345'], '.txtr', depth)
    # set4 = generate_all_reverse_hashes(0x7220ea23, [*'012345'], '.txtr', depth)
    # set5 = generate_all_reverse_hashes(0xf4b4988d, [*'012345'], '.txtr', depth)
    #
    # for txtr_hash in set0:
    #     if txtr_hash in set1 and txtr_hash in set2 and txtr_hash in set3 and txtr_hash in set4 and txtr_hash in set5:
    #         print(f'{set0[txtr_hash]}\n{set1[txtr_hash]}\n{set2[txtr_hash]}\n{set3[txtr_hash]}\n{set4[txtr_hash]}\n{set5[txtr_hash]}\n')

    for txtr_hash in set1:
        if txtr_hash in set2:
            print(f'{set1[txtr_hash]}\n{set2[txtr_hash]}\n')
    #
    # for txtr_hash in set1:
    #     if txtr_hash in set2 and txtr_hash in set3:
    #         print(f'{set1[txtr_hash]}\n{set2[txtr_hash]}\n{set3[txtr_hash]}\n')

if __name__ == '__main__':
    #find_middle(0x58152E28, 0x525C36BB, [*gallery_words, '/', 's', *spacers], '1/', '/x_ray_hand.txtr', '2/', '/triclops.txtr', 3)
    #find_middle(0x7E37BC82, 0xA99E8D37,['/',*gallery_words,  's', *spacers], 'metroid',  'metroid_base.txtr','minnow', 'minnowc.txtr', 4)
    # find_middle(0x95DAA36B, 0xE1193C3D,[*spacers, 'ring', 'tower', 'light', 'tl', 'base', '/cooked/', '14_', '_bound', 'anim', *'0123', 'middle', 'mid', 's', '/', 'very', 'hi', 'high', 'low'], '1/cooked/',  '1.cmdl','2/cooked/', '2.cmdl', 4)
    main()