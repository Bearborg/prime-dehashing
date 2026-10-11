import struct
from typing import List, Dict, Tuple
from dataclasses import dataclass
from typing import BinaryIO
import sqlite3

mp3_obj_types: Dict[str, str] = {
    'ACHI': 'Achievement',
    'ACKF': 'ActorKeyframe',
    'ACTR': 'Actor',
    'ADMG': 'AreaDamage',
    'AIFZ': 'AIFuse',
    'AIHT': 'AIHint',
    'AIKF': 'AIKeyframe',
    'AITP': 'AITaskPoint',
    'AIWP': 'AIWaypoint',
    'ALRM': 'AlarmController',
    'AMIA': 'AmbientAI',
    'AMOR': 'ActorMorph',
    'AOCL': 'AudioOccluder',
    'ASAS': 'AreaStreamedAudioState',
    'ATMA': 'AtomicAlpha',
    'ATRN': 'ActorTransform',
    'AUR1': 'AuroraUnit1',
    'AUR2': 'AuroraUnit2',
    'AVIS': 'AudioVisualizer',
    'AVMC': 'AreaVisitMapController',
    'BALS': 'SpiderBallAttractionSurface',
    'BALT': 'BallTrigger',
    'BALW': 'SpiderBallWaypoint',
    'BEAM': 'Beam',
    'BLUR': 'CameraBlurKeyframe',
    'BLWF': 'BlinkWolf',
    'BOS3': 'SeedBoss3',
    'BSKR': 'Berserker',
    'BSTR': 'BeastRider',
    'CABL': 'Cable',
    'CABP': 'ContextActionButtonPressing',
    'CACL': 'ContextActionCombinationLock',
    'CAIF': 'ContextActionImageFocus',
    'CAMH': 'CameraHint',
    'CAMP': 'CameraPitch',
    'CAMS': 'CameraShaker',
    'CANB': 'CannonBall',
    'CAWL': 'ContextActionWelding',
    'CINE': 'CinematicCamera',
    'CLRM': 'ColorModulate',
    'CMBT': 'CombatTrooper',
    'CNTA': 'ControllerAction',
    'CNTR': 'Counter',
    'COVR': 'CoverPoint',
    'CRAR': 'CrossAreaRelay',
    'CRLY': 'ConditionalRelay',
    'CSAC': 'ContextSensitiveAction',
    'CSAT': 'ContextSensitiveActivator',
    'CTLH': 'ControlHint',
    'DEBR': 'Debris',
    'DEFM': 'DefenseMechanoid',
    'DFOG': 'DistanceFog',
    'DGMN': 'DialogueMenu',
    'DKSE': 'DarkSamusEcho',
    'DLHT': 'DynamicLight',
    'DMGA': 'DamageActor',
    'DOCK': 'Dock',
    'DOOR': 'Door',
    'DRKS': 'DarkSamus',
    'DTRG': 'DamageableTrigger',
    'DTRO': 'DamageableTriggerOrientated',
    'EFCT': 'Effect',
    'EFTR': 'EffectRepulsor',
    'EMPU': 'ElectroMagneticPulse',
    'EYEP': 'EyePod',
    'FGHS': 'FargullHatcherSwarm',
    'FGHT': 'FargullHatcher',
    'FILT': 'CameraFilterKeyframe',
    'FISH': 'FishCloud',
    'FLAR': 'VisorFlare',
    'FLPS': 'FalsePerspective',
    'FLYP': 'FlyingPirate',
    'FOGO': 'FogOverlay',
    'FOGV': 'FogVolume',
    'FRND': 'Friendly',
    'FSHM': 'FishCloudModifier',
    'FSWM': 'FlyerSwarm',
    'FXDC': 'EnvFxDensityController',
    'GAND': 'Gandrayda',
    'GENR': 'Generator',
    'GHOR': 'GhorLowerBody',
    'GHRU': 'GhorUpperBody',
    'GMNU': 'GuiMenu',
    'GNTB': 'GunTurretBase',
    'GNTT': 'GunTurretTop',
    'GOBD': 'GeneratedObjectDeleter',
    'GRAP': 'GrapplePoint',
    'GRFL': 'GragnolFlyer',
    'GSAC': 'GellSac',
    'GSCR': 'GuiScreen',
    'GSLD': 'GuiSlider',
    'GWIG': 'GuiWidget',
    'HHNT': 'HUDHint',
    'HINT': 'PlayerHint',
    'IFTC': 'IncomingFieldTransmission',
    'KRAK': 'Korakk',
    'KRBA': 'KorbaSnatcherSwarm',
    'KRBM': 'KorbaMaw',
    'LODC': 'LODController',
    'LUAX': 'LUAScript',
    'LVOL': 'LightVolume',
    'MEMO': 'HUDMemo',
    'MHAT': 'MetroidHatcher',
    'MHOP': 'MetroidHopper',
    'MIIA': 'MiiAccessory',
    'MINI': 'MinorIng',
    'MMDL': 'MultiModelActor',
    'MOVI': 'StreamedMovie',
    'MPHZ': 'MetroidPhazeoid',
    'MREE': 'Metaree',
    'MRLY': 'MemoryRelay',
    'MYSF': 'MysteryFlyer',
    'NBAR': 'Nightbarb',
    'NOTU': 'NoseTurret',
    'OPAA': 'OptionalAreaAsset',
    'PARA': 'Parasite',
    'PCKP': 'Pickup',
    'PCTL': 'PathControl',
    'PDBR': 'PhysicsDebris',
    'PDRN': 'PirateDrone',
    'PGVS': 'PlayerGravityScalar',
    'PHHR': 'PhazonHarvester',
    'PHPF': 'PhazonPuffer',
    'PHZD': 'Phaazoid',
    'PHZS': 'PhazonFlyerSwarm',
    'PILL': 'PillBug',
    'PIRT': 'SpacePirate',
    'PLAC': 'PlayerActor',
    'PLAT': 'Platform',
    'PLCH': 'PhazonLeech',
    'PLPX': 'PlayerProxy',
    'PMCT': 'PathMeshCtrl',
    'POIN': 'PointOfInterest',
    'PPDL': 'PhazonPuddle',
    'PSSM': 'PlantScarabSwarm',
    'PTNT': 'PhazonTentacle',
    'PUAP': 'PlayerUserAnimPoint',
    'PUFR': 'Puffer',
    'RADD': 'RadialDamage',
    'REAA': 'AreaAttributes',
    'REPH': 'ReptilicusHunter',
    'REPL': 'Repulsor',
    'RID1': 'Ridley1',
    'RIPL': 'Ripple',
    'RMAC': 'RoomAcoustics',
    'RRLY': 'RandomRelay',
    'RSPL': 'RainSplash',
    'RUMB': 'RumbleEffect',
    'RUND': 'Rundas',
    'SAMD': 'StreamedAudioModifier',
    'SAMF': 'SamusForm',
    'SB2G': 'SeedBoss2GiantForm',
    'SB2P': 'SeedBoss2PrimeBot',
    'SB2X': 'SeedBoss2BotSwarm',
    'SBEM': 'ScanBeam',
    'SBMI': 'SkyboxModInca',
    'SBO1': 'SeedBoss1Orb',
    'SCIC': 'ScanIncoming',
    'SCTL': 'SurfaceControl',
    'SDB1': 'SeedBoss1',
    'SDRN': 'SteamDrone',
    'SHBG': 'ShellBug',
    'SHBR': 'ShipBombingRun',
    'SHCI': 'ShipCommandIcon',
    'SHCP': 'ShipCommandPath',
    'SHDW': 'ShadowProjector',
    'SHHC': 'ShipHudControl',
    'SHIP': 'Ship',
    'SHPX': 'ShipProxy',
    'SKRP': 'SkyRipple',
    'SLCT': 'ScriptLayerController',
    'SNAG': 'SnagVineHelper',
    'SNDM': 'SoundModifier',
    'SOND': 'Sound',
    'SPDC': 'ShipDecalController',
    'SPFN': 'SpecialFunction',
    'SPIN': 'Spinner',
    'SPRL': 'PositionRelay',
    'SPRT': 'Sprite',
    'SPWN': 'SpawnPoint',
    'SQTR': 'SequenceTimer',
    'SRLY': 'Relay',
    'STAU': 'StreamedAudio',
    'STEM': 'Steam',
    'STMB': 'SteamBot',
    'STML': 'SteamLord',
    'SUBT': 'Subtitles',
    'SWBT': 'SwarmBot',
    'SWJT': 'ScrewAttackWallJumpTarget',
    'SWRM': 'WallCrawlerSwarm',
    'SWTC': 'Switch',
    'TEL1': 'WorldTeleporter',
    'TGPT': 'TargetingPoint',
    'TIMR': 'Timer',
    'TKEY': 'TimeKeyframe',
    'TMAI': 'TeamAI',
    'TRGR': 'Trigger',
    'TXPN': 'TextPane',
    'VGOO': 'VisorGoo',
    'VOLG': 'VolGroup',
    'WATR': 'Water',
    'WAYP': 'Waypoint',
    'WEED': 'VenomWeed',
    'WLDA': 'WorldAttributes',
    'WLIT': 'WorldLightFader',
    'WPNG': 'WeaponGenerator',
    'WTAT': 'WorldTeleporterAttributes',
    'WTCR': 'WorldTransitionChoiceRelay',
}
object_type_lookup: Dict[str, Dict[object, str]] = {
    'MP3C': mp3_obj_types
}
game_lookup: Dict[str, str] = {
    'MP3C': 'MP3/NTSC'
}

