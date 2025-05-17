from binascii import crc32 as py_crc32

def crc32(string: str, checksum=0xFFFFFFFF):
    """
    Wrapper about Python's built-in CRC32 function that cancels out some extra XORs to make it match Retro's algorithm.
    :param string: Input string.
    :param checksum: Starting checksum.
    :return: Hash, as a 32-bit unsigned int.
    """
    return py_crc32(string.encode(), checksum ^ 0xFFFFFFFF) ^ 0xFFFFFFFF