import os
from typing import Set
from extrapolating.update_if_matched import update_if_matched, MatchType


def guess_particles(res_dict, deep_search: bool = False):
    """
    Attempts to match several types of particle effect files by testing if known particle filenames were reused in other
    particle effect folders. Optionally, the deep_search parameter will attempt fuzzy matching by adding/removing digits
    and other common suffixes (this is disabled by default, as it can be very slow and generates many false positives).

    Due to a high rate of false positives, this function does not automatically add matches to the DB, and treats them
    only as potentially correct.

    :param res_dict: A dict of integer hashes to string filenames. Non-matching filenames should be suffixed with "!!".
    :param deep_search: A boolean determining whether to use computationally costlier matching techniques.
    :return: Number of newly-added filename matches, as an int.
    """
    print("Checking particles...")
    matched = 0

    part_folders: Set[str] = set()
    part_folders.update([
        '$/Effects/particles/cinematics/SpaceBootsPickUp',
        '$/Effects/particles/enemy_weapons/',
        '$/Effects/particles/enemy_weapons/pirates',
        '$/Effects/particles/FluidSplashes',
        '$/Effects/particles/FluidSplashes/Splashes',
        '$/Effects/particles/pyro',
        '$/Effects/particles/ruins',
        '$/Effects/particles/ruins/Group01/A',
        '$/Effects/particles/ruins/Group02/A',
        '$/Effects/particles/ruins/Group02/B',
        '$/Effects/particles/mines',
        '$/Effects/particles/overworld',
        '$/Effects/particles/lava',
        '$/Effects/particles/crater',
        '$/Effects/particles/introunderwater',
        '$/Effects/particles/intro_underwater',
        '$/Effects/particles/introunder',
        '$/Effects/particles/intro_under',
        '$/Effects/particles/characters/Bloodflower',
        '$/Effects/particles/characters/Blood_Flower',
        '$/Effects/particles/characters/Burrower',
        '$/Effects/particles/characters/Burrowers',
        '$/Effects/particles/enemy_weapons/Burrower',
        '$/Effects/particles/enemy_weapons/Burrowers',
        '$/Effects/particles/enemy_weapons/Sheegoth',
        '$/Effects/particles/enemy_weapons/Sheegoths',
        '$/Effects/particles/characters/garganBeetleBeta',
        '$/Effects/particles/characters/garganBeetle_Beta',
        '$/Effects/particles/characters/FireFlea',
        '$/Effects/particles/characters/FireFlee',
        '$/Effects/particles/characters/Fire_Flea',
        '$/Effects/particles/characters/Fire_Flee',
        '$/Effects/particles/characters/Flickerbat',
        '$/Effects/particles/characters/Flicker_bat',
        '$/Effects/particles/characters/Flickerbat_Alpha',
        '$/Effects/particles/characters/Flicker_bat_alpha',
        '$/Effects/particles/characters/Geemer',
        '$/Effects/particles/characters/Lumigek',
        '$/Effects/particles/bosses/MetroidPrime',
        '$/Effects/particles/bosses/Metroid_Prime',
        '$/Effects/particles/characters/PuddleToad',
        '$/Effects/particles/characters/Puddle_Toad',
        '$/Effects/particles/characters/PuddleToadGamma',
        '$/Effects/particles/characters/Puddle_Toad_Gamma',
        '$/Effects/particles/characters/Puffer',
        '$/Effects/particles/characters/Ripper',
        '$/Effects/particles/characters/Scarab',
        '$/Effects/particles/characters/Scarabs',
        '$/Effects/particles/characters/Seedling',
        '$/Effects/particles/characters/Seedlings',
        '$/Effects/particles/enemy_weapons/Seedling',
        '$/Effects/particles/enemy_weapons/Seedlings',
        '$/Effects/particles/enemy_weapons/Sova',
        '$/Effects/particles/enemy_weapons/Sovas',
        '$/Effects/particles/characters/Sova',
        '$/Effects/particles/characters/Sovas',
        '$/Effects/particles/bosses/Thardus',
        '$/Effects/particles/bosses/ThardusBoss',
        '$/Effects/particles/bosses/Thardus_Boss',
        '$/Effects/particles/bosses/Thardus/elem',
        '$/Effects/particles/bosses/Thardas',
        '$/Effects/particles/bosses/ThardasBoss',
        '$/Effects/particles/bosses/Thardas_Boss',
        '$/Effects/particles/bosses/IceBoss',
        '$/Effects/particles/bosses/IceBoss/elem',
        '$/Effects/particles/bosses/Ice_Boss',
        '$/Effects/particles/bosses/RockBoss',
        '$/Effects/particles/bosses/Rock_Boss',
        '$/Effects/particles/characters/Tryclops',
        '$/Effects/particles/characters/Triclops',
        '$/Effects/particles/characters/WarWasp',
        '$/Effects/particles/characters/WarWasps',
        '$/Effects/particles/characters/War_Wasp',
        '$/Effects/particles/characters/War_Wasps',
        '$/Effects/particles/characters/Wasp',
        '$/Effects/particles/characters/Wasps',
        '$/Effects/particles/characters/Zoomer',
        '$/Effects/particles/characters2/Grenchler',
        '$/Effects/particles/characters2/Ing',
        '$/Effects/particles/characters2/Ings',
        '$/Effects/particles/characters2/MinorIng',
        '$/Effects/particles/characters2/MediumIng',
        '$/Effects/particles/characters2/BabyMetroid',
        '$/Effects/particles/characters2/Blogg',
        '$/Effects/particles/characters2/Brizgee',
        '$/Effects/particles/characters2/Crystallite',
        '$/Effects/particles/characters2/Crystalite',
        '$/Effects/particles/characters2/DarkSamus',
        '$/Effects/particles/characters2/Dark_Samus',
        '$/Effects/particles/characters2/DarkTrooper',
        '$/Effects/particles/characters2/DarkTroopers',
        '$/Effects/particles/characters2/Dark_Trooper',
        '$/Effects/particles/characters2/Dark_Troopers',
        '$/Effects/particles/characters2/DeathEye',
        '$/Effects/particles/characters2/Death_Eye',
        '$/Effects/particles/characters2/Kralee',
        '$/Effects/particles/characters2/Krokus',
        '$/Effects/particles/characters2/Krocuss',
        '$/Effects/particles/characters2/Luminoth',
        '$/Effects/particles/characters2/Lumite',
        '$/Effects/particles/characters2/Metaree',
        '$/Effects/particles/characters2/Octopede',
        '$/Effects/particles/characters2/Octapede',
        '$/Effects/particles/characters2/Octapede',
        '$/Effects/particles/characters2/Pillbug',
        '$/Effects/particles/characters2/Pill_bug',
        '$/Effects/particles/characters2/PlantScarabSwarm',
        '$/Effects/particles/characters2/Plant_Scarab_Swarm',
        '$/Effects/particles/characters2/PuddleSpore',
        '$/Effects/particles/characters2/Puddle_Spore',
        '$/Effects/particles/characters2/Puffer',
        '$/Effects/particles/characters2/Rezbit',
        '$/Effects/particles/characters2/Sandworm',
        '$/Effects/particles/characters2/Shredder',
        '$/Effects/particles/characters2/Skiff',
        '$/Effects/particles/characters2/Splinter',
        '$/Effects/particles/characters2/Splinters',
        '$/Effects/particles/characters2/Splitter',
        '$/Effects/particles/characters2/Sporb',
        '$/Effects/particles/characters2/StoneToad',
        '$/Effects/particles/characters2/Stone_Toad',
        '$/Effects/particles/characters2/SwimmerSwarm',
        '$/Effects/particles/characters2/Swimmer_Swarm',
        '$/Effects/particles/characters2/UnseenShrieker',
        '$/Effects/particles/characters2/Unseen_Shrieker',
        '$/Effects/particles/characters2/UnseenShriek',
        '$/Effects/particles/characters2/Unseen_Shriek',
        '$/Effects/particles/characters2/WallWalker',
        '$/Effects/particles/characters2/Wall_Walker',
        '$/Effects/particles/characters2/WarWasp',
        '$/Effects/particles/characters2/War_Wasp',
        '$/Effects/particles/characters2/WispTentacle',
        '$/Effects/particles/characters2/Wisp_Tentacle',
        '$/Effects/particles/characters2/MysteryFlyer',
        '$/Effects/particles/characters2/Mystery_Flyer',
        '$/Effects/particles/sam_weapon/beam/power',
        '$/Effects/particles/sam_weapon/missile',
        '$/Effects/particles/sam_weapon/missile/explosion',
        '$/Effects/particles/sam_weapon/missile/elem',
        '$/Effects/particles/sam_weapon/missile/elements',
        '$/Effects/particles/sam_weapon/missile/elements/missilea',
        '$/Effects/particles/sam_weapon/missile/elements/missileb',
        '$/Effects/particles/sam_weapon/bomb/elements/bomba',
        '$/Effects/particles/sam_weapon/bomb/elements/bombc',
        '$/Effects/particles/sam_weapon/bomb/elements/bombd',
        '$/Effects/particles/sam_weapon/bomb/elements/bomb',
        '$/Effects/particles/sam_weapon/bomb'
        '$/Effects/particles/sam_weapon/bomb/elements',
        '$/Effects/particles/sam_weapon/bomb/elements/bombb/bombend',
        '$/Effects/particles/sam_weapon/bomb/elements/bombb/explode',
        '$/Effects/particles/sam_weapon/beam/power/elem',
        '$/Effects/particles/sam_weapon/beam/phazon',
        '$/Effects/particles/sam_weapon/beam/phazon/elem',
        '$/Effects/particles/sam_weapon/beam/phason',
        '$/Effects/particles/sam_weapon/beam/phason/elem',
        '$/Effects/particles/sam_weapon/beam/plasma',
        '$/Effects/particles/sam_weapon/beam/plasma/elem',
        '$/Effects/particles/sam_weapon/beam/plasma/2ndaryfx',
        '$/Effects/particles/sam_weapon/beam/wave',
        '$/Effects/particles/sam_weapon/beam/wave/elem',
        '$/Effects/particles/sam_weapon/beam/wave/2ndaryfx',
        '$/Effects/particles/sam_weapon/beam/ice/2ndaryfx',
        '$/Effects/particles/sam_weapon/icecombo',
        '$/Effects/particles/sam_weapon/grapple',
    ])
    part_names: Set[str] = set()
    part_names.update([
        'pollen'
        'pollen1'
    ])
    alpha_num = set()
    alpha_num.update([*'abcdefxy'])
    for i in range(10):
        for x in ['', *'abcdefxy']:
            alpha_num.add(f'{i}{x}')
            alpha_num.add(f'0{i}{x}')

    for key in res_dict:
        if res_dict[key][-4:] in ['part', 'swhc', 'elsc', 'wpsc', 'crsc', 'dpsc']:
            part_folder, part_name = os.path.split(res_dict[key])
            part_folders.add(part_folder)
            part_names.add(part_name)
            part_names.add(part_name[:-10] + '.crsm.crsc')
            part_names.add(part_name[:-10] + '.wpsm.wpsc')
            if deep_search:
                part_folders.add(part_folder + '/elem')
                part_folders.add(part_folder + '/elements')
                if part_name[-11].isdigit() or part_name[-12].isdigit():
                    end = -11
                    for i in [-11, -12, -13]:
                        if part_name[i].isdigit():
                            end = i
                    part_names.update([part_name[:end] + n + part_name[-10:] for n in alpha_num])
                    part_names.add(part_name[:end] + part_name[-10:])
                else:
                    part_names.update([part_name[:-10] + n + part_name[-10:] for n in alpha_num])

    for folder in part_folders:
        for part in part_names:
            commit = False #r'/RuinWorld/' in folder
            match_type = update_if_matched(f'{folder}/{part}', part[-5:] + "!!", res_dict, commit)
            if match_type == MatchType.NewMatch and commit:
                matched += 1

    return matched