@dataclass
class DependencyNode:
    unk: bool
    type: str

    def __init__(self, stream: BinaryIO):
        self.unk = struct.unpack('>?', stream.read(1))[0]
        self.type = struct.unpack('>4s', stream.read(4))[0].decode('ascii')

@dataclass
class DependencyTree(DependencyNode):
    children: List[DependencyNode]

    def __init__(self, game: str, stream: BinaryIO):
        DependencyNode.__init__(self, stream)
        child_count =  struct.unpack('>I', stream.read(4))[0]
        self.children = [read_dependency_node(game, stream) for _ in range(child_count)]

@dataclass
class Resource(DependencyNode):
    id: str

    def __init__(self, _: str, stream: BinaryIO):
        DependencyNode.__init__(self, stream)
        self.id = '{0:016x}'.format(struct.unpack('>Q', stream.read(8))[0])

@dataclass
class ScriptInstance(DependencyNode):
    object_type: str
    children: List[DependencyNode]

    def __init__(self, game: str, stream: BinaryIO):
        DependencyNode.__init__(self, stream)
        obj_type_id = stream.read(4).decode('ascii')
        self.object_type = object_type_lookup[game][obj_type_id]
        child_count = struct.unpack('>I', stream.read(4))[0]
        self.children = [read_dependency_node(game, stream) for _ in range(child_count)]

