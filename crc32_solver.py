import re
import z3
import utils.crc32


# By alkalinesec - https://gist.github.com/aemmitt-ns/6b6d4098c48ebba0f26894b77c8d7e10
# Slightly tweaked by chz - https://github.com/MrCheeze/dread-tools/blob/master/crc64_reversing/decrc64.py
# Slightly tweaked again by Bearborg
# Prerequisite: z3-solver

def solve(goalchecksum, prefixstr, suffixstr, maxunklen=13, minunklen=1, timeout: int = None):
    """
    Uses constraint solving techniques to perform per-character brute-forcing. Allowed characters can be changed by
    commenting/un-commenting the sections inside the z3.Or collection
    """
    for unklen in range(minunklen, maxunklen + 1):

        print("Solving %s for string %s{?x%d}%s" % (hex(goalchecksum), prefixstr, unklen, suffixstr))
        rewound_goal = utils.crc32.remove_suffix(goalchecksum, suffixstr)
        start = utils.crc32.crc32(prefixstr)

        s = z3.Solver()
        if timeout is not None:
            s.set("timeout", timeout * 1000)
        s.push()

        poly = z3.BitVecVal(0xEDB88320, 32)
        goal = z3.BitVecVal(rewound_goal, 32)
        ZERO = z3.BitVecVal(0, 32)
        ONE = z3.BitVecVal(1, 32)

        unknown = z3.BitVec("fn", unklen * 8)

        crc = z3.BitVecVal(start, 32)
        for i in range(unklen):
            c = z3.Extract(8 * (i + 1) - 1, 8 * i, unknown)
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
            #if re.match(r'[a-z_]+\d*_?$', guess):
            print(prefixstr + guess + suffixstr)

def solve_pair(goalchecksum1, prefixstr1, suffixstr1,
               goalchecksum2, prefixstr2, suffixstr2,
               maxunklen=13, minunklen=1, timeout: int = None, ctx: z3.Context = None):
    """
    Similar to 'solve', but takes in two hashes that are known/suspected to have identical unknown portions. Comparing
    two hashes this way can reduce false positives, since the only values that will match both hashes are values of
    the same length as the original plaintext.
    """
    for unklen in range(minunklen, maxunklen + 1):

        print(f"Solving {hex(goalchecksum1)} for string {prefixstr1}{{?x{unklen}}}{suffixstr1}, {hex(goalchecksum2)} for string {prefixstr2}{{?x{unklen}}}{suffixstr2}")

        s = z3.Solver(ctx=ctx)
        if timeout is not None:
            s.set("timeout", timeout * 1000)
        s.push()

        goalchecksum1_rewound = utils.crc32.remove_suffix(goalchecksum1, suffixstr1)
        start1 = utils.crc32.crc32(prefixstr1)

        goalchecksum2_rewound = utils.crc32.remove_suffix(goalchecksum2, suffixstr2)
        start2 = utils.crc32.crc32(prefixstr2)

        poly = z3.BitVecVal(0xEDB88320, 32, ctx=ctx)
        goal1 = z3.BitVecVal(goalchecksum1_rewound, 32, ctx=ctx)
        goal2 = z3.BitVecVal(goalchecksum2_rewound, 32, ctx=ctx)
        ZERO = z3.BitVecVal(0, 32, ctx=ctx)
        ONE = z3.BitVecVal(1, 32, ctx=ctx)

        unknown = z3.BitVec("fn", unklen * 8, ctx=ctx)

        crc1 = z3.BitVecVal(start1, 32)
        crc2 = z3.BitVecVal(start2, 32)
        for i in range(unklen):
            c = z3.Extract(8 * (i + 1) - 1, 8 * i, unknown)
            s.add(z3.simplify(z3.Or(
                # z3.And(
                #     c >= z3.BitVecVal(ord(' '), 8, ctx=ctx),
                #     c <= z3.BitVecVal(ord('@'), 8, ctx=ctx),
                # ),
                # z3.And(
                #     c >= z3.BitVecVal(ord('['), 8, ctx=ctx),
                #     c <= z3.BitVecVal(ord('~'), 8, ctx=ctx),
                # ),
                z3.And(
                    c >= z3.BitVecVal(ord('a'), 8, ctx=ctx),
                    c <= z3.BitVecVal(ord('z'), 8, ctx=ctx),
                ),
                # z3.And(
                #     c >= z3.BitVecVal(ord('A'), 8, ctx=ctx),
                #     c <= z3.BitVecVal(ord('Z'), 8, ctx=ctx),
                #     unklen <= 8,
                # ),
                z3.And(
                    c == z3.BitVecVal(ord('_'), 8, ctx=ctx),
                    unklen <= 14,
                ),
                z3.And(
                    c >= z3.BitVecVal(ord('0'), 8, ctx=ctx),
                    c <= z3.BitVecVal(ord('9'), 8, ctx=ctx),
                    unklen <= 14,
                ),
                z3.And(
                    c == z3.BitVecVal(ord('-'), 8, ctx=ctx),
                    unklen <= 8,
                ),
                z3.And(
                    c == z3.BitVecVal(ord(' '), 8, ctx=ctx),
                    unklen <= 8,
                ),
                # z3.And(
                #     c == z3.BitVecVal(ord('('), 8, ctx=ctx),
                #     unklen <= 8,
                # ),
                # z3.And(
                #     c == z3.BitVecVal(ord(')'), 8, ctx=ctx),
                #     unklen <= 8,
                # ),
                # z3.And(
                #     c == z3.BitVecVal(ord('!'), 8, ctx=ctx),
                #     unklen <= 14,
                # ),
                # z3.And(
                #     c == z3.BitVecVal(ord('.'), 8, ctx=ctx),
                #     unklen <= 14,
                # ),
                # c == z3.BitVecVal(ord('/'), 8, ctx=ctx)
            )))

            crc1 = z3.simplify(crc1 ^ z3.ZeroExt(24, c))
            crc2 = z3.simplify(crc2 ^ z3.ZeroExt(24, c))
            for k in range(8):
                crc1 = z3.If(crc1 & ONE != ZERO,
                            z3.LShR(crc1, ONE) ^ poly,
                            z3.LShR(crc1, ONE))
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
