import xml.etree.ElementTree as ET
from utils.crc32 import crc32, remove_suffix
from typing import Dict, List
from dataclasses import dataclass
import os
import sqlite3
import itertools


@dataclass
class Property:
    hash: int
    name: str
    type: str
    def matched(self):
        if hex(self.hash)[2:] in [b'INAM'.hex(), b'XFRM'.hex(), b'ACTV'.hex()]:
            return True  # Force success for hardcoded editor properties
        return crc32(self.name + self.type) == self.hash

    def __init__(self, element: ET.Element):
        key_elem = element.find('Key')
        self.hash = int(key_elem.attrib['ID'], 16)
        self.name = element.find('Value').attrib['Name']
        self.type = key_elem.attrib['Type']

@dataclass
class PropertyUsage:
    hash: int
    type: str
    source: str
    game: str

@dataclass
class EnumValue:
    hash: int
    name: str
    game: str
    source: str
    def matched(self):
        return crc32(self.name) == self.hash

db_path = './script_properties.db'
g_curr_game = ''
g_curr_template = ''
g_enums: Dict[int, List[EnumValue]] = dict()
g_property_usages: List[PropertyUsage] = []

start_red = '\033[91m'
start_green = '\033[92m'
start_yellow = '\033[93m'
start_blue = '\033[94m'
end_color = '\033[0m'
pwe_type_lookup = {
    "Int": "int",
    "Bool": "bool",
    "Enum": "enum",
    "Float": "float",
    "String": "string",
    "Asset": "asset",
    "Spline": "spline",
    "Choice": "choice",
    "Array": "array",
    "Sound": "sound",
    "Guid": "guid",
}

def parse_key_value_pairs(parent_node: ET.Element):
    ret = dict()
    for obj in parent_node.iterfind("Element"):
        ret[obj.find("Key").text] = obj.find("Value").attrib["Path"]
    return ret

def validate_enum(enum_node: ET.Element):
    values = enum_node.find("Values")
    name_node = enum_node.find("Name")
    name_suffix = ""
    if name_node is not None:
        name_suffix = f" in {name_node.text}"
    if values is None:
        return
    for val in values.iterfind("Element"):
        e_hash = int(val.attrib["ID"], 16)
        e_name = val.attrib["Name"]
        g_enums[e_hash] = (g_enums.get(e_hash) or []) + [EnumValue(e_hash, e_name, g_curr_game, g_curr_template)]

def validate_property_recursive(elem: ET.Element, structs: Dict[str, str], property_map: Dict[int, List[Property]]):
    """
    All recursive-safe validation for a property.
    """
    elem_hash = int(elem.attrib["ID"], 16)
    elem_type = elem.attrib["Type"]
    if elem_type in pwe_type_lookup:
        elem_type = pwe_type_lookup[elem_type]
    if elem_type == "enum":
        if "Archetype" in elem.attrib:
            archetype = elem.attrib["Archetype"]
            if archetype not in structs:
                print(start_red + f"Missing Archetype: '{archetype}'" + end_color)
        else:
            validate_enum(elem)
    if ((elem_type != "Struct") and
        (elem_type != "AnimationSet") and # todo handle this better
        (elem_hash in property_map) and
        (elem_type not in (expected_types := [prop.type for prop in property_map[elem_hash]])) and
        (not (elem_type in ["enum", "choice"] and ("Archetype" in elem.attrib) and (elem.attrib["Archetype"] in expected_types)))):
        print(f"{start_red}Unexpected type for {hex(elem_hash)}: '{elem_type}' in {g_curr_template}. Expected {expected_types}{end_color}")
    g_property_usages.append(PropertyUsage(elem_hash, elem_type, g_curr_template, g_curr_game))
    subproperties = elem.find("SubProperties")
    if subproperties is not None:
        for sub_elem in subproperties.iterfind("Element"):
            validate_property_recursive(sub_elem, structs, property_map)

def validate_property(elem: ET.Element, structs: Dict[str, str], property_map: Dict[int, List[Property]]):
    """
    Outer-layer-only property validation. Checks only things that are not available on inner properties, e.g. struct
    types, hash validity.
    """
    elem_hash = int(elem.attrib["ID"], 16)
    assert elem_hash in property_map, f'Missing hash: {hex(elem_hash)}'
    if elem.attrib["Type"] == "Struct":
        if (archetype := elem.attrib["Archetype"]) not in structs:
            print(start_red + f"Missing Archetype: '{archetype}'" + end_color)
        if elem.attrib["Archetype"] not in (expected_types := [prop.type for prop in property_map[elem_hash]]):
            print(f"{start_red}Unexpected type for {hex(elem_hash)}: '{elem.attrib["Archetype"]}' in {g_curr_template}. Expected {expected_types}{end_color}")
    validate_property_recursive(elem, structs, property_map)


