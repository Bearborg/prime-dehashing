import os

from extrapolating.update_if_matched import update_if_matched


mpr_scans_root = r'F:\Wikitroid Content\Room Scans\MPR\English'

def guess_scans_old(res_dict, match_scans=True, match_strings=True):
    """
    Leverages resource names from Prime Remastered to guess SCAN/STRG names in MP1. This code relies on an existing tool
    I had written to dump out the contents of MSBT files in Remastered, and is redundant now that all SCAN files present
    in Remastered have already been matched. I've left the code here for reference purposes, but without the exported
    MSBT contents it will not be directly useful for generating matches.
    :param res_dict: A dict of integer hashes to string filenames. Non-matching filenames should be suffixed with "!!".
    :param match_scans: Boolean to enable matching SCAN files.
    :param match_strings: Boolean to enable matching STRG files.
    :return: Number of newly-added filename matches, as an int.
    """
    print("Checking scans...")
    matched = 0

    world_scan_paths = {
        'IntroLevel' : '$/ScannableObjects/Intro_World/',
        'ChozoRuins' : '$/ScannableObjects/Chozo_Ruins/',
        'IceWorld' : '$/ScannableObjects/Ice_World/',
        'OverWorld' : '$/ScannableObjects/Overworld/',
        'Mines' : '$/ScannableObjects/Mines/',
        'LavaWorld' : '$/ScannableObjects/Lava_World/'
    }

    world_strg_paths = {
        'IntroLevel' : '$/Strings/English/Scan_Data/!Scans_Intro_Level/',
        'ChozoRuins' : '$/Strings/English/Scan_Data/!Scans_Chozo_Ruins/',
        'IceWorld' : '$/Strings/English/Scan_Data/!Scans_Ice_World/',
        'OverWorld' : '$/Strings/English/Scan_Data/!Scans_Overworld/',
        'Mines' : '$/Strings/English/Scan_Data/!Scans_Mines/',
        'LavaWorld' : '$/Strings/English/Scan_Data/!Scans_Lava_World/'
    }

    rooms = {
        'IntroLevel': [
            "00a_intro",  # "..._connect"
            "00b_intro_connect",
            "00b_map",  # This room doesn't actually exist
            "00c_intro",  # "..._connect"
            "00d_intro",  # "..._connect"
            "00e_intro",  # "..._connect"
            "00f_intro_begin",
            "00f_intro_end",
            "00g_intro-elev",  #should be "00g_intro_begin"
            "00g_intro_end",
            "00h_intro_mechshaft",
            "01_intro_hanger",
            "01_hanger connect",  # "01_intro_hanger_connect"
            "02_intro_elevator",
            "02_intro_epod_connect",
            "02_intro_epodroom",
            "03_intro_elevator",
            "04_intro_specimen", # "04_intro_specimen_chamber"
            "05_intro_zoo",  # "05_zoo"
            "06_Freight tunnel", # This room doesn't actually exist
            "06_intro_freight_lifts",
            "06_intro_to_reactor",
            "07_intro_reactor",
            "08a_intro_ventshaft",
            "08b_intro_ventshaft",
            "08c_intro_ventshaft",
            "08d_intro_ventshaft",
            "08e_intro_ventshaft",
            "08f_intro_ventshaft",
            "09_Ridley"  # "09_intro_ridley_chamber"
        ],
        'ChozoRuins': [
            "06_grapgallery",
            "0_elev_lava_b",
            "0_elev_over_a",
            "0_elev_over_e",
            "0_elev_over_f",
            "0a_connect",  # this room doesn't exist
            "0b_connect",  # "0b_connect_tunnel"
            "0c_connect",  # "0c_connect_tunnel"
            "0d_connect",  # "0d_connect_tunnel"
            "0e_connect",  # "0e_connect_tunnel"
            "0f_connect",  # "0f_connect_tunnel"
            "0g connect", # doesn't exist
            "0h_connect",  # "0h_connect_tunnel"
            "0i_connect",  # "0i_connect_tunnel"
            "0j_connect",  # "0j_connect_tunnel"
            "0k_connect",  # "0k_connect_tunnel"
            "0l_connect",  # "0l_connect_tunnel"
            "0m_connect",  # "0m_connect_tunnel"
            "0p_connect",  # "0p_connect_tunnel"
            "0q_connect",  # "0q_connect_tunnel"
            "0s_connect",  # "0s_connect_tunnel"
            "0t_connect",  # "0t_connect_tunnel"
            "0u_connect",  # "0u_connect_tunnel"
            "0v_connect (hall_f)",  # "0v_connect_tunnel"
            "0w_connect (hall_g)", # "0w_connect_tunnel"
            "10_energy_core_entrance",  # "10_coreentrance"
            "11_watery_hall",  # "11_wateryhall"
            "12_monkey_shaft",  # "12_monkeyshaft"
            "14_tl_base01",
            "14_tl_room01_02",
            "14_tower",  # this room doesn't exist
            "15_energy_cores",  # "15_energycore"
            "16_furnaces",
            "17_chozo_bowling",  # "17_chozobowling"
            "17_connect",
            "18_halfpipe",
            "18_halfpipe_connect_a",
            "18_halfpipe_connect_b",
            "19_hive_totem",  # "19_hivetotem"
            "01_main_plaza",  # "1_mainplaza"
            "1_savestation",
            "1_special",
            "01a_morphball_shrine",  # "1a_morphball_shrine"
            "1a_morphballtunnel2",
            "20_pickuproom",
            "20_reflecting_pool",
            "22_Flaahgra_Chamber",  # "22_flaahgraChamber"
            "02_main_hall",  # "2_mainhall"
            "2_savestation",
            "03_monkey_lower",  # "3_monkey_lower"
            "03_monkey_upper",  # "3_monkey_upper"
            "3_savestation",
            "04_maproom_d",  # "4_maproom_d"
            "4_monkey_hallway",
            "05_bath_hall",  # "5_bathhall"
            "7_ruinedroof",
            "08_courtyard",  # "8_courtyard"
            "99_some_hallway",
            "generic_x01",
            "generic_x02",
            "generic_x04",
            "generic_x05",
            "generic_x06",
            "generic_z02",
            "generic_z3",  # "generic_z03"
            "mapstation"
        ],
        'IceWorld': [
            "ice_elev lava c", # "00_ice_elev_lava_c"
            "00_ice_elev_lava_d",
            "00b_connect",  # "00b_ice_connect"
            "00d_ice_connect",
            "00e_ice_connect",
            "00f_ice_connect",
            "00g_ice_connect",
            "00h_connect",  # "00h_ice_connect"
            "00i_ice_connect",
            "00j connect", # "00j_ice_connect"
            "00k_ice_connect",
            "00l_connect",
            "00n_ice_connect",
            "00o_ice_connect",
            "00p_ice_connect",
            "00q_ice_connect",
            "00r_ice_connect",
            "00s_ice_connect",
            "01_main plaza", # "01_ice_plaza"
            "02_ice_ruins_a",
            "03_ice_ruins_b",
            "04_ice_boost canyon", # "04_ice_boost_canyon"
            "05_ice_shorlines",  # "05_ice_shorelines"
            "06_ice chapel",  # "06_ice_chapel"
            "06_ice_temple",
            "08_ice ridley", # "08_ice_ridley"
            "09_ice lobby", # "09_ice_lobby"
            "0 common elev a", # 0_common_elevator_a
            "0_common_elev b", # 0_common_elevator_b
            "10_ice research a",  # "10_ice_research_a"
            "11_ice observ", # "11_ice_observatory"
            "12_ice_research_b",
            "13_ice vault",  # "13_ice_vault"
            "14_ice_tower_a",
            "15_ice_cave_a",
            "16_ice_tower_b",
            "17_ice_cave_b",
            "18_ice_gravity_chamber",
            "19_ice_thardus",
            "generic_x1",
            "generic_z1",
            "generic_z2",
            "generic_z3",
            "generic_z4",
            "generic_z5",
            "generic_z6",
            "generic_z7",
            "generic_z8",
            "mapstation ice",  # "mapstation_ice"
            "pickup01",
            "pickup02",
            "pickup03",
            "pickup04",
            "savestation a", # "savestation_ice_a"
            "savestation b", # "savestation_ice_b"
            "savestation c"  # "savestation_ice_c"
        ],
        'OverWorld': [
            "00_over_elev_lava_l",
            "00_over_elev_mines_g",
            "over_elev_ruins",  # "00_over_elev_ruins_a"
            "00_over_elev_ruins_e",
            "00_over_elev_ruins_f",
            "00a_IntroUnderwater_Connect",
            "Over_Hall_A",  # "00a_over_hall"
            "Over_Hall_C",  # doesn't exist
            "00b_IntroUnderwater_connect",
            "Over Hall B",  # "00b_over_hall"
            "00c_IntroUnderwater_Connect",
            "00d_IntroUnderwater_connect",
            "Over_Hall_D",  # "00d_over_hall",
            "00e_IntroUnderwater_connect",
            "Over_Hall_F",  # "00f_over_hall",
            "00g_over_hall",
            "Over_Hall_J",  # "00j_over_hall",
            "00j_over_plaza_hall",
            "Over_Hall_K",  # "00k_over_hall",
            "Over_Hall_L",  # "00l_over_hall"
            "Over_Hall_M",  # "00m_over_hall",
            "Over_Hall_O",  # "00o_over_hall",
            "Over_Hall_T",  # "00t_over_hall"
            "01_main_plaza",  # "01_over_mainplaza"
            "Over Pickup Space Jump",  # "01_over_pickup_spacejump"
            "02_halfpipe",  # "02_over_halfpipe"
            "03_IntroUnderwater_elevator",
            "03_over_pickup",
            "03_Rootcave",  # "03_over_rootcave"
            "04_IntroUnderwater_specimen_chamber", # "04_IntroUnderwater_specimen_chamber"
            "04_over_pickup",  # "04_over_pickup"
            "04_over_treeroom",
            "05_IntroUnderwater_Zoo",  # "05_IntroUnderwaterZoo"
            "05_Over_xrayroom",
            "06_IntroUnderwater_Freight_Lifts",
            "06_IntroUnderwater_savestation",
            "06_IntroUnderwater_to_reactor",
            "04_crashed_ship", # "06_over_crashed_ship"
            "over_hall_crashed ship",  # "06_over_hall_crashedship"
            "07_IntroUnderwater_reactor",
            "07_Over_stonehenge",
            "07_Over_stonehenge_hall",
            "08a_IntroUnderwater_ventshaft",
            "08b_IntroUnderwater_ventshaft",
            "08c_IntroUnderwater_ventshaft"
        ],
        'Mines': [
            "00_crater_over_elev_j",
            "00a_crater_connect",
            "00b_crater_connect",
            "01_crater_dental",  # "01_crater_dental"
            "03a_crater",
            "03b_crater",
            "03c_crater",
            "03d_crater",
            "03e_crater",
            "03e_f_crater",
            "03f_crater",
            "missilerechargestation_crater",
            "00_mines_elev_over_g",  # "00_mine_lava_elev_g"
            "00_mines_lava_elev_h",
            "00_Mines_Mapstation",
            "00_mines_pickup_02",
            "00_mines_pickup_04",
            "00_Mines_Savestation_A",
            "00_mines_savestation_b",
            "00_mines_savestation_c",
            "00_mines_savestation_d",
            "00a_mines_connect",
            "00b_mines_connect",
            "00c_mines_connect",
            "00d_mines_connect",
            "00e_mines_connect",
            "00f_mines_connect",
            "00g_mines_connect",
            "00h_mines_connect",
            "00i_mines_connect",
            "00j_mines_connect",
            "00k_mines_connect",
            "00l_mines_connect",
            "00m_mines_connect",
            "00n_mines_connect",
            "00o_mines_connect",
            "00p_mines_connect",
            "00r_mines_connect",
            "00s_mines_connect",
            "01_mines_mainplaza",
            "02_mines_shootmeup",  # "02_mines_shootemup"
            "03_mines",
            "04_mines_pillar",
            "05_mines_forcefields",
            "06_mines_elitebustout",
            "07_mines_electric",
            "08_mines",
            "09_mines_mushroomhall",
            "10_mines_altmushroomhall",
            "11_mines",
            "12_ mines_eliteboss", # "12_mines_eliteboss"
            "13_mines_vertical_ascent",
            "1_2_mines_elevator",
            "2_3_mines_elevator"
        ],
        'LavaWorld': [
            "lava_elev_ice c", # "00_lava_elev_ice_c"
            "lava_elev_ice d", # "00_lava_elev_ice_d"
            "00_lava_elev_over_l",
            "lava_elev ruins b", # "00_lava_elev_ruins_b"
            "lava_elev mines h",
            "00a_lava_connect",
            "00b_lava_connect",
            "00c_lava_connect",
            "00d_lava_connect",
            "00e_lava_connect",
            "00f_lava_connect",
            "00g_lava_connect",
            "00h_lava_connect",
            "00i_lava_connect",
            "00j_lava_connect",
            "00k_lava_connect",
            "08_over_muddywaters_a",
            "09_lava_pickup",
            "09_over_monitortower",
            "10_over_1alavaarea",
            "11_over_muddywaters_b",
            "12_over_fieryshores",
            "13_lava_pickup",
            "13_over_burningeffigy",
            "14_lava_pickup",
            "14_over_magdolitepits",
            "23_lava_burningtrail",
            "a_lava_savestation",
            "b_lava_savestation"
        ]
    }

    generic_scan_paths = {
        'GameMechanics': '$/ScannableObjects/Game Mechanics/',
        'SpacePirateLog': '$/ScannableObjects/Space_Pirate_Log/',
        'ChozoLore': '$/ScannableObjects/Chozo_Lore/',
    }

    generic_strg_paths = {
        'GameMechanics': '$/Strings/English/Scan_Data/!Scans_Game_Mechanics/',
        'SpacePirateLog': '$/Strings/English/Scan_Data/!Scans_SpacePirate_Log/',
        'ChozoLore': '$/Strings/English/Scan_Data/!Scans_Chozo_Lore/',
    }

    catchall_scan_paths = [
        '$/ScannableObjects/Creatures/',
        '$/ScannableObjects/Crater/',
        '$/ScannableObjects/Tests/',
        '$/ScannableObjects/Intro_World/',
        '$/ScannableObjects/Chozo_Ruins/',
        '$/ScannableObjects/Ice_World/',
        '$/ScannableObjects/Overworld/',
        '$/ScannableObjects/Mines/',
        '$/ScannableObjects/Lava_World/'
    ]

    strg_substitutions = {
        '00a_door to airlock': '00a_Hall door to airlock',
        '00a_door to escape': '00a_Hall door to Escape pod',
        '00b_door to escape': '00b_map Door to Escape',
        '00b_door to map': '00b_map Door to map',
        '00g_door to elev': '00b_map door to Elevator',
        '00b_map panel 1 ': '00b_map panel 1',
        '00b_map panel 2 ': '00b_map panel 2',
        '00b_map panel 3 ': '00b_map panel 3',
        '00b_map panel 4 ': '00b_map panel 4',
        '00c_Intro door to bio': '00c_door to Bio-tech Research Area',
        '00c_Intro door to elev': '00c_door to elevator',
        '00c_Intro electrical arc': '00c_electrical arc',
        '00c_Intro holo 1': '00c_hologram 1',
        '00d_door to bio': '00d_door to Bio tech',
        '00e_tunnel string circle 1': '00e_Tunnel hologram string circle 1',
        '00e_tunnel string circle 2': '00e_Tunnel hologram string circle 2',
        '00e_tunnel string circle 3': '00e_Tunnel hologram string circle 3',
        '00g_door to 00g begin': '00g Entrance to 00g begin',
        '00g_door to reactor': '00g Entrance to reactor',
        '00g_door to Specimen': '00g Entrance to Specimen',
        '00g_Intro elev': '00g_end elevator',
        '00g_Intro platform': '00g_end platform',
        '01_hanger door after scan': '01_Hanger Con door after scan',
        '01_hanger door to hanger': '01_Hanger Con door to hanger',
        '01_Hanger door to main hanger': '01_Hanger Door to hall',
        '01_Hanger first hologram string 1': '01_Hanger First hologram string circle 1',
        '01_Hanger first hologram string 2': '01_Hanger First hologram string circle 2',
        '01_Hanger first hologram string 3': '01_Hanger First hologram string circle 3',
        '01_Hanger forcefield_2': '01_Hanger Forcefield 2',
        '01_Hanger panel to open gate': '01_Hanger Panel to second open gate',
        '01_Hanger samus ship': '01_Hanger Samus\' ship',
        '02_elev access': '02_elev activate elevator',
        '02_escape boss mouth': '02_Escape Dead boss mouth',
        '02_escape boss tail': '02_Escape Dead boss Tail',
        '02_escape boss': '02_Escape Dead boss',
        '02_escape door 00b': '02_Escape Door to 00b',
        '02_escape injured pir': '02_Escape Injured Pirate',
        '02_escape pod': '02_Escape Jettisoned pod',
        '03_Intro control panel access': '03_Elevevator control panel with access code',
        '03_Intro door to 00c': '03_Elevator Door to 00c',
        '03_Intro door to map': '03_Elevator Door to Map',
        '03_Intro platform': '03_Elevator platform',
        '04_spec dead queen': '04_Specimen Dead queen',
        '04_spec door to 00c': '04_Specimen Door to 00c',
        '04_spec door to 00d': '04_Specimen Door to 00d',
        '04_spec door to elev': '04_Specimen Door to elevator',
        '04_spec floor station': '04_Specimen Floor station',
        '04_spec injured pir 1': '04_Specimen injured Pirate 1',
        '04_spec injured pir 2': '04_Specimen injured Pirate 2',
        '04_spec lg 1': '04_Specimen lg panel 1',
        '04_spec lg 2': '04_Specimen lg panel 2',
        '04_spec lg 3': '04_Specimen lg panel 3',
        '04_spec lg 4': '04_Specimen lg panel 4',
        '04_spec panel 1': '04_Specimen Control panel 1',
        '04_spec panel 2': '04_Specimen Control panel 2',
        '04_spec panel 3': '04_Specimen Control panel 3',
        '04_spec tank': '04_Specimen Tank',
        '04_spec_heat vent': '04_Specimen Heat Vent',
        '05_Zoo boss': '05_Zoo Boss tank',
        '05_Zoo elevator panel bot': '05_Zoo Elevator panel bottom',
        '05_Zoo injured pir 1': '05_Zoo Injured Pirate 1',
        '05_Zoo injured pir 2': '05_Zoo Injured Pirate 2',
        '05_Zoo injured pir 3': '05_Zoo Injured Pirate 3',
        '05_Zoo injured pir 4': '05_Zoo Injured Pirate 4',
        '05_Zoo locked contain 1': '05_Zoo Locked containment 1',
        '05_Zoo locked contain 2': '05_Zoo Locked containment 2',
        '05_Zoo locked contain 3': '05_Zoo Locked containment 3',
        '05_Zoo locked contain 4': '05_Zoo Locked containment 4',
        '05_Zoo locked contain 5': '05_Zoo Locked containment 5',
        '06_Freight access panel': '06_Freightlifts top panel access code',
        '06_Freight clamp hologram': '06_Freightlifts hologram',
        '06_Freight clamp inactive': '06_Freightlifts Ball clamp inactive',
        '06_Freight clamp panel': '06_Freightlifts Ball clamp panel',
        '06_Freight Dead pirate 1': '06_Freightlifts Dead Pirate 1',
        '06_Freight Dead pirate 2': '06_Freightlifts Dead Pirate 2',
        '06_Freight door on': '06_Freightlifts Ball large door on',
        '06_Freight door to 00e': '06_Freightlifts door to 00e',
        '06_Freight door': '06_Freightlifts Ball large door',
        '06_Freight injured pir': '06_Freightlifts Injured Pirate ',
        '07_Reactor dead gr 1': '07_Reactor Dead pirate gr 1',
        '07_Reactor dead gr 2': '07_Reactor Dead pirate gr 2',
        '07_Reactor dead gr 3': '07_Reactor Dead pirate gr 3',
        '09_Ridley door to elev': '09_Ridley door to elevator',
        '09_Ridley grapple': '09_Ridley Grapple point',
        'turret disable': 'Turret Destroyed',
        '1_Main First Tree': '01_Main First Tree',
        '1_Main Holo to Shrine': '01_Main Holo to Shrine',
        '1_Main Leaves': '01_Main Leaves',
        '1_Main Stones on Ground': '01_Main Stones on Ground',
        '1_Main bridge': '01_Main bridge',
        '1_Main Energy': '01_Main Energy',
        '1_Main Missile': '01_Main Missile',
        '1_Main image': '01_Main image',
        '1a_Morph Halfpipe': '1a_Morph  Halfpipe',
        '03_Monkey_Lower contrap' : '03 Mon lower contrap',
        '03_Monkey_Upper Poison' : '03_Mon up Poison',
        '03_Monkey_Upper Ball openings' : '03_Mon up Ball openings',
        '4_Map_D hole1': '4 Map D hole 1',
        '4_Map_D hole 2': '4 Map D hole 2',
        '4_Map_D hole 3': '4 Map D hole 3',
        '0p Watefall': '0p Waterfall',
        '08_Court Large tree part 1': '08_Court  Large tree part 1',
        '08_Court Large tree leaves': '08_Court  Large tree leaves',
        '08_Court Bombable walls': '08_Court Bombable wall',
        '08_Court Branch supports': '08_Court  Branch supports',
        '22_Flaahgra Scan creature': '22_Flaah Scan creature',
        '22_Flaahgra tentacle': '22_Flaah  tentacle',
        '22_Flaahgra Mirror': '22_Flaah Mirror',
        '22_Flaahgra Poison': '22_Flaah Poison',
        '10_Ener_En Water pump': '10_Ener En Water pump',
        '10_Ener_En Wall sculpture 1': '10_Ener En Wall sculpture 1',
        '10_Ener_En Red Cylinders': '10_Ener En Red Cylinders',
        '11_Water Roots': '11_Water Roots ',
        '15_Ener_Cores Platforms inactive': '15 Ener Cores Platforms inactive',
        '15_Ener_Cores Core 1 inactive': '15 Ener Cores Core 1 inactive',
        '15_Ener_Cores Core 1 active': '15 Ener Cores Core 1 active',
        '15_Ener_Cores Core 2 active': '15 Ener Cores Core 2 active',
        '15_Ener_Cores Core 3 inactive': '15 Ener Cores Core 3 inactive',
        '15_Ener_Cores Core 3 active': '15 Ener Cores Core 3 active',
        '15_Ener_Cores 2nd hole inactive': '15 Ener Cores 2nd hole inactive',
        '03_Monkey_Lower Destructible wall': '03 Mon Lower Destructible wall',
        'Spinner inactive': '05_Ice_Shore Spinner inactive',
        'Spinner inactive initial': '05_Ice_Shore Spinner inactive initial',
        'Thardus': '19_Ice Thardus Thardus',
        '10_over_lava east gate': '10_over_lava east gate ',
        '04_Crash ship': '04 Crash ship',
        '04_Crash sap sacs': '04 Crash sap sacs',
        '04_Crash injured pirate 1': '04 Crash injured pirate 1',
        '04_Crash injured pirate 2': '04 Crash injured pirate 2',
        'Hall_T blue patches': 'Hall T blue patches',
        'Hall_L shrooms': 'Hall L shrooms',
        'Hall_L mini lights': 'Hall L mini lights',
        '02_Halfpipe halfpipe': '02 Halfpipe halfpipe',
        '02_Halfpipe tree': '02 Halfpipe tree',
        '02_Halfpipe twisted vines': '02 Halfpipe twisted vines',
        '03_Root beetle pile': '03 Root beetle pile',
    }

    for folder in os.scandir(mpr_scans_root):
        if folder.is_dir():
            for file in os.scandir(folder):
                if file.is_file():
                    matched_scan = 0
                    matched_strg = 0
                    filename = file.name[file.name.find('-') + 2:-4]
                    scan_filename = filename + '.scan'
                    strg_filename = strg_substitutions[filename] if filename in strg_substitutions else filename
                    strg_filename += '.strg'

                    if not filename.startswith('Unnamed'):
                        if match_scans:
                            if folder.name in world_scan_paths:
                                base_path = world_scan_paths[folder.name]
                                # try with no room first
                                matched_scan |= (
                                    update_if_matched(base_path + scan_filename, '.scan!!', res_dict).value
                                )
                                # try all rooms
                                for room in rooms[folder.name]:
                                    matched_scan |= update_if_matched(f'{base_path}{room}/{scan_filename}',
                                                                   '.scan!!', res_dict).value

                            elif folder.name in generic_scan_paths:
                                folder_path = generic_scan_paths[folder.name]
                                if scan_filename == 'Chozo Lore 001.scan':  # Special case, this one moved
                                    folder_path = '$/ScannableObjects/Chozo_Ruins/0q_connect/'

                                new_path = f'{folder_path}{scan_filename}'
                                matched_scan |= update_if_matched(new_path, '.scan!!', res_dict).value

                            for path in catchall_scan_paths:
                                new_path = f'{path}{scan_filename}'
                                matched_scan |= update_if_matched(new_path, '.scan!!', res_dict).value

                            if matched_scan == 0:
                                print(f'Unmatched scan: {folder.name}/{scan_filename}')
                            elif matched_scan % 2 == 1:
                                matched += 1

                        if match_strings:


                            if folder.name in world_strg_paths:
                                base_path = world_strg_paths[folder.name]
                                matched_strg |= (
                                    update_if_matched(base_path + strg_filename, '.strg!!', res_dict).value
                                )

                            elif folder.name in generic_strg_paths:
                                base_path = generic_strg_paths[folder.name]
                                matched_strg |= (
                                    update_if_matched(base_path + strg_filename, '.strg!!', res_dict).value
                                )

                            base_path = '$/Strings/English/Scan_Data/!Scans_Game_Mechanics/'
                            matched_strg |= (
                                update_if_matched(base_path + strg_filename, '.strg!!', res_dict).value
                            )

                            if matched_strg == 0:
                                print(f'Unmatched string: {folder.name}/{strg_filename}')
                            elif matched_strg % 2 == 1:
                                matched += 1
                    elif match_strings:
                        if res_dict[int(filename[8:16], 16)].endswith('!!'):
                            print(f'Unmatched MPR strg: {res_dict[int(filename[8:16], 16)]}')

    return matched