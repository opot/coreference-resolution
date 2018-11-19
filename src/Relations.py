# encoding: "utf-8"

from enum import Enum

NONE = "none"
attrib = ["fname", "fname", "fname", "lname", "lname", "lname", "patr", "patr", "patr", "gen"]
THRESHOLD = 0.5


class MatchType(Enum):
    FNameStrict = 0
    FNFameRelaxed = 1
    FNameFirstLetter = 2

    LNameStrict = 3
    LNameRelaxed = 4
    LNameFirstLetter = 5

    PatrStrict = 6
    PatrRelaxed = 7
    PatrFirstLetter = 8

    GenderStrict = 9


class StringCmp(Enum):
    NoneField = -2
    Mismatch = -1
    StrictMatch = 0
    RelaxedMatch = 1
    FirstLetterMatch = 2

    @staticmethod
    def compare_values(a, b, gender=False):
        if a == NONE or b == NONE:
            return StringCmp.NoneField

        if gender:
            if a == b:
                return StringCmp.StrictMatch
            else:
                return StringCmp.Mismatch

        if a == b:
            return StringCmp.StrictMatch

        if len(a) > len(b):
            a, b = b, a

        if len(b) == 1 and b[0] == a[0]:
            return StringCmp.FirstLetterMatch

        if a.find(b) != -1 or b.find(a) != -1:
            return StringCmp.RelaxedMatch

        i = 0
        while i < len(a):
            if a[i] != b[i]:
                break
            i += 1

        if len(a) - i <= 3 and len(b) - i <= 3:
            return StringCmp.RelaxedMatch

        return StringCmp.Mismatch


def r(mentions, m, n, match_type):
    if n >= m:
        return 0.0

    int_type = match_type.value
    param = attrib[int_type]
    result = StringCmp.compare_values(mentions[m][param], mentions[n][param],
                                      gender=(int_type == MatchType.GenderStrict))

    if result == StringCmp.Mismatch:
        return -1.0

    if (int_type % 3) == 0:
        return 1.0 if result == StringCmp.StrictMatch else 0.0
    if (int_type % 3) == 1:
        return 1.0 if result == StringCmp.RelaxedMatch else 0.0
    if (int_type % 3) == 2:
        return 1.0 if result == StringCmp.FirstLetterMatch else 0.0

    assert False


coeffs = [2.37865952e+000, 1.49723484e+000, 1.45603707e-136,
          2.40788311e+000, 6.77331372e-001, 3.42756345e-137,
          6.75451402e-001, 2.51671768e-136, 5.53567541e-137,
          2.36343975e+000]


def informative_score(match_type):
    return coeffs[match_type]