def validate_template(template_path: str, structs: Dict[str, str], property_map: Dict[int, List[Property]]):
    root_node = ET.parse(template_path).getroot()
    assert root_node.tag in ("ScriptObject", "PropertyTemplate"), f"Unrecognized template root: {root_node.tag}"
    if root_node.tag == "ScriptObject":
        properties = root_node.find("Properties")
        # print(properties.find("Name").text)
    else: # root_node.tag == "PropertyTemplate"
        properties = root_node.find("PropertyArchetype")
        # print(properties.find("Name").text)
        prop_type = properties.attrib["Type"]
        if prop_type == "Choice":
            return
        elif prop_type == "Enum":
            validate_enum(properties)
            return
        else:
            assert prop_type == "Struct", f"Unrecognized PropertyArchetype type {prop_type}"
    is_atomic = (properties.find("Atomic") is not None) and (properties.find("Atomic").text.lower() == "true")
    if is_atomic:
        return
    subproperties = properties.find("SubProperties")
    if subproperties is None:
        print(start_red + f"Empty SubProperties: {properties.find("Name").text}" + end_color)
        return
    for elem in subproperties.iterfind("Element"):
        validate_property(elem, structs, property_map)


def parse_templates(game_root: str, property_map: Dict[int, List[Property]]):
    archive = ET.parse(os.path.join(game_root, 'Game.xml')).getroot()
    objects = parse_key_value_pairs(archive.find('ScriptObjects'))
    structs = parse_key_value_pairs(archive.find('PropertyArchetypes'))
    misc = parse_key_value_pairs(archive.find('MiscTemplates'))
    all_paths = {*objects.values(), *structs.values(), *misc.values()}

    for item in os.listdir(game_root):
        if os.path.isdir(item_path := os.path.join(game_root, item)):
            assert item in ['Enums', 'Misc', 'Script', 'Structs'], f"Unrecognized folder {item}"
            for child_item in os.listdir(item_path):
                assert os.path.isfile(child_item_path := os.path.join(item_path, child_item))
                rel_path = f'{item}/{child_item}'
                assert rel_path in all_paths, f"Unregistered template {rel_path}"
                all_paths.remove(rel_path)

                global g_curr_template
                g_curr_template = rel_path

                validate_template(child_item_path, structs, property_map)
        else:
            assert item == 'Game.xml', f"Unrecognized file {item}"
    assert len(all_paths) == 0, f"Missing items: {all_paths}"


def build_property_map(xml_file: str) -> Dict[int, List[Property]]:
    tree = ET.parse(xml_file)
    properties_xml = tree.getroot().find('PropertyMap')
    properties_by_id: Dict[int, List[Property]] = dict()
    for element in properties_xml:
        prop = Property(element)
        properties_by_id[prop.hash] = (properties_by_id.get(prop.hash) or []) + [prop]
    return properties_by_id


def check_duplicate_hashes(property_map_xml):
    tree = ET.parse(property_map_xml)

    properties_xml = tree.getroot().find('PropertyMap')
    properties_by_id: Dict[int, Property] = dict()
    for element in properties_xml:
        prop = Property(element)
        if prop.hash not in properties_by_id or prop.matched():
            if prop.hash in properties_by_id:
                print(f"{prop.hash:08x} {properties_by_id[prop.hash].type} -> {prop.type}")
            properties_by_id[prop.hash] = prop
        elif prop.hash in properties_by_id and properties_by_id[prop.hash].matched():
            print(f"{prop.hash:08x} {prop.type} -> {properties_by_id[prop.hash].type}")
        elif prop.hash in properties_by_id and not prop.matched():
            print(f"{prop.hash:08x} {prop.type} -?> {properties_by_id[prop.hash].type}")
        if not prop.matched() and prop.type in ['int', 'sound', 'choice', 'asset', 'enum']:
            for prop_type in ['sound', 'choice', 'asset', 'enum', 'int', 'characteranimation']:
                if crc32(prop.name + prop_type) == prop.hash:
                    print(f"{prop.hash:08x} {prop.type} -> {prop_type}")


