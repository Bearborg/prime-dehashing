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
                    # z3.And(
                    #     c >= z3.BitVecVal(ord(' '), 8),
                    #     c <= z3.BitVecVal(ord('@'), 8),
                    # ),
                    # z3.And(
                    #     c >= z3.BitVecVal(ord('['), 8),
                    #     c <= z3.BitVecVal(ord('~'), 8),
                    # ),
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

def solve_pair(goalchecksum1, prefixstr1, suffixstr1, goalchecksum2, prefixstr2, suffixstr2, maxunklen=13, minunklen=1):
    """
    Similar to 'solve', but takes in two hashes that are known/suspected to have identical unknown portions. Comparing
    two hashes this way can reduce false positives, since the only values that will match both hashes are values of
    the same length as the original plaintext.
    """
    for unklen in range(minunklen, maxunklen + 1):

        print("Solving %s for string %s{?x%d}%s" % (hex(goalchecksum1), prefixstr1, unklen, suffixstr1))

        s = z3.Solver()
        s.push()

        poly = z3.BitVecVal(0xEDB88320, 32)
        goal1 = z3.BitVecVal(goalchecksum1, 32)
        goal2 = z3.BitVecVal(goalchecksum2, 32)
        ZERO = z3.BitVecVal(0, 32)
        ONE = z3.BitVecVal(1, 32)

        unknown = z3.BitVec("fn", unklen * 8)
        full1 = unknown
        full2 = unknown
        prefix_num1 = sum(ord(c) << 8 * i for i, c in enumerate(prefixstr1))
        if len(prefixstr1) > 0:
            prefix1 = z3.BitVecVal(prefix_num1, len(prefixstr1) * 8)
            full1 = z3.Concat(full1, prefix1)
        suffix_num1 = sum(ord(c) << 8 * i for i, c in enumerate(suffixstr1))
        if len(suffixstr1) > 0:
            suffix1 = z3.BitVecVal(suffix_num1, len(suffixstr1) * 8)
            full1 = z3.Concat(suffix1, full1)
            
        prefix_num2 = sum(ord(c) << 8 * i for i, c in enumerate(prefixstr2))
        if len(prefixstr2) > 0:
            prefix2 = z3.BitVecVal(prefix_num2, len(prefixstr2) * 8)
            full2 = z3.Concat(full2, prefix2)
        suffix_num2 = sum(ord(c) << 8 * i for i, c in enumerate(suffixstr2))
        if len(suffixstr2) > 0:
            suffix2 = z3.BitVecVal(suffix_num2, len(suffixstr2) * 8)
            full2 = z3.Concat(suffix2, full2)

        crc1 = ~ZERO
        crc2 = ~ZERO
        for i in range(full1.size() // 8):
            c = z3.Extract(8 * (i + 1) - 1, 8 * i, full1)

            if len(prefixstr1) <= i < len(prefixstr1) + unklen:
                s.add(z3.simplify(z3.Or(
                    # z3.And(
                    #     c >= z3.BitVecVal(ord(' '), 8),
                    #     c <= z3.BitVecVal(ord('@'), 8),
                    # ),
                    # z3.And(
                    #     c >= z3.BitVecVal(ord('['), 8),
                    #     c <= z3.BitVecVal(ord('~'), 8),
                    # ),
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
                    z3.And(
                        c == z3.BitVecVal(ord('/'), 8),
                        unklen <= 8,
                    ),
                )))

            crc1 = z3.simplify(crc1 ^ z3.ZeroExt(24, c))
            for k in range(8):
                crc1 = z3.If(crc1 & ONE != ZERO,
                            z3.LShR(crc1, ONE) ^ poly,
                            z3.LShR(crc1, ONE))
        for i in range(full2.size() // 8):
            c2 = z3.Extract(8 * (i + 1) - 1, 8 * i, full2)

            if len(prefixstr2) <= i < len(prefixstr2) + unklen:
                remapped_i = len(prefixstr1) - len(prefixstr2) + i
                c1 = z3.Extract(8 * (remapped_i + 1) - 1, 8 * remapped_i, full1)
                s.add(z3.simplify(c1 == c2))

            crc2 = z3.simplify(crc2 ^ z3.ZeroExt(24, c2))
            for k in range(8):
                crc2 = z3.If(crc2 & ONE != ZERO,
                            z3.LShR(crc2, ONE) ^ poly,
                            z3.LShR(crc2, ONE))

        s.add(crc1 == goal1)
        s.add(crc2 == goal2)

        while s.check() == z3.sat:
            m = s.model()
            r = m.eval(unknown, True)
            s.add(unknown != r)

            guess = ("".join(chr((r.as_long() >> 8 * i) & 0xff) for i in range(unklen)))
            print(prefixstr1 + guess + suffixstr1)

if __name__ == '__main__':
    solve(0x77da870f, "$/effects/textures/".lower(), ".txtr".lower(), 8)