@dataclass
class ScriptProperty(DependencyNode):
    name: str
    id: str

    def __init__(self, _: str, stream: BinaryIO):
        DependencyNode.__init__(self, stream)
        name_len = struct.unpack('>I', stream.read(4))[0]
        self.name = stream.read(name_len).decode('ascii')
        self.id = '{0:016x}'.format(struct.unpack('>Q', stream.read(8))[0])

@dataclass
class CharacterProperty(DependencyNode):
    name: str
    id: str
    unk_int: int

    def __init__(self, _: str, stream: BinaryIO):
        DependencyNode.__init__(self, stream)
        name_len = struct.unpack('>I', stream.read(4))[0]
        self.name = stream.read(name_len).decode('ascii')
        self.id = '{0:016x}'.format(struct.unpack('>Q', stream.read(8))[0])
        self.unk_int = struct.unpack('>I', stream.read(4))[0]

@dataclass
class SetCharacter(DependencyNode):
    character_index: int
    children: List[DependencyNode]

    def __init__(self, game: str, stream: BinaryIO):
        DependencyNode.__init__(self, stream)
        self.character_index =  struct.unpack('>I', stream.read(4))[0]
        child_count =  struct.unpack('>I', stream.read(4))[0]
        self.children = [read_dependency_node(game, stream) for _ in range(child_count)]

@dataclass
class SetAnimation(DependencyNode):
    character_indices: List[int]
    children: List[DependencyNode]

    def __init__(self, game: str, stream: BinaryIO):
        DependencyNode.__init__(self, stream)
        character_indices_count =  struct.unpack('>I', stream.read(4))[0]
        self.character_indices = [struct.unpack('>I', stream.read(4))[0] for _ in range(character_indices_count)]
        child_count =  struct.unpack('>I', stream.read(4))[0]
        self.children = [read_dependency_node(game, stream) for _ in range(child_count)]

@dataclass
class AnimEvent(DependencyNode):
    id: str
    character_index: int

    def __init__(self, _: str, stream: BinaryIO):
        DependencyNode.__init__(self, stream)
        self.id = '{0:016x}'.format(struct.unpack('>Q', stream.read(8))[0])
        self.character_index =  struct.unpack('>I', stream.read(4))[0]

@dataclass
class Area(DependencyNode):
    children: List[DependencyNode]
    layer_offsets: List[int]

    def __init__(self, game: str, stream: BinaryIO):
        DependencyNode.__init__(self, stream)
        child_count =  struct.unpack('>I', stream.read(4))[0]
        self.children = [read_dependency_node(game, stream) for _ in range(child_count)]
        layer_offsets_count =  struct.unpack('>I', stream.read(4))[0]
        self.layer_offsets = [struct.unpack('>I', stream.read(4))[0] for _ in range(layer_offsets_count)]
@dataclass
class Asset:
    id: str
    type: str
    unk: int
    name: str
    path: str
    dependencies: DependencyNode


    def __init__(self, game: str, stream: BinaryIO):
        self.id = '{0:016x}'.format(struct.unpack('>Q', stream.read(8))[0])
        self.type = struct.unpack('>4s', stream.read(4))[0].decode('ascii')
        self.unk = struct.unpack('>I', stream.read(4))[0]
        name_len = struct.unpack('>I', stream.read(4))[0]
        self.name = stream.read(name_len).decode('utf8')
        path_len = struct.unpack('>I', stream.read(4))[0]
        self.path = stream.read(path_len).decode('utf8')
        self.dependencies = read_dependency_node(game, stream)