def generate_rewound_hashes(properties_by_id: Dict[int, List[Property]]) -> Dict[int, List[int]]:
    rewound_hashes = dict()
    for i, key in enumerate(properties_by_id):
        for prop in properties_by_id[key]:
            rewound_hash = remove_suffix(prop.hash, prop.type)
            rewound_hashes[rewound_hash] = (rewound_hashes.get(rewound_hash) or []) + [prop.hash]

    return rewound_hashes


def update_enums(property_root_folder: str, enum_dict: Dict[int, List[EnumValue]]):
    for key, uses in enum_dict.items():
        if len(uses) > 1:
            matched_names = set([y.name for y in filter(lambda x: x.matched(), uses)])
            assert len(matched_names) < 2
            unmatched: List[EnumValue] = list(filter(lambda x: not x.matched(), uses))
            if len(unmatched) > 0 and len(matched_names) > 0:
                matched_name = matched_names.pop()
                for usage in unmatched:
                    print(f"{start_green}Rename {usage.game}/{usage.source} hash {hex(key)} from {usage.name} to {matched_name}{end_color}")
                    file_path = os.path.join(property_root_folder, usage.game, usage.source)
                    assert os.path.isfile(file_path)
                    with open(file_path, 'r+', encoding='utf8') as xml_file:
                        xml_text = xml_file.read()
                        xml_text = xml_text.replace(f'<Element Name="{usage.name}" ID="0x{key:X}"/>', f'<Element Name="{matched_name}" ID="0x{key:X}"/>')
                        xml_file.seek(0)
                        xml_file.write(xml_text)
                        xml_file.truncate()
                    usage.name = matched_name

def write_xml_in_pwe_format(tree: ET.ElementTree, out_path):
    ET.indent(tree, space=" " * 4, level=0)
    tree_str = ET.tostring(tree.getroot(), encoding='unicode')
    tree_str = tree_str.replace(' />', '/>')
    with open(out_path, 'w') as out_file:
        out_file.write(f'<?xml version="1.0" encoding="UTF-8"?>\n{tree_str}\n')

def rename_struct(game_root: str, property_map_xml: str, old_name: str, new_name: str):
    assert old_name != new_name
    archive_path = os.path.join(game_root, 'Game.xml')
    archive = ET.parse(archive_path)
    target = archive.find(f"./PropertyArchetypes/Element/Key[.='{old_name}']/..")
    assert target is not None, f"Could not find type '{old_name}'"
    collision = archive.find(f"./PropertyArchetypes/Element/Key[.='{new_name}']/..")
    assert collision is None, f"A type named '{new_name}' already exists"
    target_rel_path = target.find('Value').attrib['Path']
    dest_rel_path = target_rel_path.replace(old_name, new_name)

    target.find("Key").text = new_name
    target.find('Value').attrib['Path'] = dest_rel_path
    archetypes = archive.find(f"./PropertyArchetypes")
    archetypes[:] = sorted(archetypes, key=lambda x: x.find("Key").text)
    write_xml_in_pwe_format(archive, archive_path)

    target_abs_path = os.path.join(game_root, target_rel_path)
    dest_abs_path = os.path.join(game_root, dest_rel_path)
    struct_content = ET.parse(target_abs_path)
    struct_content.find('./PropertyArchetype/Name').text = new_name
    write_xml_in_pwe_format(struct_content, dest_abs_path)
    os.remove(target_abs_path)

    # update uses in structs
    instances: set[int] = set()
    for root, dirs, files in os.walk(game_root):
        for file in files:
            template_file_path = os.path.join(root, file)
            template_content = ET.parse(template_file_path)
            target_elements = template_content.findall(f".//Element[@Type='Struct'][@Archetype='{old_name}']")
            if len(target_elements) > 0:
                for element in target_elements:
                    instances.add(int(element.attrib['ID'], 16))
                    element.attrib['Archetype'] = new_name
                write_xml_in_pwe_format(template_content, template_file_path)

    # update propertymap
    property_map_content = ET.parse(property_map_xml)
    for instance in instances:
        target_elements = property_map_content.findall(f".//Element/Key[@Type='{old_name}'][@ID='0x{instance:X}']")
        existing_elements = property_map_content.findall(f".//Element/Key[@Type='{new_name}'][@ID='0x{instance:X}']/..")
        if len(existing_elements) > 0:
            assert len(existing_elements) == 1
            for elem in target_elements:
                property_map_content.getroot().find('PropertyMap').remove(elem)
            continue
        if len(target_elements) != 1:
            print(f'{start_yellow}{len(target_elements)} matches found while renaming {old_name} {instance:#x}{end_color}')
        for element in target_elements:
            element.attrib['Type'] = new_name
    write_xml_in_pwe_format(property_map_content, property_map_xml)

    print(f"{start_blue}Renamed {target_rel_path} -> {dest_rel_path}{end_color}")

