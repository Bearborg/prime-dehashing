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
import itertools
import sqlite3
from utils.crc32 import crc32, remove_suffix
from typing import List, Dict
import string

start_green = '\033[92m'
end_color = '\033[0m'

prime_boss_words = ['metroid','prime','head','body','spider','exo','core','essence','boss','new','stage','phase','0','1','2','/',]
artifact_scan_words = [ 'chozo', 'holo', 'hologram', 'artifact', 'hint', 'space ', 'pirate', 'pirate log', '002', '003', '006', '012', '018', '019', '020', '023', 'scan']
digits = [str(n) for n in range(21)] + ['{:02}'.format(n) for n in range(1, 10)]
small_digits = ['0', '1', '2', '3', '01', '02', '03']
spacers = [' ', '_'] # '-'
tex_words = [ 'a', 'b', 'c', 'i', 'y', 's', 'color', 'reflected', 'reflectivity', 'new']
rare_tex_words = ['incan', 'incandes', 'incandescent', 'incandesant', 'incandescence', 'refl', 'reflect', 'reflectance', 'reflective', 'reflection']
colors = ['red', 'purple', 'green', 'orange', 'blue', 'cyan', 'amber', 'white', 'black', 'grey', 'gray', 'yellow', 'brown']
world_tex_words = [
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
ruin_words = ['mud', 'muddy', 'cord', 'corded', 'mold', 'molded', 'spike', 'spider', 'monkey', 'claw', 'tendril', 'rust', 'rusty', 'moss', 'mossy', 'chozo', 'rune', 'glyph', 'symbol', 'symbols', 'writing', 'sand', 'vine', 'tree', 'leaf', 'leaves', 'bark', 'brick', 'bricks', 'hieroglyph', 'heiroglyph', 'hieroglyphic', 'heiroglyphic', 'statue', 'carving', 'carved', 'bird', 'bronze', 'copper', 'dust']
ice_words = ['snow', 'snowy', 'frost', 'frosty', 'ice', 'icy', 'frozen', 'icicle', 'cave', 'temple', 'iced', 'crystal', 'gravity', 'stalactite', 'stalagmite']
over_words = ['mud', 'muddy', 'spider', 'canopy', 'root', 'dandelion', 'star', 'shovel', 'moss', 'vine', 'grass', 'sand', 'leaf', 'leaves', 'tree', 'trunk', 'bark', 'mossy', 'fern', 'lichen', 'ivy', 'plant', 'mud', 'wet', 'riverbed', 'sulfur', 'granite', 'limestone', 'lime', 'glow', 'foliage']
lava_words = ['lava', 'magma', 'ember', 'embers', 'mud', 'muddy', 'capacitor', 'crystal', 'molten', 'hot', 'heated', 'ash', 'cinder', 'cooled', 'volcanic']
mine_words = ['shaft', 'mine', 'gravel', 'track', 'cement', 'dirt', 'shroom', 'mushroom', 'fungus', 'fungal', 'phason', 'phazon', 'phas', 'phaz']
crater_words = ['spider', 'web', 'webbing', 'bone', 'membrane', 'floss', 'egg', 'alive', 'dead', 'glow', 'glowing', 'vein', 'cancer', 'barnacle', 'growth', 'pale', 'sphincter', 'pucker', 'tumor', 'scab', 'flesh', 'brain', 'nub', 'organ', 'tissue', 'tooth', 'teeth', 'phazon', 'phason', 'phaz', 'phas', 'cell']
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
pwe_list = [word.strip().lower() for word in open(r'word_lists/PWE_WordList.txt', 'r').read().split('\n')]
pwe_huge_list = [word.strip().lower() for word in open(r'word_lists/PWE_WordList_large.txt', 'r').read().split('\n')]
pwe_bad_list = [word.strip().lower() for word in open(r'word_lists/PWE_WordList_old.txt', 'r').read().split('\n')]
world_words = [word.strip().lower() for word in open(r'word_lists/world_tex_words.txt', 'r').read().split('\n')]
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
    'fla',
    'flaa',
    'flagra',
    'flaaghra',
    'flaahgra',
    'flaahgraa',
    'plant',
    'boss',
    'creature',
    'boss_creature',
    'plant_boss',
    'plantboss',
    # 'plant_creature',
    # 'top',
    'ra',
    'ghra',
    'hgra',
    'g',
    'h',
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
scan_tex_suffixes = ['l', 'r', '2l', '2r', '4l', '4r']
scan_tex_suffixes_rare = [
    '1',
    'one',
    '2',
    'two',
    '3',
    'three',
    '4',
    'four',
    'l',
    'left',
    'r',
    'right',
    '1l',
    '2l',
    '2la',
    '2lb',
    '3l',
    '4l',
    'half_4l',
    '4la',
    '4lb',
    '4l2',
    '1r',
    '2r',
    '2ra',
    '2rb',
    '3r',
    '4r',
    'half_4r',
    '4ra',
    '4rb',
    '4r2',
    'lr',
    'quad',
    'quad_1',
    'quad_2',
    'bi',
    'bi_1',
    'bi_2',
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

effect_prefixes = [
    "$/Effects/particles/bosses/introBoss/Beam/",
    "$/Effects/particles/bosses/introBoss/BeamSplash/",
    "$/Effects/particles/bosses/introBoss/elem/",
    "$/Effects/particles/bosses/introBoss/",
    "$/Effects/particles/bosses/introBoss/NewCharge/",
    "$/Effects/particles/bosses/PlantBoss/",
    "$/Effects/particles/characters/AtomicAlpha/",
    "$/Effects/particles/characters/AtomicBeta/",
    "$/Effects/particles/characters/Babygoth/",
    "$/Effects/particles/characters/Bloodflower/",
    "$/Effects/particles/characters/ChozoGhost/",
    "$/Effects/particles/characters/Drone/",
    "$/Effects/particles/characters/garganBeetle/",
    "$/Effects/particles/characters/Jellyzap/",
    "$/Effects/particles/characters/Magdalite/",
    "$/Effects/particles/characters/Metaray/",
    "$/Effects/particles/characters/Metroid/",
    "$/Effects/particles/characters/Metroid_Beta/",
    "$/Effects/particles/characters/Oculus/",
    "$/Effects/particles/characters/Parasite/",
    "$/Effects/particles/characters/Parasite/MasterSystem/",
    "$/Effects/particles/characters/PuddleSpore/",
    "$/Effects/particles/characters/Ridley/",
    "$/Effects/particles/characters/Samus/",
    "$/Effects/particles/characters/Samus/morphball/",
    "$/Effects/particles/characters/Samus/morphball/boostattack/",
    "$/Effects/particles/characters/Samus/morphball/deathball/outside/",
    "$/Effects/particles/characters/Samus/morphball/deathball/spikes/",
    "$/Effects/particles/characters/Samus/morphball/transition/",
    "$/Effects/particles/characters/Samusball/",
    "$/Effects/particles/characters/Samusball/work/",
    "$/Effects/particles/characters/Samusgun/",
    "$/Effects/particles/characters/SamusShip/",
    "$/Effects/particles/characters/Sheegoth/",
    "$/Effects/particles/characters/SpacePirate/",
    "$/Effects/particles/characters/SpacePirate/EmptyWeapon/",
    "$/Effects/particles/characters/SpacePirate/NewBlood/",
    "$/Effects/particles/characters/SpacePirate/NewerWeapon/",
    "$/Effects/particles/characters/SpacePirate_Elite/",
    "$/Effects/particles/characters/SpacePirate_Flying/",
    "$/Effects/particles/characters/SpacePirate_Flying/NewJetPack/",
    "$/Effects/particles/characters/SpacePirate_Trooper/",
    "$/Effects/particles/characters/",
    "$/Effects/particles/characters/SpankWeed/",
    "$/Effects/particles/characters/spiderball/",
    "$/Effects/particles/characters/Turret/",
    "$/Effects/particles/characters2/MinorIng/",
    "$/Effects/particles/characters2/samus/screwattack_walljump/work/",
    "$/Effects/particles/characters2/spacepirate/weapon/work/",
    "$/Effects/particles/cinematics/02_Intro_elevator/",
    "$/Effects/particles/cinematics/09_Intro_Ridley_Chamber/",
    "$/Effects/particles/cinematics/AfterCredits/",
    "$/Effects/particles/cinematics/IntroShipExplosion/",
    "$/Effects/particles/cinematics/SaveStation/",
    "$/Effects/particles/cinematics/SaveStation/Station1/",
    "$/Effects/particles/cinematics/ShipLanding_Overworld/",
    "$/Effects/particles/cinematics/SuitPickUp/",
    "$/Effects/particles/cinematics/SuitPickUp/New6_20_02/",
    "$/Effects/particles/cinematics/ThardusIntro/",
    "$/Effects/particles/darkworld/",
    "$/Effects/particles/decals/",
    "$/Effects/particles/enemy_weapons/pirates/pirate_hitSplash/elem/",
    "$/Effects/particles/enemy_weapons/pirates/pirate_hitSplash/",
    "$/Effects/particles/enemy_weapons/pirates/space_pirate/",
    "$/Effects/particles/FluidSplashes/NewSplashes/",
    "$/Effects/particles/gibs/",
    "$/Effects/particles/ice/",
    "$/Effects/particles/intro/02_elev/",
    "$/Effects/particles/intro/02Intro_elevator/",
    "$/Effects/particles/intro/08Venthall_Effects/",
    "$/Effects/particles/intro/0c_connect/",
    "$/Effects/particles/intro/",
    "$/Effects/particles/intro/elevetrorLights/",
    "$/Effects/particles/intro/Explosions/",
    "$/Effects/particles/intro/group04/C/",
    "$/Effects/particles/intro/group04/D/",
    "$/Effects/particles/intro/group05/A/",
    "$/Effects/particles/intro/group05/D/",
    "$/Effects/particles/intro/meteor/",
    "$/Effects/particles/intro/ReactorEffect/AnotherReactor/",
    "$/Effects/particles/intro/ReactorEffect/",
    "$/Effects/particles/intro/ReactorEffect/Explosion/",
    "$/Effects/particles/intro/ReactorEffect/NewReactor/",
    "$/Effects/particles/intro/sparks/",
    "$/Effects/particles/intro/SpecimanChamber/",
    "$/Effects/particles/ModelParticles/",
    "$/Effects/particles/ModelParticles/working/",
    "$/Effects/particles/MTEST/",
    "$/Effects/particles/multiplayer/entanglergibs/",
    "$/Effects/particles/multiplayer/morphballgibs/work/",
    "$/Effects/particles/newsamusweapons/annihilatorbeam/v3/charge/work/2ndaryfx/",
    "$/Effects/particles/newsamusweapons/annihilatorbeam/v3/combo/",
    "$/Effects/particles/newsamusweapons/darkbeam/2ndaryfx/burst/",
    "$/Effects/particles/newsamusweapons/echovisorfx/",
    "$/Effects/particles/newsamusweapons/lightbeam/charge/work/collisionfx/",
    "$/Effects/particles/newsamusweapons/missilecharge/work/",
    "$/Effects/particles/newsamusweapons/newmissile/work/",
    "$/Effects/particles/newsamusweapons/newsupermissile/work/",
    "$/Effects/particles/overworld/03_over/",
    "$/Effects/particles/pickups/",
    "$/Effects/particles/pickups/ryanwork/",
    "$/Effects/particles/pyro/powerbeamexplosion/sparks/",
    "$/Effects/particles/pyro/powerbeamexplosion/",
    "$/Effects/particles/pyro/response/",
    "$/Effects/particles/pyro/smExpl/elem/",
    "$/Effects/particles/pyro/smExpl/",
    "$/Effects/particles/ruins/Group01/B/",
    "$/Effects/particles/sam_weapon/beam/ice/elem/",
    "$/Effects/particles/sam_weapon/beam/ice/",
    "$/Effects/particles/sam_weapon/beam/plasma/2ndaryfx/",
    "$/Effects/particles/sam_weapon/beam/plasma/elem/",
    "$/Effects/particles/sam_weapon/beam/plasma/flamethrower/",
    "$/Effects/particles/sam_weapon/beam/plasma/",
    "$/Effects/particles/sam_weapon/beam/power/2ndaryfx/",
    "$/Effects/particles/sam_weapon/beam/wave/2ndaryfx/",
    "$/Effects/particles/sam_weapon/beam/wave/",
    "$/Effects/particles/sam_weapon/bomb/elements/",
    "$/Effects/particles/sam_weapon/bomb/elements/bombb/bombstart/",
    "$/Effects/particles/sam_weapon/bomb/elements/bombb/",
    "$/Effects/particles/sam_weapon/bomb/elements/bombd/explode/",
    "$/Effects/particles/sam_weapon/bomb/elements/bombd/",
    "$/Effects/particles/sam_weapon/bomb/",
    "$/Effects/particles/sam_weapon/bomb/superbomb/",
    "$/Effects/particles/sam_weapon/charge/",
    "$/Effects/particles/sam_weapon/combo/plasmacombo/",
    "$/Effects/particles/sam_weapon/combo/transferfx/",
    "$/Effects/particles/sam_weapon/combo/WaveCombo/",
    "$/Effects/particles/sam_weapon/frozenmodels/",
    "$/Effects/particles/sam_weapon/grapple/",
    "$/Effects/particles/sam_weapon/missile/smmissile/explosion/andyexplosion_high/",
    "$/Effects/particles/sam_weapon/missile/supermissile/explosion/",
    "$/Effects/particles/sam_weapon/missile/supermissile/explosion/newexplosionandy2/",
    "$/Effects/particles/sam_weapon/missile/supermissile/",
    "$/Effects/particles/sam_weapon/muzzlesmoke/",
    "$/Effects/particles/steam/",
    "$/Effects/particles/various/",
    "$/Effects/particles/various/EnemyGoo/New Goo/",
    "$/Effects/particles/various/HiveFire/",
    "$/Effects/particles/various/VisorFx/2ndaryWater/",
    "$/Effects/particles/various/VisorFx/",
    "$/Effects/particles/various/VisorFx/frozenvisor/",
    "$/Effects/working/alex/",
    "$/Effects/working/bethwork/",
    "$/Effects/working/chuckwork/",
    "$/Effects/working/chuckwork/flame/",
    "$/Effects/working/DonWork/",
    "$/Effects/working/elben/intro/",
    "$/Effects/working/irving/blackhole/",
    "$/Effects/working/irving/imploder/",
    "$/Effects/working/irving/missilechargefx/",
    "$/Effects/working/leeWork/",
    "$/Effects/working/leeWork/Sparks/",
    "$/Effects/working/luisWork/",
    "$/Effects/working/luisWork/0b_sparksGPSM.PART",
    "$/Effects/working/Marco/",
    "$/Effects/working/Ryanwork/",
    "$/Effects/working/Ryanwork/electric/",
    "$/Effects/working/Ryanwork/fire/",
    "$/Effects/working/Ryanwork/health/",
    "$/Effects/working/todwork/",
    "$/Experiments/irving/effects/",
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
#dictionary = ['zoomer', 'grisby', 'grizby', 'piece', 'part', 'arm', 'leg', 'hip', 'thigh', 'armor', 'armour', 'left', 'l', 'right', 'r', '/', *'012', *spacers]
#dictionary = ['new', *flaahgra_words, *character_words, 'test', 'work', 'working', 'body', 'cine', 'cinematic', 'component', 'set', 'animation', 'animated', 'anim', 'tree', 'blood_flower', 'phason', 'phazon', 'poison', 'poisonous', 'toxic', 'ruin', 'ruins', 'bosses', 'metroid', 'chozoruins', 'chozo_ruins', 'ruinsworld', 'ruinworld', 'flower', 'piece', 'part', 'version', 'char', 'character', 'version', 'v', '/cooked', '/scenes', *'()/s012.!', *spacers]
#dictionary = [*flaahgra_words, *char_tex_words, 'f', 'p', 'b', 'eye', 'eyes', 'eyeball', 'face', 'orange', 'glow', 'glowing', 's', *tex_words, *small_digits, *spacers]
#dictionary = ['wave', 'beam', 'charge', 'v', 'version', 'projectile', 'main', 'new', 'cinema', 'shot', 'weapon', '0', '1', '2', '3', '4', '/', 's', *spacers]
#dictionary = [*pwe_list, *spacers]
#dictionary = ['sapsack', 'broken', 'damaged', 'damage', 'destroyed', 'destroy', 'dead', 'exploded', 'core', 'debris', 'pit', 'sap', 'sack', 'sac', 's', *string.digits,  *spacers]
#dictionary = [*string.ascii_lowercase]
#dictionary = ['metroid', 'prime', 'swamp', 'world', *'12345!.', '/swamp_world', '/swampworld', '/', 's', *spacers]
#dictionary = ['bogus', 'phaz', 'phas', 'phase', 'veins', 'phazon', 'phason', 'gun', 'cannon', 'casing', 'incan', 'reflectivity', 'dark', 'light',  's', *spacers]
#dictionary = ['/', '/sourceimages/', 'garbeetle', 'garganbeetle', 'gargantuanbeetle', 'gargantuan_beetle', 'gar_beetle', 'beetle', 'beta', 'alpha', 'gamma', *tex_words, *rare_tex_words, *char_tex_words, *small_digits, *spacers]
#dictionary = ['big', 'bug', 'butt', 'hive', 'part', 'piece', 'gib', 'tail', 'ass', 'gaster', 'rear', 'back', 'backside', 'split', 'gar', 'garbeetle', 'beta_garbeetle', 'garg', 'gargan', 'gargant', 'gargantu', 'gargantua', 'gargantuan', 'beetle', 'boss', 'body', 'front', 'half', 'beta', 'alpha', 'gamma', 'bound', '_bound', *'v012', 'new', 'newer', *spacers]
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
#dictionary = [ 'metroid', 'sentry', 'security', 'drone', 'drones', *character_words, 'new', 'invis', 'invisible', 'visible', 'normal', 'generic', 'water', 'air', 'and', 'aqua', 'boss', 'pirate', 'space_pirate', 'spacepirate', 'sp', 'flying', 'laser', 'robot', 'bot', 'hover', 'fly', 'flyer', 'float', 'floating', *'0123', 's', '-', '/', *spacers]
#dictionary = [ 'atomic', 'atom', *character_words, 'new', 'spin', 'spinner', 'bombu', 'bomb', *'0123', 's', '-', '/', *spacers]
#dictionary = ['frontend', 'flipbook', 'slideshow', 'artgallery', 'art_gallery', 'gallery1', 'gallery_1', 'artgalleries', 'art_galleries', '50', '25', '75', '100', '%', 'percent', 'slide_show', 'samus', 'bonus', 'gallery', 'galleries', 'concept', 'art', 'artwork', 'concept_art', 'conceptart', 'cooked/', 'sourceimages/', 'textures/', 'assets/', *'01234', '01', '02', '03', '00', '04', '/', 's', *spacers]
#dictionary = ['env', 'environment', 'enviorment', 'enviroment', 'mine', 'mines', 'phason', 'phazon', 'phaz', 'mushroom', 'shroom', 's', *spacers]
# dictionary = ['stalactite', 'icicle', 'breakable', 'destructable', 'destructible', 'destroyable', 'missile', 'missle', *'012', 's', *scan_tex_words, *scan_tex_suffixes, *spacers]
#dictionary = ['samus', 'e3', 'promo', 'render', 'game', 'end', 'game_end', 'gameend', 'box', 'cover', 'sketch', 'sketches', 'concept', 'gesture', 'gestures', 'pose', 'poses', 'art', 'artwork', 'varia', 'suit', 'variasuit', 'varia_suit', 'line', 'color', 's', *'0123', *spacers]
#dictionary = ['samus', 'rough',  'board', 'e3', 'render', 'doodle', 'metroid', 'gun', 'arm', 'cannon', 'canon', 'charge', 'power', 'beam', 'bonus', 'detail', 'details', 'note', 'notes', 'sketch', 'sketches', 'concept', 'pose', 'poses', 'art', 'artwork', 'line', 'color', 's', *'0123', *spacers]
#dictionary = ['ending', 'storyboard', 'sb', 'board', 'story', 'comic', 'panel', 'rough', 'end', 'game', 'scene', 'cutscene', 'detail', 'details', 'note', 'notes', 'sketch', 'sketches', 'concept', 'art', 'artwork', 'line', 'color', 's', *'0123', *spacers]
#dictionary = ['cinematic', 'cine', 'samusgun', 'samus_gun', 'power', 'beam', 'gun', 'high', 'low', '/', 'bound', '_bound', 's', *spacers]
#dictionary = ['01_', '01 ', '01', *'abc', 'test', 'name', 'player', 'spawn', 'point', 'work', 'dummy', 'room', '1_', '0', 'o', '1', '.', '!', 'save', 'station', 'savestation', 'save_station', 'plazza', 'samus', 'demo', 'overworld', 'main', 'plaza', 'start', 'intro', 'first', 'gunship', 'starting', 'game', 'mainplaza', 'main_plaza', 'main plaza', 'crashed', 'crash', 'ship', 'world', 'landing', 'site', 'over_', 'over', 'lava_', 'introunderwater_', 's', *spacers]
#dictionary = ['01_', '01 ', '01', *'abcv', 'new', 'test', 'name', 'player', 'spawn', 'point', 'work', 'dummy', 'room', '1_', '0', '1', 'save', 'station', 'savestation', 'save_station', 'plazza', 'samus', 'overworld', 'main', 'plaza', 'start', 'intro', 'first', 'gunship', 'starting', 'game', 'mainplaza', 'main_plaza', 'main plaza', 'ship', 'world', 'landing', 'site', 'over_', 'over', 'lava', 'introunderwater', 's', *spacers]
#dictionary = ['00j', 'over_hall_holo', 'anim', 'animating', 'animated', '00j_', '0j_', 'orange', 'space_pirate', 'artefact', 'key', 'lock', 'rotate', 'rot', 'rotating', 'rotation', 'over', 'hall', 'over_hall', 'overworld', 'hallway', 'temple', 'temp', 'stonehenge', 'holo', 'lore', 'hint', 'pirate', 'sp', *'012', '_bound', 'hologram', 'chozo', 'chozo_artifact', 'chozoartifact', 'artifact', 's', *spacers]
#dictionary = ['samus', 'mp', 'battle', 'meet', 'begin', 'fight', 'walk', 'up', 'ready', 'flinch', 'incubate', 'met', 'metroid', 'metroid_prime', 'prime', 'body', 'spider', 'head', 'animated', 'intro', 'anim', 'cine', 'cinema', 'cinematic', *'012', *spacers]
#dictionary = ['06_', '04_', '07_', 'intro', 'floating', 'crashed', 'crash', 'crashedship', 'ship', 'underwater', 'under', 'introunderwater', 'part', 'parts', 'piece', 'pieces', 'obj', 'object', 'block', 'blocker', 'reactor', 'spec', 'specimen', 'specimen_chamber', 'speciman', 'chamber', 'freight', 'type', 'types', 'lifts', 'freight_lifts', 'freight_lift', 'debris', 'platform', 'animated', 'anim', *'012', 's', '/', '/cooked', *spacers]
#dictionary = ['19', 'ice', 'thardus', 'rock', 'node1', 'death', 'dead', 'outro',  'pebble', 'hit', 'hitinhead', 'hitin_head','in', 'head', 'float','floating', 'cine', 'cinematic', 'cinema', 'samus', 'anim', 'animated', 'mud', 'inyoass', 'in_yo_ass', 's', 'bound', *'012', '/', *spacers]
#dictionary = ['skra', 'skrahell', 'shell', 'skrashell', 'zoomer', 'eyeball', 'eye', 'eyes', 'ocu', 'oculus', 'under', 'bottom', 'bot', 'underside', *'012abcd', 'new', 'light', 'dark', 'lighter', 'darker', *tex_words, *rare_tex_words, *spacers]
#dictionary = ['samus', 'morph', 'low', '/cooked/', 'lo', 'rez', 'res', 'into', 'ball', 'transition', 'transform', 'transformation', 'furl', 'unfurl', *spacers]
#dictionary = ['variasuit', 'varia', 'varia_suit', 'gravitysuit', 'gravity', 'gravity_suit', 'low', '_low', '/sourceimages/', 'low_rez', 'low_res', *spacers]
#dictionary = ['samus', 'samus_', 'metal', 'spin', 'spinner', 'gravity', 'gravity_suit', 'low_rez', 'low_res', 'low_poly', 'lowpoly','low', 'variasuit', 'varia', 'varia_', 'varia_suit', 'spider', 'ball', 'spiderball', 'spider_ball', 'morph', '/', '/sourceimages', *'0123abc', *tex_words, *spacers]
#dictionary = ['decal', 'scorch', 'burn', 'mine', '03_', 'cannon', 'canon', 'laser_cannon', 'laser', 'lazer', 'lazor', 'mines', 'mining', 'red', 'drill', 'pirate', 'beam', 'space_pirate', 'spacepirate', 'new', *'012', *'abcdefv', 's', *spacers]
#dictionary = ['hud_messages/', 'game_mechanics/', 'ingame/','tutorials/', 'hud',  'game', 'mechanics', 'game_mechanics', 'upgrade', 'expansion', 'pickup', 'pick', 'up', 'pick-up', 'pickups', 'item', 'items', 'text', 'note', 'memo', 'message', 'acquisition', 'acquire', 'aquire', 'acquired', 'aquired', 'found', 'got', 'string', 'strings', 'work', 'working', 'gameplay', 'tutorial', 'tutorials', 'metroid', 's', '!', '/', *spacers]
#dictionary = ['mapuniverse', 'map', 'universe', 'universal', 'global', 'world', 'cooked/', '/', '_master', '!', *spacers]
#dictionary = ['hint', 'hints', 'redundanthintsystem', 'redundant', 'system', 'metroid', 'mp', 'new', *'012', 'cooked/', '/', '!', *spacers]
#dictionary = ['gbalink', 'gameboy', 'advance', 'fusion', 'connect', 'gba', 'link', 'new', 'menu', 'screen', 'frontend', '/', *spacers]
#dictionary = ['grapple', 'grappling', 'beam', 'grapple_point', 'claw', 'hook', 'point', '_bound', '/cooked/', *spacers]
#dictionary = ['xray', 'x-ray', 'x', 'ray', 'visor', '2', 'room', 'over', 'overworld', 'vision', 'pickup', 'nag', 'second', 'first', '1', 'one', 'puzzle', 'two', '0', 's', *spacers]
#dictionary = ['tallon', 'planet', 'zebes', 'talon', 'from', 'overworld', 'over', 'world', 'chozo', 'ruin', 'ruins', 'elev', 'elevator', 'to', 'go', 'hint', 's', *spacers]
#dictionary = [ 'rhs', 'ruin', 'ruins', 'ruin world', 'ruins world', 'tallon', 'talon', 'overworld', 'over', 'world', 'to', 'elev', 'elevator', 'hint', 's', *spacers]
#dictionary = ['flame', 'jet', 'flamejet', 'flame_jet', 'flamethrower', 'nozzle', 'bound', 's', '/cooked/', *spacers]
#dictionary = ['ice', 'under', 'introunderwater', 'underwater', 'water', 'gravity', 'grav', 'gravitysuit', 'gravity_suit', 'gravity suit', 'use', 'need', 'needed', 'require', 'required', 's', 'hint', *'012', *spacers]
#dictionary = ['00m', 'mines', 'connect', 'mines_connect', 'rock', 'block', 'blocker', 'blocking', 'bomb', 'static', '01', '02', '03', '04', *string.digits, 's', *spacers]
#dictionary = ['gamma', 'beta', 'colormod', 'metroid', 'metriod', 'met', 'col', 'version', 'parts', 'color', 'mod', 'beta', '/sourceimages/', '/', 's', '-', *spacers]
#dictionary = ['character', 'char', '11_', '11 ', 'base', 'ob', 'observ', 'observatory', 'lower arm', 'lowerarm', 'lower_arm', 'lower', 'arm', 'node', 'node1', 'static', 'anim', 'animated', 'animation', 'animating', 's', 'bound', *'012', '/', *spacers]
#dictionary = ['pickup', 'item', 'xray', 'trans', 'transparent', 'ready', 'visor', 'vizor', 'glass', 'gradation', 'gradient', 'gradiant', 'blue', 'noise', 'noisy', *tex_words, *rare_tex_words, *'012', '/', *spacers]
#dictionary = ['chubb', 'chub', 'weed', 'mushroom', 'shroom', 'cap', 'stem', 'trunk', 'small', *character_words, *tex_words, *rare_tex_words, *'012', '/', *spacers]
#dictionary = ['chozo', 'lore', 'glow', 'chozo_lore', 'chozolore', 'chozoloreglow', 'chozo_lore_glow', 'static', 'anim', 'bound', '_bound', '/cooked/', *spacers]
#dictionary = ['petri', 'petrified', 'eye', 'eyeball', '11', '11_', 'static', 'anim', 'bound', '_bound', '/cooked/', *spacers]
#dictionary = ['metroid', 'met', 'beta', 'mand', 'mandible', 'base', 'gamma', 'head', 'ball', 'brain', 'organ', *tex_words, 's', *spacers]
#dictionary = ['3', '03', '0', '3', 'monkeyflamethrower', 'monkey', 'lower', 'flamethrower', 'contrap', 'contraption', 'body', 'eye', *scan_tex_words, *scan_tex_suffixes, 's', *spacers]
#dictionary = ['tryclops', 'triclops', 'tri', 'try', 'clops', 'alpha', 'beta', 'gamma', 'lava', *scan_tex_suffixes, 's', '-', *spacers]
#dictionary = ['ripper_', 'glider_', 'alpha_', 'beta_', 'gamma_', *scan_tex_words, *scan_tex_suffixes, 's', *spacers]
#dictionary = ['mega', 'big', 'heavy', 'gun', 'turret', 'turet', 'turrent', 'mine', 'mines', 'pirate', 'space_pirate', 'sp', 'sentry', 'auto', 'defense', 'defence', 's', *spacers]
#dictionary = ['metroid', 'prime', 'metroid_prime', 'spider', 'exo', 'body', 'mp', 'metroidprime', 'front', 'close', 'closeup', 'stage', *'01', 's', '_4l', '_4r', '_right', '_left', '_r', '_l', *spacers]
#dictionary = ['block', 'blocks', '14_', '14_tower', 'tower_of_light', 'tol', '14_ruins_', 'objects', 'ruins_', 'tower', 'tl', 'light', 'base', 'base01', '/cooked/', 'bound', 'static', 's', *'012', *spacers]
#dictionary = [ 'pillar', 'pil', 'mines', 'parts', 'pieces', 'mines_pillar', '/cooked/', '04', '04_',  'level', 'spider', 'spiderball', 'puzzle', 's', '/', *spacers]
#dictionary = ['big', 'small', 'medium', 'med', 'cargo', 'generic', 'explode', 'c', 'exploding', 'explo', 'explosive', 'bound', 'static', 'pirate', 'spacepirate', 'space_pirate', 'mine', 'mines', 'new',  *'012', 's', '/', *spacers]
#dictionary = ['metal', 'test', 'tube', '11', '11_', 't', 'mine', 'mines', 'new', 'breakable', 'destroyable', 'destructable', 'destructible', *string.digits, 's', *spacers]
#dictionary = ['multi', 'multiplayer', '01', 'sidehopper_station', 'sidehopper', 'station', 'sidehopperstation', 'intro', 'introllevel', 'level', 'world', 's', '/', *spacers]
# dictionary = ['large', 'health', 'node', '1', 'static', 'new', 'bound', 'old', 's', *spacers]
#dictionary = ['death_eye', 'deatheye', 'death', 'eye', 'eyeball', 'dark', 'light', 'new', *'012/', 's', *spacers]
#dictionary = ['ingsnatchingswarm', 'ing', 'snatch', 'snatching', 'swarm', 'boss', 'mega', 'alpha', 'splinter', 'new', *'012/', 's', *spacers]
#dictionary = ['playergun', 'playergun/', 'first', 'person', 'multiplayer', 'multi', 'samusarm', 'samus_arm', 'fsm', 'patterned/', 'player', 'player/', 'gun', 'samus', 'arm', 'player', 'anim', 'ctrl', 'control', 'controller', 'singleplayer', *'012/', 's', *spacers]
#dictionary = ['dead', 'trooper', 'log', 'lore', 'gf', 'federation', 'galactic', *'012', 's', *spacers]
#dictionary = ['dead', 'rotting', 'pirate', 'log', 'scan', 'corpse', 'space pirate', 'spacepirate', 'space_pirate', 'body', 'bodies', *'012ab', '001', '002', '01', '02', 's', *spacers]
#dictionary = ['pirate', 'creatures', 'scan', 'data', 'space pirate', 'spacepirate', 'space_pirate', 'note', 'lore', 'scan', *'012/', 's', *spacers]
#dictionary = ['05_', 'cliff', 'engine', 'room', 'vault', 'bridge', 'cage', 'screw', 'puzzle', 'attack', *'012/', 's', *spacers]
#dictionary = ['05_', '05', 'sand', 'sandland', 'portal', 'puzzle', 'room', 'dark', 'light', 'object', *'0125/', 'scenes/', 's', *spacers]
#dictionary = ['emperor', 'ing', 'final', 'boss', 'stage3', 'stage', *'ei03/', '/cooked/', 's', *spacers]
#dictionary = ['sand', 'sandland', 'sandlands','land', 'alamo', 'demo', '06', '22','04', 'e3', 'e3_', 'world', 'string', *'/!', 's', *spacers]
#dictionary = ['e3_temple', 'e3_temple_string', 'temple', 'hub', 'temple_world','world_hub', 'string', 'demo', '06', '17','04', 'e3', 'e3_', 'world', *'/!', 's', *spacers]
#dictionary = ['m', 'frontend',  'front', 'mp', 'dm', 'end', 'master', 'world','string', 'multi', 'multiplayer', 'mode', 'arena', 'arenas', 'deathmatch', 'coins', 'game', 'level', 'map', 'metroid', 'worlds', *'0125./!', 's', *spacers]
#dictionary = ['fe', 'frontend',  'front', 'end', 'menu', 'master', 'world','string', 'game', 'level', 'map', 'metroid', 'worlds', *'024./!', 's', *spacers]
#dictionary = ['samus', 'cinematic', 'cinema', 'new', 'high_rez', 'high_res', 'hi_res', 'metroid', 'character', 'character_cinematics', 'cage', '/cooked/', 'anim', 'animation', 'cutscene', *'012/', 's', *spacers]
#dictionary = ['portal', 'rift', 'rift portal', 'light portal', 'transdimensional', 'interdimensional', 'forgotten', 'shield', 'gate', 'barrier', 'blocker', 'blocked', 'active', 'enabled', 'on', 'force field', 'forcefield', 'scan', 'hint', 's', *spacers]
#dictionary = ['swamp', 'swampland', 'swamplands', 'dark', '_dark', '03_swamp', 'forgottenbridge', 'forgotten_bridge', '03_swamp_forgottenbridge', '/', 'land', 's', *spacers]
#dictionary = ['temple', 'int', 'interior', 'world', 'dark', 'sky', '_dark', '12_temple', 'finalgate', 'final', 'gate', '/', 'land', 's', *spacers]
#dictionary = ['chozo', 'ghost', 'blue', 'ghostly', 'glow', 'glowy', 'glowing', 'tint', 'blend', 'add', 'additive', 'tinted', 'new', *'civ012', *rare_tex_words, 's', 'sourceimages/', '/', *spacers]
#dictionary = ['medium', 'med', 'ing', 'ball', 'sphere', 'orb', 'anim', 'animation', 'new', *'012', *character_words, 's', '/cooked', '/', *spacers]
#dictionary = [*string.ascii_lowercase, '-', *spacers]
#dictionary = [*scan_tex_words, *spacers]
#dictionary = [*string.digits, *spacers]
#dictionary = [*[('0' + x) for x in string.ascii_lowercase], *digits, '_temple deadtrooper ', '_temple_deadtrooper ',  '_temple deadtrooper_', '_temple_deadtrooper_', '_temple dead trooper ', '_temple_dead trooper ',  '_temple dead trooper_', '_temple_dead trooper_', '_temple dead_trooper ', '_temple_dead_trooper ',  '_temple dead_trooper_', '_temple_dead_trooper_',]

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
    final_goals = {remove_suffix(g, suffix) for g in goals}
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
            print(f"{start_green}Match: 0x{crc32(suffix, match):08x} = {prefix}{words[0] * k}{suffix}{end_color}")

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
                                  f"Match: 0x{crc32(suffix, match):08x} = "
                                  f"{prefix}{''.join([words[i] for i in currents[:end_index]])}{suffix}"
                                  f"{end_color}")
                    break

def dictionary_attack_multi(goals: List[int], prefixes: List[str], suffixes: List[str], depth: int):
    """
    Basically the same as above, but takes in a list of potential prefixes and suffixes instead of a single string. The
    code for this version is uglier due to the extra loops, so I've kept it as a separate function for clarity.
    :param goals: List of ints. If any of these values are matched by a guess, the match will be printed out.
    :param prefixes: List of strings, each of which will be separately prepended to all guessed strings.
    :param suffixes: List of strings, each of which will be separately appended to all guessed strings.
    :param depth: Max number of words to use in a single guess.
    :return: None
    """
    final_goals: Dict[int, List[str]] = dict()
    printed = set()
    for g, suffix in itertools.product(goals, suffixes):
        val = remove_suffix(g, suffix)
        final_goals[val] = [suffix] + (final_goals.get(val) or [])

    for key in final_goals:
        if len(final_goals[key]) > 2:
            print({hex(crc32(val, key))[2:]: val for val in sorted(final_goals[key])})

    print(f'Matching [{", ".join([hex(g) for g in goals])}]')
    print(f'for prefixes {prefixes}')
    print(f'and suffixes {suffixes}')
    print(f'at depth {depth}')
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
            for suffix in suffixes:
                if (match := crc32(suffix, init)) in final_goals:
                    print(f"{start_green}Match: 0x{crc32(suffix, match):08x} = {prefixes[idx]}{words[0] * k}{suffix}{end_color}")

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
                            #if (match := crc32('_'.join([words[z] for z in currents[:(-k + 1) or None]]), prefix_hashes[m])) in final_goals:
                            if (match := guess_stack[-1]) in final_goals:
                                end_index = (-k + 1) or None
                                for curr_suffix in final_goals[match]:
                                    full_match = f"{prefixes[m]}{''.join([words[i] for i in currents[:end_index]])}{curr_suffix}"
                                    if full_match not in printed:
                                        print(f"{start_green}"
                                              f"Match: 0x{crc32(curr_suffix, match):08x} = {full_match}{end_color}")
                                        printed.add(full_match)
                    break

def fetch_unmatched_assets(asset_types: List[str], pak_name: str = None):
    asset_db_path = r'./database/mp_resources.db'
    connection = sqlite3.connect(asset_db_path)
    command  = f"select ap.hash from asset_paths ap "
    command += f"inner join asset_usages us on ap.hash = us.hash "
    command += f"where ap.path_matches = 0 "
    command += f"and us.game like 'MP1/1.00' "
    if pak_name:
        command += f"and us.pak = '{pak_name}.pak' COLLATE NOCASE "
    command += f"and us.type in ('{"', '".join(asset_types)}') "
    command += f"and not ap.path like '$/Scannable%' "
    command += f"and not ap.path like '%lightmap%' "
    command += f"group by ap.hash "
    command += f"order by ap.path "
    resource_results = connection.execute(command).fetchall()
    return [int(row[0], 16) for row in resource_results]

if __name__ == '__main__':
    m2_goals = fetch_unmatched_assets(['TXTR'], 'Metroid2')
    m3_goals = fetch_unmatched_assets(['TXTR'], 'Metroid3')
    m4_goals = fetch_unmatched_assets(['TXTR'], 'Metroid4')
    m5_goals = fetch_unmatched_assets(['TXTR'], 'Metroid5')
    m6_goals = fetch_unmatched_assets(['TXTR'], 'Metroid6')
    m7_goals = fetch_unmatched_assets(['TXTR'], 'Metroid7')
    room_prefixes  = [f'0{char}' for char in string.ascii_lowercase]
    room_prefixes += [f'00{char}' for char in string.ascii_lowercase]
    room_prefixes += [f'{num:02}' for num in range(24)]
    room_prefixes += [f'{num}' for num in range(24)]
    tex_suffixes = [".txtr", "c.txtr", 'i.txtr', 'r.txtr', 'incan.txtr', 'reflected.txtr', 'blend.txtr', 'blendc.txtr']
    tex_suffixes += [f"{num}.txtr".lower() for num in range(6)]
    tex_suffixes += [f"blend{num}.txtr".lower() for num in range(6)]
    tex_suffixes += [f"{num}c.txtr".lower() for num in range(6)]
    tex_suffixes += [f"0{num}c.txtr".lower() for num in range(6)]
    tex_suffixes += [f"blend{num}c.txtr".lower() for num in range(6)]
    tex_suffixes += [f"{num}i.txtr".lower() for num in range(6)]
    effect_goals = fetch_unmatched_assets(['PART'])
    effect_suffixes = [".gpsm.part"]
    effect_suffixes += [f"{char}.gpsm.part" for char in 'abcdefg']
    effect_suffixes += [f"{num}{suf}" for num, suf in itertools.product(range(10), effect_suffixes.copy())]
    slideshow_goals = fetch_unmatched_assets(['TXTR'], 'Slideshow')
    m2_prefixes = [
        "$/Worlds/RuinWorld/common_textures/".lower(),
        "$/Worlds/RuinWorld/common_textures/stone/".lower(),
        "$/Worlds/RuinWorld/common_textures/metal/".lower(),
        "$/Worlds/RuinWorld/common_textures/organic/".lower(),
    ]
    #dictionary_attack_multi(m3_goals, m3_prefixes, ".txtr".lower(), 4)

    # dictionary = [*digits, *spacers]
    # dictionary.extend(pwe_list)
    # dictionary = list(itertools.chain(*[[word, word + '_'] for word in dictionary]))
    # dictionary_attack_multi(effect_goals, [pref for pref in effect_prefixes], effect_suffixes, 1)

    # dictionary = [*flaahgra_words, *char_tex_words, *tex_words,  *spacers]
    # #dictionary.extend(pwe_bad_list)
    # dictionary = list(itertools.chain(*[[word, word + '_'] for word in dictionary]))
    # dictionary_attack_multi([0xB22871B2, 0xFE225271, 0x9E628F99], ['$/2c02wdn/', '$/2c02wdn/flaahgraa_',  '$/2c02wdn/flaahgraa_', ], tex_suffixes, 3)

    dictionary = [*world_tex_words, *ruin_words, *tex_words, *colors, *digits, *spacers]
    dictionary.extend(world_words)
    #dictionary.extend(pwe_bad_list)
    #dictionary = [f'{num:>02}' for num in itertools.chain(range(1, 23), *string.ascii_lowercase)] + dictionary
    dictionary = list(itertools.chain(*[[word, word + '_'] for word in dictionary]))
    #dictionary_attack_multi(m2_goals, [pref + f'0{char}_' for pref, char in itertools.product(m2_prefixes, string.ascii_lowercase)], tex_suffixes, 2)
    dictionary_attack_multi(m2_goals, [pref for pref in m2_prefixes], tex_suffixes, 2)

    # dictionary = [*world_tex_words, *ice_words, *tex_words, *colors, *digits, *spacers]
    # dictionary.extend(world_words)
    # dictionary.extend(pwe_bad_list)
    # dictionary = room_prefixes + dictionary
    # dictionary = list(itertools.chain(*[[word, word + '_'] for word in dictionary]))
    # dictionary_attack_multi(m3_goals, [f'$/Worlds/IceWorld/common_textures/'.lower()], tex_suffixes, 2)
    # #dictionary_attack_multi(m3_goals, [f'$/Worlds/IceWorld/common_textures/'.lower()], tex_suffixes, 2)

    # dictionary = [*world_tex_words, *over_words, *lava_words, *tex_words, *colors, *digits, *spacers]
    # dictionary.extend(world_words)
    # #dictionary.extend(pwe_bad_list)
    # dictionary = room_prefixes + dictionary
    # dictionary = list(itertools.chain(*[[word, word + '_'] for word in dictionary]))
    # dictionary_attack_multi(m4_goals + m6_goals, ["$/Worlds/Overworld/common_textures/".lower()], tex_suffixes, 2)
    # #dictionary_attack_multi(m4_goals + m6_goals, ["$/Worlds/Overworld/06_over_crashed_ship/sourceimages/06".lower()], tex_suffixes, 2)
    # #dictionary_attack_multi(m4_goals + m6_goals, [f'$/Worlds/Overworld/common_textures/00{char}_'.lower() for char in string.ascii_lowercase], tex_suffixes, 2)

    # dictionary = [*world_tex_words, *over_words, *tex_words, *colors, *digits, *spacers]
    # dictionary.extend(world_words)
    # dictionary = room_prefixes + dictionary
    # dictionary = list(itertools.chain(*[[word, word + '_'] for word in dictionary]))
    # dictionary_attack_multi(m4_goals, ["$/Worlds/IntroUnderwater/common_textures/".lower()], tex_suffixes, 2)

    # dictionary = [*world_tex_words, *mine_words, *tex_words, *colors, *digits, *spacers]
    # dictionary.extend(world_words)
    # #dictionary.extend(pwe_bad_list)
    # dictionary = room_prefixes + dictionary
    # dictionary = list(itertools.chain(*[[word, word + '_'] for word in dictionary]))
    # dictionary_attack_multi(m5_goals, ["$/Worlds/Mines/common_textures/".lower()], tex_suffixes, 2)
    #dictionary_attack_multi(m5_goals, [f'$/Worlds/Mines/common_textures/0{char}_'.lower() for char in string.ascii_lowercase], tex_suffixes, 2)

    # dictionary = [*world_tex_words, *crater_words, *tex_words, *colors, *digits, *spacers]
    # dictionary.extend(world_words)
    # #dictionary.extend(pwe_bad_list)
    # dictionary = room_prefixes + dictionary
    # dictionary = list(itertools.chain(*[[word, word + '_'] for word in dictionary]))
    # dictionary_attack_multi(m7_goals, ["$/Worlds/Crater/common_textures/".lower()], tex_suffixes, 2)

    # dictionary = ['babygoth', 'baby', 'sheegoth', 'icicle', 'icecle', 'crystal', 's', *ice_words, *tex_words, *digits, *spacers]
    # # dictionary.extend(world_words)
    # # dictionary.extend(pwe_bad_list)
    # dictionary = list(itertools.chain(*[[word, word + '_', word + '/'] for word in dictionary]))
    # dictionary_attack_multi([0x4C94FB4B], ['$/Characters/ice_sheegoth/sourceimages/'.lower(), '$/Characters/ice_sheegoth/sourceimages/babygoth_'.lower()], tex_suffixes, 4)

    # dictionary = ['thardus', 'rock', 'stone', 'ice', 'snow', 'frost', 'frosty', 'icy', 'snowy', 's', *ice_words, *char_tex_words, *tex_words, *digits, *spacers]
    # # dictionary.extend(world_words)
    # dictionary.extend(pwe_list)
    # dictionary = list(itertools.chain(*[[word, word + '_', word + '/'] for word in dictionary]))
    # dictionary_attack_multi([0x86A95D4E, 0x884BFBD5, 0x2159C8B6], ['$/Characters/thardus/sourceimages/'.lower(),'$/Characters/thardus/sourceimages/c_'.lower(), '$/Characters/thardus/sourceimages/thardus_'.lower()], tex_suffixes, 2)

    # dictionary = ['08', '08_ice_ridley', 'ridley', 'spacebox','space', 'box', 'intro','cargo', 'crate', 'cargocrate', 'ice', 'large', 'big',  's', '/cooked/', *spacers]
    # # dictionary.extend(world_words)
    # #dictionary.extend(pwe_list)
    # dictionary = list(itertools.chain(*[[word, word + '_', word + '/'] for word in dictionary]))
    # dictionary_attack_multi([0x2A1651CD], ['$/AnimatedObjects/IceWorld/'.lower(),'$/AnimatedObjects/IceWorld/IceCargoCrate/'.lower(),'$/AnimatedObjects/Mines/'.lower(), '$/AnimatedObjects/Introlevel/scenes/'.lower(),], ['.cmdl'.lower(), ], 5)

    # dictionary = ['metroid', 'prime', 'metroidprime', 'exo', 'exoskeleton', 'metroid_prime', 'boss', 'stage', 'stage1', 'crystal', 's', *scan_tex_words, *spacers]
    # # dictionary.extend(world_words)
    # dictionary.extend(pwe_list)
    # dictionary = list(itertools.chain(*[[word, word + '_'] for word in dictionary]))
    # dictionary_attack_multi([0x30FB9196, 0x4A15F683], ['$/ScannableObjects/Creatures/sourceimages/'.lower(),'$/ScannableObjects/Creatures/sourceimages/Prime_'.lower(),'$/ScannableObjects/Creatures/sourceimages/Prime_Stage1_'.lower(), ], ['4l.txtr', '4r.txtr'], 3)

    # dictionary = ['a', '0a', '00a', 'd', '0d', '00d', 'over_hall', 'hall', '6', '06', '06_over_crashed_ship', 'delete', 'crashed_ship', 'over', 'overworld', 'area', 'room', 'work', 'working', 'textures', 'texture', 'common_textures', 'sourceimages', 'don', 'beth', 'chuck', 'ms', 'gk', 'marco', 'ryan', 'tod', 's', *spacers]
    # # dictionary.extend(world_words)
    # #dictionary.extend(pwe_list)
    # dictionary = list(itertools.chain(*[[word, word + '_', word + '/'] for word in dictionary]))
    # dictionary_attack_multi([0x3d2b4bdf], ['$/Worlds/Overworld/common_textures/'.lower(), '$/Worlds/Overworld/06_over_crashed_ship/'.lower(), '$/Worlds/Overworld/00d_over_hall/'.lower(), '$/Worlds/Overworld/00a_over_hall/'.lower(),'$/Worlds/Overworld/06_over_crashed_ship_delete/'.lower(), '$/Worlds/Overworld/06_over_crashed_ship/sourceimages/'.lower()], ['vine1c.txtr'.lower(), '06vine1c.txtr'.lower(),], 4)

    # dictionary = ['x', '6', '06', '06_over_crashed_ship', 'delete', 'crashed_ship', 'over', 'over_hall', 'connect', 'overworld', 'area', 'room', 'work', 'working', 'textures', 'texture', 'common_textures', 'sourceimages', 'don', 'beth', 'chuck', 'ms', 'gk', 'marco', 'ryan', 'tod', 's', *spacers]
    # # dictionary.extend(world_words)
    # dictionary.extend(pwe_list)
    # dictionary.extend(pwe_bad_list)
    # dictionary = list(itertools.chain(*[[word, word + '_',] for word in dictionary]))
    # dictionary_attack_multi([0x3d2b4bdf], ['$/Worlds/Overworld/'.lower(),], [ '/sourceimages/vine1c.txtr'.lower(), '/sourceimages/06vine1c.txtr'.lower(),], 2)

    # dictionary = ['19', 'hive', 'totem', 'missile', 'missle', 'launcher', 'rocket', 'missile launcher', 'missile launcher upgrade', 'upgrade', 's', 'pickup', 'scan', *spacers]
    # # dictionary.extend(world_words)
    # #dictionary.extend(pwe_list)
    # #dictionary.extend(pwe_bad_list)
    # dictionary = list(itertools.chain(*[[word, word + ' ', word + '_'] for word in dictionary]))
    # dictionary_attack_multi([0x089ea5aa], ['$/Strings/English/Scan_Data/!Scans_Chozo_Ruins/19_'.lower(),'$/Strings/English/Scan_Data/!Scans_Chozo_Ruins/'.lower(),'$/Strings/English/Scan_Data/!Scans_Game_Mechanics/'.lower(),'$/Strings/English/Scan_Data/!Scans_Chozo_Ruins/19 Hive '.lower(),], [ '.strg'.lower()], 5)

    # #dictionary = ['moving', 'metal', 'ele', 'elev', 'puzzle', 'chozo', 'core', 'cores', 'energy', 'ener', 'elevator', 'bound', 'static', 'base', 'anim', 'lift', 'platform', 'plat', 'static', 's', *spacers]
    # dictionary = [ 'core', 'cores', 'energy', 'ener', 'bomb', 'mb', 'morph', 'ball', 'morphball', 'slot', 'hole', 'ring', 'bound', 'static', 'base', 'anim', 's']
    # # dictionary.extend(world_words)
    # #dictionary.extend(pwe_list)
    # #dictionary.extend(pwe_bad_list)
    # dictionary = list(itertools.chain(*[[word, word + '_',] for word in dictionary]))
    # dictionary_attack_multi([0x2F87FC01], ['$/Worlds/RuinWorld/15_energycore/cooked/'.lower(),'$/Worlds/RuinWorld/15_energycore/cooked/15_'.lower(),], [f'{num}.cmdl'.lower() for num in range(1,999)], 5)

    #dictionary = ['3', '03', '3_monkey', '0', 'monkey', 'monkey_lower', 'flamethrower', 'lower', 'pickup', 'item', 'bomb', 'morphball', 'morph' 'ball', 'stand', 'platform', 'static', 'anim', 'bound', '/', 's', *spacers]
    #dictionary_attack([0xAA95E77E], "$/AnimatedObjects/RuinsWorld/scenes/".lower(), "/sourceimages/ground_circleC.txtr".lower(), 6)

    # dictionary = ['splitter', 'dark', 'main', 'body', 'leg', 'c', 'color', *'01/s', *spacers]
    # dictionary = list(itertools.chain(*[[word, word + '_', word + '/'] for word in dictionary]))
    # dictionary_attack([0x0E1C3D43, 0x53A19C15], '$/Characters/splitter/sourceimages/'.lower(), ".txtr".lower(), 5)

    #dictionary_attack(m2_goals, "$/Worlds/RuinWorld/common_textures/".lower(), ".txtr".lower(), 4)
    #dictionary_attack([0x693D8E22, 0xEEA26B3D, 0x0DB82983, 0x38B6B3D1, 0x7A30AAB8, 0x8C016008], "$/Characters/gargantuan_beetle/sourceimages/".lower(), ".txtr".lower(), 4)
    #dictionary_attack([0x24B75052, 0x750EDEB3, 0x68919D46, 0x05368239, 0xF9563AF9, 0x69B2F842], "$/Characters/elite_space_pirate/sourceimages/omega_pirate/".lower(), ".txtr".lower(), 4)
    #dictionary_attack(m2_goals, "$/Worlds/RuinWorld/common_textures/metal/".lower(), ".txtr".lower(), 4)
    #dictionary_attack(m3_goals, "$/Worlds/IceWorld/common_textures/".lower(), ".txtr".lower(), 4)
    #dictionary_attack(m4_goals, "$/Worlds/Overworld/common_textures/".lower(), ".txtr".lower(), 4)
    #dictionary_attack(m4_goals, "$/Worlds/IntroUnderwater/common_textures/".lower(), ".txtr".lower(), 4)
    #dictionary_attack(m5_goals, "$/Worlds/Mines/common_textures/".lower(), ".txtr".lower(), 4)
    #dictionary_attack(m6_goals, "$/Worlds/Overworld/common_textures/".lower(), ".txtr".lower(), 4)
    # dictionary_attack_multi([0x5628c9ad], ['$/AnimatedObjects/General/pickups/LargeHealth/'.lower(),], '.acs'.lower(), 6)
    #dictionary_attack(m4_goals, "$/Worlds/IntroUnderwater/common_textures/".lower(), ".txtr".lower(), 5)
    #dictionary_attack([0xba2e567c, 0x8d5241eb], "$/Characters/spank_weed/cooked/".lower(), "_bound.cmdl".lower(), 6)
    #dictionary_attack_multi([0xe2d76f28], ["$/AnimatedObjects/RuinsWorld/scenes/".lower(), "$/Characters/".lower(), ], "/B_shudderbase_flaaghra.ani".lower(), 7)
    #dictionary_attack_multi([0x70035854], ["$/AnimatedObjects/RuinsWorld/".lower(), "$/AnimatedObjects/RuinsWorld/scenes/".lower(), "$/Characters/".lower()], "".lower(), 5)

    # dictionary = [*flaahgra_words, *spacers]
    # dictionary = list(itertools.chain(*[[word, word + '_', word + '/'] for word in dictionary]))
    # dictionary_attack_multi([0xc7a7abec], ["$/Experiments/".lower(), "$/".lower(), "$/Characters/".lower(), ], ["/".lower()], 5)

    # dictionary = [*flaahgra_words, '/sourceimages', *spacers, '/']
    # dictionary_attack_multi([0xAD4ED949], ["$/AnimatedObjects/RuinsWorld/".lower(), "$/AnimatedObjects/RuinsWorld/scenes/".lower(), "$/Characters/".lower(), "$/Characters/plant_boss/".lower()], "/eyec.txtr".lower(), 5)
    #dictionary_attack_multi([0x10762b2e], ["$/characters/".lower(), "$/AnimatedObjects/RuinsWorld/scenes/".lower()], "/cooked/b_intoready_flaaghra.ani".lower(), 5)
    #dictionary_attack_multi([0x96324de1], ["$/Effects/particles/sam_weapon/beam/wave/".lower(), "$/Effects/particles/sam_weapon/beam/".lower(), "$/Effects/particles/sam_weapon/".lower(), "$/Characters/samusGun/cooked/effects/".lower()], ".wpsm.wpsc".lower(), 5)
    #dictionary_attack_multi([0xe9b1a835], ["$/Worlds/".lower(), "$/Worlds2/".lower(),], "/01_sidehopperstation/cooked/01_sidehopperstation_lit_lightmap4.txtr".lower(), 6)
    #dictionary_attack([0x22568ca0], "$/Characters/".lower(), "/B_angry4_flaaghra.ani".lower(), 6)
    #dictionary_attack([0x8033012D], "$/Characters/warwasp/sourceimages/".lower(), ".txtr".lower(), 6)
    #dictionary_attack([0x0945B1B7], "$/Characters/common_textures/samusgun/".lower(), ".txtr".lower(), 5)
    #dictionary_attack_multi([0xF7971653, 0xAD4ED949, 0x60468339, 0x8AF881A4, 0x9E628F99], ["$/characters/plant_boss_creaturencxk_rn/sourceimages/".lower()], ".txtr".lower(), 4)
    #dictionary_attack_multi([0x203B5A77], ["$/Worlds/RuinWorld/7_ruinedroof/sourceimages/".lower()], ".txtr".lower(), 5)
    #dictionary_attack([0x0c5c9c3b], "$/Characters/samusGunMotion/cooked/".lower(), ".cmdl".lower(), 5)
    #dictionary_attack_multi([0x5B81ABC1], ["$/Worlds/".lower(),"$/"], "/!Swamp_World/cooked/0q_swamp_hall_dark.mrea".lower(), 6)
    #dictionary_attack([0x0c5c9c3b, 0x9c8058b1, 0x0ef58656], "$/Characters/SamusGun/cooked/models/".lower(), ".cmdl".lower(), 5)
    # dictionary_attack_multi([0x7BDE8CD3, 0x06955FA2, 0xbee1f32f],[
    #                                 "$/editorsupport/editormodels/sourceimages/".lower(),
    #                                 "$/editorsupport/common_textures/".lower(),
    #                                 "$/Textures/defaults/".lower(),
    #                                 "$/Textures/editorsupport/".lower()
    # ], ".txtr".lower(), 5)
    #dictionary_attack([0xC22E8E2E], "$/AnimatedObjects/IceWorld/11_hologram/".lower(), "/cooked/11_trajectorylines_ready.ani".lower(), 6)
    #dictionary_attack([0xC22E8E2E], "$/AnimatedObjects/IceWorld/11_hologram/cooked/".lower(), "/11_trajectorylines_ready.ani".lower(), 6)
    #dictionary_attack([0xC22E8E2E], "$/AnimatedObjects/IceWorld/11_hologram/cooked/".lower(), "/cooked/11_trajectorylines_ready.ani".lower(), 6)
    #dictionary_attack([0x9CA3F99B], "$/".lower(), "_DGRP".lower(), 6)
    #dictionary_attack([0x74D5FE5B, 0xE6722B40, 0xBE530FCE, 0x1E0FB564], "$/Characters/elite_space_pirate/cooked/omega/".lower(), ".dcln".lower(), 6)
    #dictionary_attack_multi([0x63987781, 0x168E7672, 0x7F47633B], ["$/AnimatedObjects/IceWorld/11_trajlines/sourceimages/".lower(), "$/AnimatedObjects/IceWorld/11_hologram/sourceimages/".lower()], ".txtr".lower(), 5)

    #dictionary = ['b_', 'r_', 'shot', 'shot1', 'shot_1', 'ridley', 'ridley_', 'ridly', *'012!.', 'stagger', 'hit', 'impact', 'hurl', 'back', 'stagger_back', 'staggerback', 'acting', 'fix', '-', *spacers]
    #dictionary_attack([0xF6644505], "$/Characters/Ridley/cooked/".lower(), ".ani".lower(), 6)

    #dictionary = ['trilogy', 'rep', 'trilogy_rep', 'us', 'u', 'usa', 'ntsc', 'america', '/mp2_interface_art', '/', *spacers]
    #dictionary_attack([0x920fb453], "$/".lower(), "/hud_message/hudmessage.frme".lower(), 6)

    #dictionary = ['phazon', 'phason', 'morph', 'spider', 'ball', 'glass', 'reflected', 'incan', 'incandes', 'red', 'cloud', '_reflected', 'low', 'poly', 'low_poly', 'new', 'black', 'phazon_spider_ball_low_poly', 'phazon_spider_ball','phason_spider_ball_low_poly', 'phason_spider_ball', 'samus', *'/s', *spacers]
    #dictionary_attack([0x8B105F2E], "$/Characters/samus_ball/spider_ball/phazon_spider_ball/sourceimages/".lower(), ".txtr".lower(), 6)
    #dictionary_attack([0x596C7FFF], "$/Characters/samus_ball/spider_ball/phazon_ball/sourceimages/".lower(), "phason_reflected.txtr".lower(), 5)

    #dictionary_attack_multi([0xE135621D, 0x0D0EFC82, 0x96ABB0ED], ['$/AnimatedObjects/Overworld/12_lavaspew/cooked/'.lower(), '$/AnimatedObjects/Overworld/12_fieryshores/cooked/'.lower(), ], '.cmdl'.lower(), 5)
    #dictionary_attack_multi([0x538D3318, 0xF512C134], ['$/AnimatedObjects/RuinsWorld/scenes/20_objects/cooked/'.lower()], '.acs'.lower(), 5)
    #dictionary_attack_multi([0x44b2a0af], ['$/Ai/StateMachines/'.lower(), '$/Ai/StateMachines/Patterned/'.lower(),], '.afsm'.lower(), 5)
    #dictionary_attack_multi([0x58152E28], ['$/'.lower(), '$/textures/'.lower(),'$/textures/misc/'.lower(),'$/textures/slideshow/'.lower(), '$/slideshow/'.lower(), '$/slideshow_art/'.lower(),'$/slideshow_gallery/'.lower(), '$/GUI_ART/'.lower(), '$/GUI_ART/slideshow/'.lower(),'$/GUI_ART/textures/'.lower(),], '/x_ray_hand.txtr'.lower(), 5)
    #dictionary_attack_multi([0x129EEA99], ['$/'.lower(), '$/textures/'.lower(),'$/textures/misc/'.lower(),'$/textures/slideshow/'.lower(), '$/slideshow/'.lower(), '$/slideshow_art/'.lower(),'$/slideshow_gallery/'.lower(), '$/mp2_interface_art/'.lower(), '$/mp2_interface_art/slideshow/'.lower(),'$/mp2_interface_art/textures/'.lower(),], '/sourceimages/space_pirate.txtr'.lower(), 5)
    #dictionary_attack([0x0FE93088, 0x62DF838C, 0x949A25CD, 0x14FE72B8], '$/Worlds/Overworld/00f_over_hall/cooked/'.lower(), ".cmdl".lower(), 6)
    #dictionary_attack_multi([0xba2e567c, 0x8d5241eb], ['$/Characters/spank_weed/cooked/'.lower(),'$/AnimatedObjects/RuinsWorld/scenes/spank_weed/cooked/'.lower(),'$/Characters/tentacle/cooked/'.lower(),'$/Characters/Water_Tentacle/cooked/'.lower(), '$/Characters/spank_weed/cooked/models/'.lower(), '$/Characters/new_spank_weed/cooked/'.lower(), '$/Characters/spank_weed_alpha/cooked/'.lower(), '$/Characters/alpha_spank_weed/cooked/'.lower(), ], "_bound.cmdl".lower(), 5)
    #dictionary_attack([0xF68AB597], '$/slideshow/ad06c64d_placeholder_34k83fd/'.lower(), '.txtr', 5)
    #dictionary_attack([0x72E3722E], '$/AnimatedObjects/IceWorld/19_thardus_rock/cooked/'.lower(), '.acs', 6)
    #dictionary_attack([0xFE6F5D43, 0x78A82871], '$/Characters/gargantuan_beetle_beta/cooked/'.lower(), '.cmdl'.lower(), 5)
    #dictionary_attack([0xFE6F5D43, 0x78A82871], '$/Characters/gargantuan_beetle_beta/cooked/'.lower(), '.cmdl'.lower(), 5)
    #dictionary_attack([0x07675658], '$/Characters/Samus_ball/spider_ball/sourceimages/'.lower(), '.txtr'.lower(), 5)
    #dictionary_attack([0xaaa8a02b, 0xc265918f, 0xd6a7cbc2], '$/Effects/particles/decals/'.lower(), '.dpsm.dpsc'.lower(), 5)
    #dictionary_attack([0x2b3dab7c], '$/AnimatedObjects/Overworld/00j_over_hall_holo/cooked/'.lower(), '.acs', 5)
    #dictionary_attack_multi([0x9666c937], ['$/AnimatedObjects/Overworld/'.lower(), '$/AnimatedObjects/Introlevel/'.lower(), '$/AnimatedObjects/IntroUnderwater/'.lower(),'$/AnimatedObjects/CrashedShip/'.lower(), ], 'block1/cooked/block1_moving.ani', 5)
    #dictionary_attack([0x0E0B1D04], '$/cutxkck/'.lower(), '.acs', 5)
    #dictionary_attack_multi([0x5C111B00], ["$/Characters/jellyzap/cooked/".lower(), "$Effects/particles/characters/jellyzap/cooked/".lower(),], ".cmdl".lower(), 6)
    #dictionary_attack_multi([0xAB39F694, 0x5AA26425], [*scan_tex_folders, '$/ScannableObjects/Chozo_Ruins/03_monkey_lower/sourceimages/'.lower()], '.txtr', 5)
    #dictionary_attack_multi([0xD0556937, 0xE9890ADC], [val + 'triclops_' for val in scan_tex_folders], '_4L.txtr'.lower(), 4)
    #dictionary_attack_multi([0xE72A74FB], [*scan_tex_folders], '.txtr', 5)
    #dictionary_attack_multi([0xDBF9EDD7], [*scan_tex_folders], "_4r.txtr".lower(), 6)
    #dictionary_attack_multi([0x30FB9196], [*scan_tex_folders, '$/ScannableObjects/Creatures/sourceimages/Prime_Stage1_', '$/ScannableObjects/Creatures/sourceimages/Prime_Stage', '$/ScannableObjects/Creatures/sourceimages/Prime_'], '.txtr', 5)
    #dictionary_attack_multi([0x9248589A], ['$/AnimatedObjects/RuinsWorld/scenes/', '$/AnimatedObjects/RuinsWorld/14_', '$/AnimatedObjects/RuinsWorld/scenes/14_tower', '$/AnimatedObjects/RuinsWorld/scenes/14_ruins_',], '_cracked.cmdl', 7)
    #dictionary_attack([0x798f36af, 0x05C498F4, 0x71C6A9F5], '$/slideshow/b039e1e3_placeholder_p8qov9/', '.txtr', 5)
    #dictionary_attack_multi([0xe88d10e1], ['$/Characters/samusGun/cooked/gun_cinematic/'.lower(), '$/Characters/samusGun/cooked/models/'.lower(), '$/Characters/samusGun/cooked/'.lower(), '$/Characters/samusGunCinematic/cooked/'.lower(), '$/Characters/samusCinematicGun/cooked/'.lower(), '$/Characters/CinematicGun/cooked/'.lower()], '.cmdl'.lower(), 6)
    #dictionary_attack([0xFDB81B76], '$/Characters/oculus/sourceimages/'.lower(), '.txtr'.lower(), 5)
    #dictionary_attack_multi([0x836C33B3], ['$/Characters/Samus/cooked/'.lower(),'$/Characters/Samus_ball/'.lower(),'$/Characters/Samus_low_res/cooked/'.lower(),'$/Characters/Samusballtransition/cooked/'.lower(),'$/Characters/Samus_ball_transition/cooked/'.lower(), ], '.acs'.lower(), 6)
    #dictionary_attack_multi([0x349AD971, 0xD2149656], ['$/Characters/Samus/varia_suit/'.lower(),'$/Characters/Samus/gravity_suit/'.lower()], '.txtr'.lower(), 6)
    #dictionary_attack_multi([0xcd758404], ['$/Strings/English/Worlds/Overworld/'.lower(),'$/Strings/English/Worlds/LavaWorld/'.lower(),'$/Strings/English/Worlds/'.lower(),'$/Strings/English/Worlds/CrashedShip/'.lower(),'$/Strings/English/Worlds/RuinsWorld/'.lower(),'$/Strings/English/Worlds/General/'.lower(),], '.strg'.lower(), 5)
    #dictionary_attack_multi([0x0d1f9c75], ['$/Strings/English/'.lower(), '$/Strings/English/Pickup/'.lower(), '$/Strings/English/Pickups/'.lower(), '$/Strings/English/HUD_Messages/'.lower(), '$/Strings/English/HUD_Messages/Pickup/'.lower(), '$/Strings/English/HUD_Messages/Pickups/'.lower(), '$/Strings/English/HUD_Messages/Tutorials/'.lower(), '$/Strings/English/InGame/'.lower(), ], 'ice beam.strg'.lower(), 3)
    #dictionary_attack_multi([0x4231a4f5], ['$/'.lower(), '$/Worlds/'.lower(), '$/Worlds/Universal/'.lower(), ], '.mapu'.lower(), 7)
    #dictionary_attack([0x2fd33fbb], '$/Strings/English/RHS/'.lower(), '.hint'.lower(), 6)
    #dictionary_attack([0xF97A7953], '$/AnimatedObjects/RuinsWorld/scenes/snake_weed/sourceimages/'.lower(), '.txtr'.lower(), 6)
    #dictionary_attack_multi([0x275d4b6f, 0xa1c939c1], ['$/Strings/English/HUD_Messages/Tutorials/'.lower(), '$/Strings/English/HUD_Messages/Tutorials/14_tower '.lower(), '$/Strings/English/HUD_Messages/Tutorials/14_tower_a '.lower(), '$/Strings/English/HUD_Messages/Tutorials/14_ice_tower_a '.lower(), '$/Strings/English/HUD_Messages/Tutorials/06_freight '.lower(), '$/Strings/English/HUD_Messages/Tutorials/06_under_freight '.lower(), ], '.strg'.lower(), 6)
    #dictionary_attack_multi([0x275d4b6f, 0xa1c939c1], ['$/Strings/English/HUD_Messages/Tutorials/'.lower(), '$/Strings/English/HUD_Messages/Tutorials/14_tower '.lower(), '$/Strings/English/HUD_Messages/Tutorials/14_tower_a '.lower(), '$/Strings/English/HUD_Messages/Tutorials/14_ice_tower_a '.lower(), '$/Strings/English/HUD_Messages/Tutorials/06_freight '.lower(), '$/Strings/English/HUD_Messages/Tutorials/06_under_freight '.lower(), ], '.strg'.lower(), 6)
    #dictionary_attack_multi([0x33181a6b, 0x5867fcf1], ['$/GUI_ART/'.lower(), '$/GUI_ART/gba'.lower(), '$/GUI_ART/gba'.lower()], '.frme'.lower(), 7)
    #dictionary_attack([0x09837E11], '$/AnimatedObjects/General/'.lower(), '.cmdl', 7)
    #dictionary_attack([0x127de5fb], '$/AnimatedObjects/IceWorld/11_Lower_Arm/cooked/'.lower(), '.acs', 6)
    #dictionary_attack_multi([0xB1B1CD47, 0xDF498E93], ['$/AnimatedObjects/RuinsWorld/scenes/chubb_weed/sourceimages/'.lower(), '$/Worlds/Overworld/common_textures/'.lower(), ], '.txtr'.lower(), 5)
    #dictionary_attack_multi([0xeead5f10], ['$/AnimatedObjects/RuinsWorld/scenes/11_wateryhall/cooked/'.lower(), '$/AnimatedObjects/RuinsWorld/scenes/'.lower(), ], '.cmdl'.lower(), 6)
    #dictionary_attack([0x3D9E7206, 0xEF411B08, 0xCC809D62], '$/Characters/metroid_beta/sourceimages/'.lower(), '.txtr'.lower(), 6)
    #dictionary_attack([0x0E8722EF, 0x10EBF355, 0x1D79FF7C, 0x1E4D6E5F, 0x2AE19225, 0x34294166, 0x3EAE1745, 0x434F83E4, 0x50B15E77, 0x6ABB3F07, 0x7052276D, 0x8283C80D, 0x88135041, 0x9BED8DD2, 0xA1E7ECA2, 0xB83A65EB, 0xBFB55DFA, 0xC5DBF14A, 0xD6252CD9, 0xD8DEC1F2, 0xDBB720F0, 0xE1BD4180, 0xF5F2C4E0], "$/Worlds/Mines/07_mines_electric/cooked/".lower(), "_lightmap0.txtr", 6)
    #dictionary_attack([0x01E12262, 0x05E4806C, 0x14EFE3EB, 0x18E1B0D4, 0x2D0C0847, 0x2F398754, 0x3802C9CE, 0x3F432C9F, 0x4027D056, 0x42125F45, 0x5D22E0EE, 0x7FF416E7, 0x8540DFDF, 0x877550CC, 0x944BBC58, 0x9597B997, 0x9B6C54BC, 0xA07A0104, 0xA5A3A6C5, 0xC2B600F6, 0xC4862DEB, 0xCD51D915, 0xD9B04E56, 0xDE6F3581, 0xF9606449], "$/Worlds/Mines/00m_mines_connect/cooked/rockblock".lower(), "_lightmap0.txtr", 6)
    #dictionary_attack_multi([0xab8473a5], ["".lower(), '$/',], "/Strings/English/Scan_Data/!Scans_Intro_Level/00g entrance to 00g begin.strg".lower(), 6)

    #dictionary = ['metroid', 'metriod', 'new', 'alpha', 'beta', 'gamma', 'split', 'splitter', 'fission', 'rainbow', 'ed', 'colormod', 'beam', 'recolor', 'met', 'col', 'version', 'parts', 'color', 'mod', 'modded', 'modding', 'modulate', 'modulated', 'modulating', 'sourceimages/', '/', 's', '-', *spacers]
    #dictionary_attack_multi([0xaa198954], ["$/Characters/metroid/sourceimages/", "$/Characters/", "$/Characters/metroid/", "$/Characters/metroid_beta/sourceimages/", "$/Characters/metroidgamma/sourceimages/", "$/Characters/metroid_gamma/sourceimages/", "$/Characters/metroid gamma/sourceimages/", "$/Characters/gammametroid/sourceimages/", "$/Characters/gamma_metroid/sourceimages/", "$/Characters/gamma metroid/sourceimages/", ], "plasma_base.txtr".lower(), 5)

    #dictionary = ['metroid', 'gamma', 'beta', 'alpha', 'fission', 'metriod', 'new', 'ball', 'lobe', 'nucleus', 'sphere', 'orb', 'organ', 'membrane', 'brane', 'cell', 'inner', 'core', 'plasma', 'head', 'base', 'brain', 'red', 'ed', 'met', 'col', '.old', 'color', *'abcs012-', *spacers]
    #dictionary_attack_multi([0x7c934ec5], ["$/Characters/metroid/sourceimages/".lower(), "$/Characters/metroid/sourceimages/gk_working/".lower(),], ".txtr".lower(), 5)

    #dictionary = ['light', 'floor', 'metal', 'metel', 'plate', 'color', *'abcs012-', *spacers]
    #dictionary_attack([0x0CA18A49, 0x536583B2], '$/Worlds/IceWorld/common_textures/'.lower(), '.txtr'.lower(), 5)

    #dictionary = ['0u', 'u', 'connect', '0u_connect', '0u_connect_tunnel', 'tube', 'cylinder', 'conn', 'hall', 'tunnel', 'refl', 'reflected', 'reflection', 'reflect', 'map', 'env', 'enviro', 'environment', 'room', 'metal', 'tex', *'abcs012-', *spacers]
    #dictionary_attack_multi([0xBC7E5BA0], ['$/Worlds/RuinWorld/common_textures/'.lower(), '$/Worlds/RuinWorld/0u_connect_tunnel/sourceimages/'.lower(), '$/Worlds/RuinWorld/0u_connect_tunnel/cooked/'.lower(), ], '.txtr'.lower(), 5)

    # dictionary = ['bark', 'save', 'tree', 'main', 'hall', 'gray', 'grey', 'trunk', 'wood', 'ruin', 'ruins', 'zebes', 'dry', 'dried', 'driftwood', 'chozo', 'red', 'dead', 'dying', 'rotten', 'skin', *'abcsy012-', *spacers]
    # dictionary_attack([0x8B802D22], '$/Worlds/RuinWorld/common_textures/organic/'.lower(), '.txtr'.lower(), 5)

    #dictionary = ['gf', 'g', 'f', 'galactic', 'federation', 'fed', 'trooper', 'marine', 'squad', 'team', 'group', 'multi', 'render', *'s012', '-', *spacers]
    #dictionary = ['samus', 'new', 'varia', 'suit', 'sam', 'render', *'s01234', '-', *spacers]
    #dictionary = ['space', 'pirate', 'sp', 'space_pirate', 'elite', 'flying', 'fly', 'jetpack', 'aero', 'trooper', 'commando', 'dark', 'light', 'render', 'art', 'sketch', 'rough', 'concept', 'rect', '_rect_', 'xl','_rect_xl', *'sxlm012345', '-', *spacers]
    #dictionary = ['ing', 'warrior', 'render', 'art', 'sketch', 'rough', 'concept', 'rect', '_rect_', 'xl', *'sxlm012345', '-', *spacers]
    #dictionary = ['dark', 'cliff', 'cliffside', 'digital', 'land', 'world', 'render', 'art', 'sketch', 'rough', 'concept', *'s012345', '-', *spacers]
    #dictionary = ['emperor', 'emp', 'boss', 'final', 'ing', 'stage', 'render', 'art', 'sketch', 'rough', 'concept', 'rect', '_rect_', 'xl', *'sxlm012345', '-', *spacers]
    #dictionary = ['medium', 'med', 'ing', 'tentacle', 'sketch', 'android', 'render', 'art', *'s012', '-', *spacers]
    #dictionary = ['luminoth', 'moth', 'lord', 'u-mos', 'umos', 'light', 'render', 'art','concept', 'rect', '_rect_', 'xl', *'sxlm012345', '-', *spacers]
    # dictionary = ['luminoth', 'lum', 'moth', 'alphabet', 'cipher', 'code', 'decode', 'decoder', 'karl', 'glyph', 'lore', 'message', 'text', 'secret', 'translator', 'translation', 'key','alphabet', 'holo', 'hologram', 'symbol', *'s01', '-', *spacers]
    # dictionary_attack([0x320E5A2D], "$/rh37bcy/", ".txtr".lower(), 5)

    #dictionary = ['android', 'jones', 'echoes', 'npc', 'aether', 'splinter', 'mecha', 'darkling', 'sm', 'bug', 'beetle', 'insect', 'creature', 'page', 'light', 'dark', 'sketch', 'skech','sketches', 'skeches', 'rough', 'doodle', 'render', 'art', 'rect', '_rect_', 'xl', *'sxlm012345-', *spacers]
    #dictionary_attack([0x95F8EB88 , 0x3DCFCCDF, 0x8CC54998, 0x47999A3D, 0x48855840, 0xC10DE893, 0xC9846E5D, 0xD778EB0C], "$/rh37bcy/", ".txtr".lower(), 5)

    #dictionary_attack_multi([0x706bd2cd], ['$/AnimatedObjects/RuinsWorld/scenes/11_wateryhall/cooked/', '$/AnimatedObjects/General/'.lower(),'$/AnimatedObjects/Overworld/'.lower(),'$/AnimatedObjects/RuinsWorld/'.lower(),], '.cmdl', 7)
    #dictionary_attack([0xe2fea6fd], '$/Strings/English/RHS/'.lower(), '.strg'.lower(), 6)
    #dictionary_attack([0x57D88247], '$/AnimatedObjects/MinesWorld/pillar'.lower(), '3.dcln'.lower(), 6)
    #dictionary_attack([0xF871A8B9, 0x881458FD, 0x881458FD], '$/AnimatedObjects/MinesWorld/crates/cooked/'.lower(), '.cmdl'.lower(), 6)
    #dictionary_attack([0xB8D72430], '$/Worlds/Mines/11_mines_/cooked/'.lower(), '.cmdl'.lower(), 6)
    #dictionary_attack( [0x757617A6], '$/Characters/chozo_ghost/sourceimages/'.lower(), '_chest.txtr'.lower(), 5)
    #dictionary_attack( [0x1b51446c], '$/Ai/StateMachines2/'.lower(), '.fsm2'.lower(), 7)
    #dictionary_attack( [0xc9bbb5e0], '$/Characters/Medium_ing/cooked/'.lower(), '/B_deactivate_intoGround_medIng.ani'.lower(), 6)
    #dictionary = ['animated', 'object', 'animatedobjects', 'worlds2', 'luminoth', 'moth', 'objects', 'metroid', 'general', 'global', 'device', 'machine', 'prop', 'game', 'gameplay', 'new', 'mechanic', 'game_mechanic', *'2s/', *spacers]
    #dictionary_attack_multi( [0xf8d916f2], ['$/'.lower(),'$/AnimatedObjects'.lower(), '$/AnimatedObjects/'.lower(), ], '/sandlands_crate/cooked/flinch_sandlandscrate.ani'.lower(), 6)
    #dictionary = ['leftarm', '_bound', 'new', 'high', 'low', 'lo', 'hi', 'res', 'rez', 'actions', 'action', 'pirate', 'spacepirate', 'space_pirate', 'player', 'multi', 'multiplayer', 'samus', 'melee', 'gun', '/cooked', 'cooked', 'right', 'left', 'work', 'working', 'hand', 'arm', 'bound', *'012s/-', *spacers]
    #dictionary_attack_multi( [0xb40a2c98], ['$/Characters/'.lower(),'$/Characters/samusGun/'.lower(),'$/Characters/pirateGun/'.lower(),  ], '/cooked/poweractions/powerbaseposition.ani'.lower(), 6)

    #dictionary = ['samus', 'varia', 'suit', 'bound', '_bound', *'012s', 'new', 'high', 'low', 'lo', 'hi', 'res', 'rez', *spacers]
    #dictionary_attack_multi( [0xcdf1c541], ['$/Characters/Samus/samus_high_res/cooked/'.lower(), ], '.cmdl'.lower(), 6)


    # dictionary = ['01', 'temple', 'hive', *'012345s', *spacers]
    # dictionary_attack_multi( [0x4c93f89a], ['$/ScannableObjects/Light Temple/'.lower(), ], '/01_Hive3 Dead Grenchler 1.scan'.lower(), 7)


    #dictionary = ['luminoth', 'temple', 'dead luminoth', 'lum', 'warrior', 'rotting', 'decaying', 'decayed', 'mummified', 'mummy', 'fallen', 'keybearer', 'moth', 'husk', 'corpse', 'body', 'dead', 'scan', *'012345sfo', *spacers]
    #dictionary_attack_multi( [0x3B2048DE], ['$/Strings/metroid2/scan_data/!Scans_Light_Temple/'.lower(), '$/Strings/metroid2/scan_data/!Scans_Light_Temple/OF_Temple '.lower(),  '$/Strings/metroid2/scan_data/!Scans_Light_Temple/0F_Temple '.lower(), ], '.strg'.lower(), 6)

    #dictionary = ['grenchler', 'dark', 'beam', 'darkbeam', 'dark_beam', 'purple', 'bit', 'flake', 'ice', 'freeze', 'frozen', 'entangle', 'bound', '_bound', 'entangler', 'entangled', *'ed', 'blob', *'s', *spacers]
    #dictionary_attack_multi( [0x750a60c5], ['$/Characters/grenchler/cooked/grenchler_'.lower(),], '_bound.cmdl'.lower(), 5)

    #dictionary = ['dark', 'ing', 'sand', 'sandland', 'sandlands', 'world', 'generic', 'global', 'crate', 'blade', 'pod', 'bean', 'pea', 'bladepod', 'scan', *'s', *spacers]
    #dictionary_attack_multi( [0xCEEC81BD], ['$/Strings/metroid2/scan_data/!Scans_Game_Mechanics/'.lower(),], '.strg'.lower(), 6)

    #dictionary = ['dialog', 'dialogue', 'sub', 'subtitle', 'title', 'worlds2', 'english', 'character', 'cooked', 'message', 'string', 'metroid2', 'text', 'ingame', 'cutscene', 'scene', *'/s', *spacers]
    #dictionary_attack_multi( [0xadae02bd], ["$/".lower(), "$/Strings/metroid2/".lower(), "$/Strings/".lower(), "$/Strings/metroid2/ingame/".lower(),], "/Sand Temple Meeting 1.strg".lower(), 6)

    #dictionary = ['dark', 'darksuit', 'varia', 'suit', 'token', 'icon', 'pickup', 'bound', 'low', 'new',  *'012/s', *spacers]
    #dictionary_attack_multi( [0xba953ccc], ['$/AnimatedObjects/General/pickups/variasuit/cooked/'.lower(),'$/AnimatedObjects/General/pickups/darksuit/cooked/'.lower(),'$/Worlds2/Animated_Objects/General/pickups/cooked/'.lower(),'$/Worlds2/Animated_Objects/General/pickups/variasuit/cooked/'.lower(),'$/Worlds2/Animated_Objects/General/pickups/cooked/variasuit/'.lower(),], '.cmdl'.lower(), 6)


    # dictionary = ['blue', 'power', 'beam', 'luminoth', 'door', 'new', 'normal', 'standard', 'default', 'all', 'any', 'scan', 'metroid', 'generic', *'012s', *spacers]
    # dictionary_attack_multi( [0x18663f39], ['$/ScannableObjects/Game Mechanics2/'.lower(), ], '.scan'.lower(), 6)

    #dictionary = ['world', 'common_textures', 'intro', 'level', 'common', 'texture', 'generic', 'old', 'global', 'default', *'012s/', *spacers]
    #dictionary_attack_multi( [0x2443EC5F], ['$/Worlds/'.lower(),'$/Worlds2/'.lower(), '$/Textures/'.lower(),'$/Textures/defaults/'.lower(), ], '/Truss3C.txtr'.lower(), 6)

    #dictionary = ['bacteria', 'bacterial', 'bacterium', 'swarm', 'single', 'particle', 'ing', 'storm', 'scan', 'logbook', 'model', *character_words, 'new', *'012s', *spacers]
    #dictionary_attack_multi( [0x6580e288], ['$/ScannableObjects/Creatures2/'.lower(), '$/ScannableObjects/Game Mechanics2/'.lower(), ], '.scan'.lower(), 6)

    #dictionary = ['body', 'four', 'new', '_bound', 'base', 'core', 'blob', 'bulb', 'tail', 'ring', 'spot', 'puddle', 'wisp', 'smoke', 'cloud', 'fog', 'eye', 'eyeball', 'main', 'center', 'central', 'nucleus', 'brain', 'organ', 'ball', 'sphere', 'orb', 'tent', 'tentacle', 'arm', 'melee', 'attack', 'medium', 'med', 'ing', *'s/', 'cooked', *spacers]
    #dictionary_attack_multi( [0x78CB664A], ['$/Characters/Medium_Ing/cooked/'.lower(), ], '/B_roar_medIng.ani'.lower(), 5)
    #dictionary_attack_multi( [0xf4adf67f], ['$/spabpyz/'.lower(), '$/Characters/Medium_Ing/cooked/'], '.cmdl'.lower(), 5)

    # dictionary = ['m', 'frontend', 'front', 'mp', 'dm', 'pvp', 'end', 'master', 'vs', 'versus', 'pirate', 'pirates', 'marine', 'trooper', 'world', 'worlds', 'land', 'string', 'multi', 'multiplayer', 'mode', 'match', 'matches', 'arena', 'arenas', 'deathmatch', 'coins', 'game', 'level', 'map', 'metroid', 'universe', 'rep', *'01235./!', 's', *spacers]
    # dictionary = list(itertools.chain(*[[word, word + '_', word + '/'] for word in dictionary]))
    # dictionary_attack_multi( [0xae171602], ['$/worlds2/'.lower(),'$/worlds/'.lower(),'$/worlds'.lower(),'$/'.lower(),], ['/07_Multi_Spires/cooked/07_Multi_Spires.mwld'.lower()], 3)

    #dictionary = ['turret', 'turret_ball', 'ball', 'anim', '_anim', 'mp', 'dm', 'pvp', 'end', 'master', 'vs', 'versus', 'world', 'land', 'string', 'multi', 'multiplayer', 'mode', 'match', 'matches', 'arena', 'arenas', 'deathmatch', 'coins', 'game', 'level', 'map', 'metroid', 'universe', 'rep', *'01235./!', 's', *spacers]
    #dictionary_attack_multi( [0xae171602], ['$/worlds2/Animated_Objects/'.lower(),'$/worlds2/Animated_Objects/General/'.lower(),'$/worlds2/Animated_Objects/Sandlands/'.lower(),], '/cooked/turret_90_down_additive.ani'.lower(), 5)

    # dictionary = ['dark', 'ing', 'forgotten', 'memory', 'war', 'chest', 'anim', 'bound', 'logbook', *'012/', 's', *spacers]
    # dictionary_attack_multi( [0x1a0e73b4], ['$/worlds2/Animated_Objects/General/'.lower(),], '/cooked/ready_darkchest.ani'.lower(), 6)

    #dictionary_attack_multi( [0xCEE3AF0D], ['$/worlds2/'.lower(),'$/worlds/'.lower(),'$/worlds'.lower(),'$/'.lower(),], '/cooked/FrontEnd04.mrea'.lower(), 6)
    #dictionary_attack_multi( [0xEB84BB39, 0x20D8689C], ['$/Strings/metroid2/scan_data/!Scans_Sandlands_Dark/09_Sand_Dark'.lower(), '$/Strings/metroid2/scan_data/!Scans_Sandlands_Dark/09_Sand'.lower(), '$/Strings/metroid2/scan_data/!Scans_Sandland_Dark/09_Sand_Dark'.lower(),], '.strg'.lower(), 6)
    #dictionary_attack_multi( [0x8828f1d1], ['$/ScannableObjects/!Scans_'.lower(),], '/Flying Pirate.scan'.lower(), 6)
    #dictionary_attack_multi( [0x7b622f21], ['$/AnimatedObjects/'.lower(),'$/Objects/'.lower(),'$/Worlds2/Sandlands/objects/'.lower(),'$/AnimatedObjects/Sand/'.lower(),'$/AnimatedObjects/SandWorld/'.lower(),'$/AnimatedObjects/Sandland/'.lower(),'$/AnimatedObjects/Sandlands/'.lower(),], '/cooked/05_locatormove.ani'.lower(), 6)
    #dictionary_attack_multi( [0x2DDD0647], ['$/Strings/metroid2/scan_data/!Scans_Cliffsides_Dark/06_Cliff_Dark '.lower()], '.strg'.lower(), 6)
    #dictionary_attack_multi( [0x118a0532], ['$/Ai/StateMachines2/'.lower(), '$/Ai/StateMachines/'.lower(), '$/Ai/StateMachines/Player/'.lower(), ], 'gun.afsm'.lower(), 6)