def read_dependency_node(game:str, stream: BinaryIO) -> DependencyNode:
    _, node_type = struct.unpack('>?4s', stream.read(5))
    node_type = node_type.decode('ascii')
    stream.seek(-5, 1)
    if node_type == 'TREE':
        return DependencyTree(game, stream)
    elif node_type == 'RSDP':
        return Resource(game, stream)
    elif node_type == 'SCIN':
        return ScriptInstance(game, stream)
    elif node_type == 'SCPR':
        return ScriptProperty(game, stream)
    elif node_type == 'CRPR':
        return CharacterProperty(game, stream)
    elif node_type == 'SCHR':
        return SetCharacter(game, stream)
    elif node_type == 'SANM':
        return SetAnimation(game, stream)
    elif node_type == 'EVNT':
        return AnimEvent(game, stream)
    elif node_type == 'AREA':
        return Area(game, stream)
    else:
        raise Exception("Unrecognized resource node type: " + node_type)

def read_resource_db(db_path):
    db_file = open(db_path, 'rb')
    sqlite_tuples: List[Tuple] = []


    assert db_file.read(4) == b'CACH', "Incorrect magic for resource DB"
    assert struct.unpack('>I', db_file.read(4))[0] == 262144, "Unexpected version number"
    game = db_file.read(4).decode('ascii')
    assert game in ['MP3C'], "Unsupported Game: " + game
    game_str = game_lookup[game]
    asset_count = struct.unpack('>I', db_file.read(4))[0]
    assets = [Asset(game, db_file) for _ in range(asset_count)]
    for asset in assets:
        deps = asset.dependencies
        if isinstance(deps, DependencyTree):
            for child in deps.children:
                if isinstance(child, Resource):
                    print(f'{asset.id} -> {child.id}')
                    sqlite_tuples.append((asset.id, child.id, game_str))
                elif isinstance(child, SetCharacter):
                    for grandchild in child.children:
                        if isinstance(grandchild, Resource):
                            print(f'{asset.id} -> {grandchild.id}')
                            sqlite_tuples.append((asset.id, grandchild.id, game_str))
                        else:
                            raise Exception("Non-Resource child of SCHR: " + grandchild.type)
                elif isinstance(child, SetAnimation):
                    for anim in child.children:
                        if isinstance(anim, Resource):
                            print(f'{asset.id} -> {anim.id}')
                            sqlite_tuples.append((asset.id, anim.id, game_str))
                        elif isinstance(anim, AnimEvent):
                            print(f'{asset.id} -> {anim.id}')
                            sqlite_tuples.append((asset.id, anim.id, game_str))
                        else:
                            raise Exception("Non-Resource child of SANM: " + anim.type)
                elif isinstance(child, AnimEvent):
                    print(f'{asset.id} -> {child.id}')
                    sqlite_tuples.append((asset.id, child.id, game_str))
                elif isinstance(child, ScriptProperty):
                    print(f'{asset.id} -> {child.id}')
                    sqlite_tuples.append((asset.id, child.id, game_str))
                elif isinstance(child, CharacterProperty):
                    print(f'{asset.id} -> {child.id}')
                    sqlite_tuples.append((asset.id, child.id, game_str))
                else:
                    raise Exception("Unexpected node: " + child.type)
        elif isinstance(deps, Area):
            for child in deps.children:
                if isinstance(child, ScriptInstance):
                    for sc_property in child.children:
                        if isinstance(sc_property, ScriptProperty):
                            print(f'{asset.id} -> {sc_property.id}')
                            sqlite_tuples.append((asset.id, sc_property.id, game_str))
                        elif isinstance(sc_property, CharacterProperty):
                            print(f'{asset.id} -> {sc_property.id}')
                            sqlite_tuples.append((asset.id, sc_property.id, game_str))
                        else:
                            print("what: " + sc_property.type)
                elif isinstance(child, Resource):
                    print(f'{asset.id} -> {child.id}')
                    sqlite_tuples.append((asset.id, child.id, game_str))
                else:
                    raise Exception("Unexpected node: " + child.type)
        else:
            raise Exception("Unexpected root-level node: " + deps.type)

    return sqlite_tuples


def add_to_db(insert_data: List[Tuple]):
    asset_db_path = r'F:\Documents\Code\prime-dehashing\md5\md5_resources.db'
    connection = sqlite3.connect(asset_db_path)

    cur = connection.cursor()
    cur.executemany('INSERT INTO asset_references(source, target, game) VALUES(?, ?, ?)', insert_data)
    cur.close()
    connection.commit()

if __name__ == '__main__':
    db_data = read_resource_db(r'E:\Game Files\MP3 Exported\ResourceDatabaseCache.bin')
    print(db_data)
    add_to_db(db_data)