def update_manual_guesses(property_map_xml: str, guesses: List[str]):
    property_map = build_property_map(property_map_xml)
    rewound_map = generate_rewound_hashes(property_map)
    tree = ET.parse(property_map_xml)

    for guess in guesses:
        if (guess_hash := crc32(guess)) in property_map:
            target = list(filter(lambda x: guess.endswith(x.type), property_map[guess_hash]))
            assert len(target) == 1, f'{len(target)} matches for {hex(guess_hash)}'
            guessed_type = target[0].type
            guessed_name = guess[:-len(guessed_type)]
        elif (partial_guess_hash := crc32(guess)) in rewound_map:
            guessed_name = guess
            for match in rewound_map[guess_hash]:
                guess_hash = match
                target = list(filter(lambda x: x.hash == crc32(x.type, partial_guess_hash), property_map[match]))
                assert len(target) == 1
                guessed_type = target[0].type
        else:
            print(f'{start_red}No match: {guess}{end_color}')
            continue
        if len(list(filter(lambda x: x.name != guessed_name, property_map[guess_hash]))) == 0:
            # All target names already match
            continue
        target_nodes = tree.findall(f"./PropertyMap/Element/Key[@ID='0x{guess_hash:X}']/..")
        assert len(target_nodes) > 0
        for target_node in target_nodes:
            if target_node.find("Value").attrib["Name"] != guessed_name:
                if (curr_type := target_node.find("Key").attrib["Type"]) == guessed_type:
                    print(f"{start_green}Match: 0x{guess_hash:08x} = {guessed_name} ({guessed_type}){end_color}")
                else:
                    print(f"{start_yellow}Partial match: 0x{guess_hash:08x} = {guessed_name} "
                          f"({start_green}{guessed_type}{start_yellow}/{curr_type}){end_color}")
                target_node.find("Value").attrib["Name"] = guessed_name

    write_xml_in_pwe_format(tree, property_map_xml)

def update_partial_matches(property_map_xml: str, partial_matches: Dict[int, str]):
    property_map = build_property_map(property_map_xml)
    tree = ET.parse(property_map_xml)

    for key, name in partial_matches.items():
        if key in property_map:
            target = list(filter(lambda x: name.endswith(x.type), property_map[key]))
            assert len(target) == 1, f'{len(target)} matches for {hex(key)}'
            guessed_type = target[0].type
            guessed_name = name[:-len(guessed_type)]
        else:
            raise Exception(f"No match found for key {key}")
        if len(list(filter(lambda x: x.name != guessed_name, property_map[key]))) == 0:
            # All target names already match
            continue
        target_nodes = tree.findall(f"./PropertyMap/Element/Key[@ID='0x{key:X}']/..")
        assert len(target_nodes) > 0
        for target_node in target_nodes:
            if target_node.find("Value").attrib["Name"] != guessed_name:
                curr_type = target_node.find("Key").attrib["Type"]
                print(f"{start_yellow}Partial match: 0x{key:08x} = {guessed_name} ({curr_type}){end_color}")
                target_node.find("Value").attrib["Name"] = guessed_name

    write_xml_in_pwe_format(tree, property_map_xml)

def update_db(property_map: Dict[int, List[Property]], enum_map: Dict[int, List[EnumValue]]):
    print("Updating property DB...")
    connection = sqlite3.connect(db_path)
    connection.execute('DELETE FROM property_names')
    props_for_db = [(hex(prop.hash), prop.type, prop.name, prop.matched()) for prop in itertools.chain(*property_map.values())]
    connection.executemany('INSERT INTO property_names VALUES(?, ?, ?, ?) '
                           'ON CONFLICT DO UPDATE '
                           'SET name = excluded.name, name_matches = excluded.name_matches', props_for_db)
    connection.execute('DELETE FROM enum_names')
    enums_for_db = [(hex(enum.hash), enum.name, enum.game, enum.source, enum.matched()) for enum in itertools.chain(*enum_map.values())]
    connection.executemany('INSERT INTO enum_names VALUES(?, ?, ?, ?, ?) '
                           'ON CONFLICT DO UPDATE '
                           'SET name = excluded.name, name_matches = excluded.name_matches', enums_for_db)
    connection.execute('DELETE FROM property_usages')
    prop_usages_for_db = [(None, hex(usg.hash), usg.type, usg.source, usg.game) for usg in g_property_usages]
    connection.executemany('INSERT INTO property_usages VALUES(?, ?, ?, ?, ?) ', prop_usages_for_db)
    connection.commit()
    connection.close()
    print("Done!")


