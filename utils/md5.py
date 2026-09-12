import struct
import hashlib

def retro_md5(text: str):
    return struct.unpack('>Q', hashlib.md5(text.encode()).digest()[-8:])[0]

def partial_retro_md5(text: str):
    return hashlib.md5(text.encode())

def finalize_retro_md5(md5):
    return struct.unpack('>Q', md5.digest()[-8:])[0]