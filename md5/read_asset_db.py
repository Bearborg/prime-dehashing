import struct
from typing import List, Dict, Tuple
from dataclasses import dataclass
from typing import BinaryIO
import sqlite3

mp1_obj_types: Dict[int, str] = {
    0x0: "Actor",
    0x2: "Waypoint",
    0x3: "Door",
    0x4: "Trigger",
    0x5: "Timer",
    0x6: "Counter",
    0x7: "Effect",
    0x8: "Platform",
    0x9: "Sound",
    0xA: "Generator",
    0xB: "Dock",
    0xC: "Camera",
    0xD: "CameraWaypoint",
    0xE: "NewIntroBoss",
    0xF: "SpawnPoint",
    0x10: "CameraHint",
    0x11: "Pickup",
    0x13: "MemoryRelay",
    0x14: "RandomRelay",
    0x15: "Relay",
    0x16: "Beetle",
    0x17: "HUDMemo",
    0x18: "CameraFilterKeyframe",
    0x19: "CameraBlurKeyframe",
    0x1A: "DamageableTrigger",
    0x1B: "Debris",
    0x1C: "CameraShaker",
    0x1D: "ActorKeyframe",
    0x20: "Water",
    0x21: "WarWasp",
    0x24: "SpacePirate",
    0x25: "FlyingPirate",
    0x26: "ElitePirate",
    0x27: "MetroidBeta",
    0x28: "ChozoGhost",
    0x2A: "CoverPoint",
    0x2C: "SpiderBallWaypoint",
    0x2D: "BloodFlower",
    0x2E: "FlickerBat",
    0x2F: "PathCamera",
    0x30: "GrapplePoint",
    0x31: "PuddleSpore",
    0x32: "DebugCameraWaypoint",
    0x33: "SpiderBallAttractionSurface",
    0x34: "PuddleToadGamma",
    0x35: "DistanceFog",
    0x36: "FireFlea",
    0x37: "MetareeAlpha",
    0x38: "DockAreaChange",
    0x39: "ActorRotate",
    0x3A: "SpecialFunction",
    0x3B: "SpankWeed",
    0x3D: "Parasite",
    0x3E: "PlayerHint",
    0x3F: "Ripper",
    0x40: "PickupGenerator",
    0x41: "AIKeyframe",
    0x42: "PointOfInterest",
    0x43: "Drone",
    0x44: "MetroidAlpha",
    0x45: "DebrisExtended",
    0x46: "Steam",
    0x47: "Ripple",
    0x48: "BallTrigger",
    0x49: "TargetingPoint",
    0x4A: "ElectroMagneticPulse",
    0x4B: "IceSheegoth",
    0x4C: "PlayerActor",
    0x4D: "Flaahgra",
    0x4E: "AreaAttributes",
    0x4F: "FishCloud",
    0x50: "FishCloudModifier",
    0x51: "VisorFlare",
    0x52: "WorldTeleporter",
    0x53: "VisorGoo",
    0x54: "JellyZap",
    0x55: "ControllerAction",
    0x56: "Switch",
    0x57: "PlayerStateChange",
    0x58: "Thardus",
    0x5A: "WallCrawlerSwarm",
    0x5B: "AIJumpPoint",
    0x5C: "FlaahgraTentacle",
    0x5D: "RoomAcoustics",
    0x5E: "ColorModulate",
    0x5F: "ThardusRockProjectile",
    0x60: "Midi",
    0x61: "StreamedAudio",
    0x62: "WorldTeleporter",
    0x63: "Repulsor",
    0x64: "GunTurret",
    0x65: "FogVolume",
    0x66: "Babygoth",
    0x67: "Eyeball",
    0x68: "RadialDamage",
    0x69: "CameraPitchVolume",
    0x6A: "EnvFxDensityController",
    0x6B: "Magdolite",
    0x6C: "TeamAIMgr",
    0x6D: "SnakeWeedSwarm",
    0x6E: "ActorContraption",
    0x6F: "Oculus",
    0x70: "Geemer",
    0x71: "SpindleCamera",
    0x72: "AtomicAlpha",
    0x73: "CameraHintTrigger",
    0x74: "RumbleEffect",
    0x75: "AmbientAI",
    0x77: "AtomicBeta",
    0x78: "IceZoomer",
    0x79: "Puffer",
    0x7A: "Tryclops",
    0x7B: "Ridley",
    0x7C: "Seedling",
    0x7D: "ThermalHeatFader",
    0x7F: "Burrower",
    0x81: "ScriptBeam",
    0x82: "WorldLightFader",
    0x83: "MetroidPrimeStage2",
    0x84: "MetroidPrimeStage1",
    0x85: "MazeNode",
    0x86: "OmegaPirate",
    0x87: "PhazonPool",
    0x88: "PhazonHealingNodule",
    0x89: "NewCameraShaker",
    0x8A: "ShadowProjector",
    0x8B: "EnergyBall"
}
mp2_obj_types: Dict[str, str] = {
    "ACKF": "ActorKeyframe",
    "ACNT": "AdvancedCounter",
    "ACTR": "Actor",
    "ADMG": "AreaDamage",
    "AIHT": "AIHint",
    "AIKF": "AIKeyframe",
    "AIMT": "AIMannedTurret",
    "AIWP": "AIWaypoint",
    "AJMP": "AIJumpPoint",
    "AMIA": "AmbientAI",
    "AROT": "ActorRotate",
    "ATMA": "AtomicAlpha",
    "ATMB": "AtomicBeta",
    "BALS": "SpiderBallAttractionSurface",
    "BALT": "BallTrigger",
    "BALW": "SpiderBallWaypoint",
    "BLOG": "Blogg",
    "BLUR": "CameraBlurKeyframe",
    "BRZG": "Brizgee",
    "BSWM": "BacteriaSwarm",
    "CAMH": "CameraHint",
    "CAMP": "CameraPitch",
    "CAMR": "Camera",
    "CAMS": "CameraShaker",
    "CAMW": "CameraWaypoint",
    "CANB": "CannonBall",
    "CHOG": "ChozoGhost",
    "CLRM": "ColorModulate",
    "CMDO": "CommandoPirate",
    "CNTA": "ControllerAction",
    "CNTR": "Counter",
    "COIN": "Coin",
    "COVR": "CoverPoint",
    "CRLT": "Crystallite",
    "CRLY": "ConditionalRelay",
    "CTLH": "ControlHint",
    "DBAR": "DestructibleBarrier",
    "DBR1": "Debris",
    "DBR2": "DebrisExtended",
    "DFOG": "DistanceFog",
    "DGHD": "DigitalGuardianHead",
    "DGRD": "DigitalGuardian",
    "DKTR": "DarkTrooper",
    "DLHT": "DynamicLight",
    "DMGA": "DamageActor",
    "DOCK": "Dock",
    "DOOR": "Door",
    "DRKC": "DarkCommando",
    "DRKS": "DarkSamus",
    "DSBS": "DarkSamusBattleStage",
    "DTRG": "DamageableTrigger",
    "DTRO": "DamageableTriggerOrientated",
    "EFCT": "Effect",
    "EM2T": "EmperorIngStage2Tentacle",
    "EMPU": "EMPulse",
    "EMS1": "EmperorIngStage1",
    "EMS3": "EmperorIngStage3",
    "EPRT": "ElitePirate",
    "EYEB": "EyeBall",
    "FGTO": "ForgottenObject",
    "FILT": "CameraFilterKeyframe",
    "FISH": "FishCloud",
    "FLAR": "VisorFlare",
    "FNWK": "FrontEndDataNetwork",
    "FOGO": "FogOverlay",
    "FOGV": "FogVolume",
    "FPRT": "FlyingPirate",
    "FSHM": "FishCloudModifier",
    "FSWM": "FlyerSwarm",
    "FXDC": "EnvFxDensityController",
    "GBUG": "Glowbug",
    "GENR": "Generator",
    "GMNU": "GuiMenu",
    "GNTB": "GunTurretBase",
    "GNTT": "GunTurretTop",
    "GPJN": "GuiPlayerJoinManager",
    "GRAP": "GrapplePoint",
    "GRCH": "Grenchler",
    "GSCR": "GuiScreen",
    "GSLD": "GuiSlider",
    "GWIG": "GuiWidget",
    "HHNT": "HUDHint",
    "HINT": "PlayerHint",
    "IBBG": "IngBoostBallGuardian",
    "IBSM": "IngBlobSwarm",
    "INGS": "Ing",
    "IPUD": "IngPuddle",
    "ISBG": "IngSpiderballGuardian",
    "ISJG": "IngSpaceJumpGuardian",
    "ISSW": "IngSnatchingSwarm",
    "KRAL": "Kralee",
    "KROC": "Krocuss",
    "LUMI": "Lumite",
    "MEMO": "HUDMemo",
    "MIDI": "Midi",
    "MING": "MediumIng",
    "MNNG": "MinorIng",
    "MOVI": "StreamedMovie",
    "MREE": "Metaree",
    "MRLY": "MemoryRelay",
    "MSWM": "MetareeSwarm",
    "MTDA": "MetroidAlpha",
    "MYSF": "MysteryFlyer",
    "OCTS": "OctapedeSegment",
    "PARA": "Parasite",
    "PCAM": "PathCamera",
    "PCKP": "Pickup",
    "PILB": "PillBug",
    "PIRT": "SpacePirate",
    "PKGN": "PickupGenerator",
    "PLAC": "PlayerActor",
    "PLAT": "Platform",
    "PLCT": "PlayerController",
    "PLRT": "PlayerTurret",
    "PMCT": "PathMeshCtrl",
    "POIN": "PointOfInterest",
    "PRTT": "PortalTransition",
    "PSCH": "PlayerStateChange",
    "PSSM": "PlantScarabSwarm",
    "PUFR": "Puffer",
    "RADD": "RadialDamage",
    "RBPZ": "RubiksPuzzle",
    "REAA": "AreaAttributes",
    "REPL": "Repulsor",
    "REZB": "Rezbit",
    "RIPL": "Ripple",
    "RIPR": "Ripper",
    "RMAC": "RoomAcoustics",
    "RPTL": "RiftPortal",
    "RRLY": "RandomRelay",
    "RSFA": "RsfAudio",
    "RUMB": "RumbleEffect",
    "SAFE": "SafeZone",
    "SBS1": "SwampBossStage1",
    "SBS2": "SwampBossStage2",
    "SCIN": "ScanTreeInventory",
    "SCMN": "ScanTreeMenu",
    "SCND": "ScanTreeCategory",
    "SCSL": "ScanTreeSlider",
    "SCSN": "ScanTreeScan",
    "SFZC": "SafeZoneCrystal",
    "SHDW": "ShadowProjector",
    "SHRD": "Shredder",
    "SHRK": "Shrieker",
    "SILH": "Silhouette",
    "SKRP": "SkyRipple",
    "SLCT": "ScriptLayerController",
    "SNAK": "SnakeWeedSwarm",
    "SNDB": "SandBoss",
    "SNDM": "SoundModifier",
    "SNFO": "ScannableObjectInfo",
    "SOND": "Sound",
    "SPBB": "SporbBase",
    "SPBN": "SporbNeedle",
    "SPBP": "SporbProjectile",
    "SPBT": "SporbTop",
    "SPFN": "SpecialFunction",
    "SPIN": "Spinner",
    "SPLL": "SplitterMainChassis",
    "SPLU": "SplitterCommandModule",
    "SPND": "SpindleCamera",
    "SPNK": "SpankWeed",
    "SPOR": "PuddleSpore",
    "SPTR": "Splinter",
    "SPWN": "SpawnPoint",
    "SQTR": "SequenceTimer",
    "SRLY": "Relay",
    "STAU": "StreamedAudio",
    "STEM": "Steam",
    "STOD": "StoneToad",
    "SUBT": "Subtitle",
    "SURC": "SurfaceCamera",
    "SWTC": "Switch",
    "TEL1": "WorldTeleporter",
    "TGPT": "TargetingPoint",
    "TIMR": "Timer",
    "TKEY": "TimeKeyframe",
    "TMAI": "TeamAI",
    "TRGE": "TriggerEllipsoid",
    "TRGO": "TriggerOrientated",
    "TRGR": "Trigger",
    "TRYC": "Tryclops",
    "TWAM": "TweakAutoMapper",
    "TWBL": "TweakBall",
    "TWC2": "TweakPlayerControls",
    "TWCB": "TweakCameraBob",
    "TWGC": "TweakGuiColors",
    "TWGM": "TweakGame",
    "TWGU": "TweakGui",
    "TWP2": "TweakPlayer",
    "TWPA": "TweakParticle",
    "TWPC": "TweakPlayerControls",
    "TWPG": "TweakPlayerGun",
    "TWPL": "TweakPlayer",
    "TWPM": "TweakPlayerGun",
    "TWPR": "TweakPlayerRes",
    "TWSS": "TweakSlideShow",
    "TWTG": "TweakTargeting",
    "TXPN": "TextPane",
    "VGOO": "VisorGoo",
    "WATR": "Water",
    "WAYP": "Waypoint",
    "WISP": "WispTentacle",
    "WLIT": "WorldLightFader",
    "WLWK": "WallWalker",
    "WORM": "Sandworm"
}
object_type_lookup: Dict[str, Dict[object, str]] = {
    'MPRM': mp1_obj_types,
    'MP2E': mp2_obj_types
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
        self.id = '{0:016x}'.format(struct.unpack('>Q', stream.read(4))[0])

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
        self.id = '{0:016x}'.format(struct.unpack('>Q', stream.read(4))[0])

@dataclass
class CharacterProperty(DependencyNode):
    name: str
    id: str
    unk_int: int

    def __init__(self, _: str, stream: BinaryIO):
        DependencyNode.__init__(self, stream)
        name_len = struct.unpack('>I', stream.read(4))[0]
        self.name = stream.read(name_len).decode('ascii')
        self.id = '{0:016x}'.format(struct.unpack('>Q', stream.read(4))[0])
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
        self.id = '{0:016x}'.format(struct.unpack('>Q', stream.read(4))[0])
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
        self.id = '{0:016x}'.format(struct.unpack('>Q', stream.read(4))[0])
        self.type = struct.unpack('>4s', stream.read(4))[0].decode('ascii')
        self.unk = struct.unpack('>I', stream.read(4))[0]
        name_len = struct.unpack('>I', stream.read(4))[0]
        self.name = stream.read(name_len).decode('ascii')
        path_len = struct.unpack('>I', stream.read(4))[0]
        self.path = stream.read(path_len).decode('ascii')
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
    assert game in ['MPRM', 'MP2E'], "Unsupported Game: " + game
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
    print(read_resource_db(r'E:\Game Files\MP3 Exported\ResourceDatabaseCache.bin'))