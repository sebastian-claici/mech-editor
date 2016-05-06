import difflib

thresh_ratio = 0.6

ellesmere = open('manuscripts/Ellesmere.txt').readlines()[:50]
hengwrt = open('manuscripts/Hengwrt.txt').readlines()[:50]


def junk_chars(s):
    return s in " \t\n"


def match_ms(m1, m2):
    i, j = 0, 0
    while i < len(ellesmere) and j < len(hengwrt):
        s = difflib.SequenceMatcher(junk_chars, m1[i], m2[j])
        print s.ratio()
        print m1[i], m2[j]
        if s.ratio() > thresh_ratio:
            i += 1, j += 1
        else:
            ii, jj = find_next_match(m1, m2, i, j)
            if ii, jj == -1, -1:
                i += 1, j += 1
            i, j = ii, jj


def find_next_match(m1, m2, i, j):
    # assume next matching line will be in a 100 line window
    window = 100
    best_ratio = 0
    best_match = (-1, -1)
    
    for ii in range(i, i + 100):
        s = difflib.SequenceMatcher(junk_chars, m1[ii], m2[j])
        if s.ratio() > best_ratio:
            best_ratio = s.ratio()
            best_match = (ii, j)
            
    for jj in range(j, j + 100):
        s = difflib.SequenceMatcher(junk_chars, m1[i], m2[jj])
        if s.ratio() > best_ratio:
            best_ratio = s.ratio()
            best_match = (i, jj)
            
    return best_match

match_ms(ellesmere, hengwrt)
