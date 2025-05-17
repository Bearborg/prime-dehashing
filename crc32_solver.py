import z3

# By alkalinesec - https://gist.github.com/aemmitt-ns/6b6d4098c48ebba0f26894b77c8d7e10
# Slightly tweaked by chz - https://github.com/MrCheeze/dread-tools/blob/master/crc64_reversing/decrc64.py
# Slightly tweaked again by Bearborg
# Prerequisite: z3-solver

def solve(goalchecksum, prefixstr, suffixstr, maxunklen=13, minunklen=1):
    """
    Uses constraint solving techniques to perform per-character brute-forcing. Allowed characters can be changed by
    commenting/un-commenting the sections inside the z3.Or collection
    """
    for unklen in range(minunklen, maxunklen + 1):

        print("Solving %s for string %s{?x%d}%s" % (hex(goalchecksum), prefixstr, unklen, suffixstr))

        s = z3.Solver()
        s.push()

        poly = z3.BitVecVal(0xEDB88320, 32)
        goal = z3.BitVecVal(goalchecksum, 32)
        ZERO = z3.BitVecVal(0, 32)
        ONE = z3.BitVecVal(1, 32)

        unknown = z3.BitVec("fn", unklen * 8)
        full = unknown
        prefix_num = sum(ord(c) << 8 * i for i, c in enumerate(prefixstr))
        if len(prefixstr) > 0:
            prefix = z3.BitVecVal(prefix_num, len(prefixstr) * 8)
            full = z3.Concat(full, prefix)
        suffix_num = sum(ord(c) << 8 * i for i, c in enumerate(suffixstr))
        if len(suffixstr) > 0:
            suffix = z3.BitVecVal(suffix_num, len(suffixstr) * 8)
            full = z3.Concat(suffix, full)

        crc = ~ZERO
        for i in range(full.size() // 8):
            c = z3.Extract(8 * (i + 1) - 1, 8 * i, full)

            if len(prefixstr) <= i < len(prefixstr) + unklen:
                s.add(z3.simplify(z3.Or(
                    z3.And(
                        c >= z3.BitVecVal(ord('a'), 8),
                        c <= z3.BitVecVal(ord('z'), 8),
                    ),
                    # z3.And(
                    #     c >= z3.BitVecVal(ord('A'), 8),
                    #     c <= z3.BitVecVal(ord('Z'), 8),
                    #     unklen <= 8,
                    # ),
                    z3.And(
                        c == z3.BitVecVal(ord('_'), 8),
                        unklen <= 14,
                    ),
                    z3.And(
                        c >= z3.BitVecVal(ord('0'), 8),
                        c <= z3.BitVecVal(ord('9'), 8),
                        unklen <= 14,
                    ),
                    z3.And(
                        c == z3.BitVecVal(ord('-'), 8),
                        unklen <= 8,
                    ),
                    z3.And(
                        c == z3.BitVecVal(ord(' '), 8),
                        unklen <= 8,
                    ),
                    # z3.And(
                    #     c == z3.BitVecVal(ord('('), 8),
                    #     unklen <= 8,
                    # ),
                    # z3.And(
                    #     c == z3.BitVecVal(ord(')'), 8),
                    #     unklen <= 8,
                    # ),
                    # z3.And(
                    #     c == z3.BitVecVal(ord('!'), 8),
                    #     unklen <= 14,
                    # ),
                    # z3.And(
                    #     c == z3.BitVecVal(ord('.'), 8),
                    #     unklen <= 14,
                    # ),
                    # z3.And(
                    #     c == z3.BitVecVal(ord('/'), 8),
                    #     unklen <= 8,
                    # ),
                )))

            crc = z3.simplify(crc ^ z3.ZeroExt(24, c))
            for k in range(8):
                crc = z3.If(crc & ONE != ZERO,
                            z3.LShR(crc, ONE) ^ poly,
                            z3.LShR(crc, ONE))

        s.add(crc == goal)

        while s.check() == z3.sat:
            m = s.model()
            r = m.eval(unknown, True)
            s.add(unknown != r)

            guess = ("".join(chr((r.as_long() >> 8 * i) & 0xff) for i in range(unklen)))
            print(prefixstr + guess + suffixstr)

if __name__ == '__main__':
    solve(0x77da870f, "$/effects/textures/".lower(), ".txtr".lower(), 8)