def main(property_root_folder: str):
    property_map = build_property_map(os.path.join(property_root_folder, 'PropertyMap.xml'))
    subdirs = list(map(lambda x: x.name, filter(lambda x: x.is_dir(), os.scandir(property_root_folder))))
    subdirs.remove('.git')
    subdirs.remove('MP1')
    subdirs.remove('MP1R')
    ordered_subdirs = ['MP2Demo', 'MP2', 'MP3Proto', 'MP3', 'DKCR']
    assert set(ordered_subdirs) == set(subdirs)
    for item in ordered_subdirs:
        if os.path.isdir(item_path := os.path.join(property_root_folder, item)):
            global g_curr_game
            g_curr_game = item
            parse_templates(item_path, property_map)
    props_matched = len(list(filter(lambda x: len(list(filter(lambda y: y.matched(), x))) > 0, property_map.values())))
    props_total = len(property_map.keys())
    enums_matched = len(list(filter(lambda x: len(list(filter(lambda y: y.matched(), x))) > 0, g_enums.values())))
    enums_total = len(g_enums.keys())

    print(f'Property progress: {props_matched}/{props_total} - {props_matched/props_total:.2%}')
    print(f'Enum progress: {enums_matched}/{enums_total} - {enums_matched/enums_total:.2%}')
    update_enums(property_root_folder, g_enums)
    update_db(property_map, g_enums)


if __name__ == '__main__':
    props_root = r'F:\Documents\Code\retro-script-object-templates'
    prop_map_path = os.path.join(props_root, 'PropertyMap.xml')
    # prop_map = build_property_map(r'F:\Documents\Code\retro-script-object-templates\PropertyMap.xml')
    # # prop_map = {y: prop_map[y] for y in filter(lambda x: prop_map[x][0].type.lower() != prop_map[x][0].type, prop_map)}
    # rewound = generate_rewound_hashes(prop_map)
    # for k, v in rewound.items():
    #     print(f'0x{k:08x}: {", ".join([f"0x{r:08x}" for r in v])}')
    # parse_templates(r"F:\Documents\Code\retro-script-object-templates\MP3", prop_map)
    # rename_struct(r'F:\Documents\Code\retro-script-object-templates\DKCR', prop_map_path, 'UnknownStruct167', 'InventoryScreen')
    # rename_struct(r'F:\Documents\Code\retro-script-object-templates\MP2', prop_map_path, 'SafeZoneStructA', 'SafeZoneFog')
    # rename_struct(r'F:\Documents\Code\retro-script-object-templates\MP2Demo', prop_map_path, 'SpawnPointStruct', 'PlayerInventory')
    # rename_struct(r'F:\Documents\Code\retro-script-object-templates\MP3', prop_map_path, 'Inventory', 'PlayerInventory')
    # rename_struct(r'F:\Documents\Code\retro-script-object-templates\DKCR', prop_map_path, 'TweakControls_UnknownStruct2', 'PlayerMovementControls')

    # partial_matches = {}
    # update_partial_matches(prop_map_path, partial_matches)
    manual_guesses = [
        # *[f'Attack{o}ChickenFlyerAttackData' for o in [*string.digits]],
        # 'BallCameraCommonFullSpeedMinHeightfloat',
        # 'MaxTurnSpeedOccludedfloat',
        # 'ShadowDashInvisiblebool',
        # 'ChildrenAliveTimefloat',
        # 'AudioPeanutGunPitchfloat',
        # 'AudioScaleFactorfloat',
        # 'HelmetPitchFactorfloat',
        # 'NodeTypeButtonAlphafloat',
        # 'OverKillThresholdfloat',
        # 'EffectGenerationDistfloat',
        # 'ConverseCastListenersbool',
        # 'ConverseInsertVsAlignbool',
        # 'HealthMessageThresholdfloat',
    ]
    update_manual_guesses(prop_map_path, manual_guesses)
    check_duplicate_hashes(prop_map_path)
    main(props_root)
    # todo: find a broader wordlist?
    # todo: convert Flags to archetype