import struct
import hashlib

def retro_md5(text: str):
    return struct.unpack('>Q', hashlib.md5(text.lower().encode()).digest()[-8:])[0]