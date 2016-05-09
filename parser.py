from lxml import html
import re
import requests
import os.path
import string


manuscripts = {
    'Hengwrt': 'http://quod.lib.umich.edu/c/cme/AGZ8233.0001.001?rgn=main;view=fulltext',
    'Ellesmere': 'http://quod.lib.umich.edu/c/cme/AGZ8232.0001.001?rgn=main;view=fulltext',
    'Cambridge-Gg': 'http://quod.lib.umich.edu/c/cme/AGZ8234.0001.001?rgn=main;view=fulltext',
    'Corpus': 'http://quod.lib.umich.edu/c/cme/AGZ8235.0001.001?rgn=main;view=fulltext',
    'Lansdowne': 'http://quod.lib.umich.edu/c/cme/AGZ8236.0001.001?rgn=main;view=fulltext',
    'Harleian': 'http://quod.lib.umich.edu/c/cme/AGZ8246.0001.001?rgn=main;view=fulltext',
    'Petworth': 'http://quod.lib.umich.edu/c/cme/ASH2689.0001.001?rgn=main;view=fulltext',
    'Cambridge-Dd': 'http://quod.lib.umich.edu/c/cme/ASH3725.0001.001?rgn=main;view=fulltext',
}

poetic_texts = {
    'Robinson': 'http://quod.lib.umich.edu/c/cme/CT?rgn=main;view=fulltext',
    'Troilus': 'http://quod.lib.umich.edu/c/cme/Troilus?rgn=main;view=fulltext',
    'Pearl': 'http://quod.lib.umich.edu/c/cme/Pearl?rgn=main;view=fulltext',
    'Ipomydon': 'http://quod.lib.umich.edu/c/cme/Ipomydon?rgn=main;view=fulltext',
    'Morte': 'http://quod.lib.umich.edu/c/cme/AllitMA?rgn=main;view=fulltext',
    'Piers': 'http://quod.lib.umich.edu/c/cme/PPlLan?rgn=main;view=fulltext',
    'Short Charter': 'http://quod.lib.umich.edu/c/cme/AFW1075.0001.001?rgn=main;view=fulltext',
    'Guy of Warwick': 'http://quod.lib.umich.edu/c/cme/ANZ4364.0001.001?rgn=main;view=fulltext',
    'Havelok the Dane': 'http://quod.lib.umich.edu/c/cme/AHA2626.0001.001?rgn=main;view=fulltext',
    'King Horn': 'http://quod.lib.umich.edu/c/cme/ACN1637.0001.001?rgn=main;view=fulltext',
    'Le Morte Arthur': 'http://quod.lib.umich.edu/c/cme/AHA2659.0001.001?rgn=main;view=fulltext',
    'Owl and Nightingale': 'http://quod.lib.umich.edu/c/cme/OwlJ?rgn=main;view=fulltext',
    'Towneley': 'http://quod.lib.umich.edu/c/cme/Towneley?rgn=main;view=fulltext',
    'York': 'http://quod.lib.umich.edu/c/cme/York?rgn=main;view=fulltext',
    'Everyman': 'http://quod.lib.umich.edu/c/cme/Everyman?rgn=main;view=fulltext',
    'Confessio Amantis': 'http://quod.lib.umich.edu/c/cme/Confessio?rgn=main;view=fulltext',
    'Hoccleve Poems': 'http://quod.lib.umich.edu/c/cme/ADQ4048.0001.001?rgn=main;view=fulltext',
    'Reson and sensuallyte': 'http://quod.lib.umich.edu/c/cme/ANY9948.0001.001?rgn=main;view=fulltext',
    'Life of man': 'http://quod.lib.umich.edu/c/cme/AJT8111.0001.001?rgn=main;view=fulltext',
}

prose_texts = {
    'Life of soul': 'http://quod.lib.umich.edu/c/cme/lifesoul?rgn=main;view=fulltext',
    'Chancery': 'http://quod.lib.umich.edu/c/cme/ChancEng?rgn=main;view=fulltext',
    'Mandeville': 'http://quod.lib.umich.edu/c/cme/acd9576?rgn=main;view=fulltext',
    'Chronicle': 'http://quod.lib.umich.edu/c/cme/ACV5981.0001.001?rgn=main;view=fulltext',
    'Romance of Merlin': 'http://quod.lib.umich.edu/c/cme/Merlin?rgn=main;view=fulltext',
    'Governance of England': 'http://quod.lib.umich.edu/c/cme/AEW3422.0001.001?rgn=main;view=fulltext',
    'Morte Darthur': 'http://quod.lib.umich.edu/c/cme/MaloryWks2?rgn=main;view=fulltext',
}


char_replace = {
    u'\u00c0': 'A', u'\u00c1': 'A', u'\u00c2': 'A', u'\u00c3': 'A', u'\u00c4': 'A', u'\u00c5': 'A',
    u'\u00c8': 'E', u'\u00c9': 'E', u'\u00ca': 'E', u'\u00cb': 'E',
    u'\u00cc': 'I', u'\u00cd': 'I', u'\u00ce': 'I', u'\u00cf': 'I',
    u'\u00d2': 'O', u'\u00d3': 'O', u'\u00d4': 'O', u'\u00d5': 'O', u'\u00d6': 'O',
    u'\u00d9': 'U', u'\u00da': 'U', u'\u00db': 'U', u'\u00dc': 'U',
    u'\u00e0': 'a', u'\u00e1': 'a', u'\u00e2': 'a', u'\u00e3': 'a', u'\u00e4': 'a', u'\u00e5': 'a',
    u'\u00e8': 'e', u'\u00e9': 'e', u'\u00ea': 'e', u'\u00eb': 'e',
    u'\u00ec': 'i', u'\u00ed': 'i', u'\u00ee': 'i', u'\u00ef': 'i',
    u'\u00f2': 'o', u'\u00f3': 'o', u'\u00f4': 'o', u'\u00f5': 'o', u'\u00f6': 'o',
    u'\u00f9': 'u', u'\u00fa': 'u', u'\u00fb': 'u', u'\u00fc': 'u',
    u'\u2010': ' ', u'\u2011': ' ', u'\u2012': ' ', u'\u2013': ' ', u'\u2014': ' ', u'\u2015': ' ',
    u'\u2234': ' ', u'\u2235': ' ', u'\u00b6': ' ', u'\u00b7': ' ', u'\u00b8': ' ',
    '&': 'and', '\n': ' '
    }

for c in string.punctuation:
    char_replace[c] = ' '


def read_poetry(dir, texts):
    for m, l in texts.items():
        if not os.path.isfile(dir + m + '.txt'):
            print 'parsing ' + m
            page = requests.get(l)
            tree = html.fromstring(page.content)
            lines = tree.xpath('//div[@class="line"]')
            with open(dir + m + '.txt', 'wb') as f:
                for line in lines:
                    f.write(parse_line(line, parse_text_poetry).encode('utf-8'))
                    f.write('\n')
            print m + ' parsed!'


def read_prose(dir, texts):
    for m, l in texts.items():
        if not os.path.isfile(dir + m + '.txt'):
            print 'parsing ' + m
            page = requests.get(l)
            tree = html.fromstring(page.content)
            lines = tree.xpath('//p')
            with open(dir + m + '.txt', 'wb') as f:
                for line in lines:
                    txts = parse_line(line, parse_text_prose)
                    for t in txts:
                        f.write(t.encode('utf-8'))
                        f.write('\n')
            print m + ' parsed!'


def remove_annotations(line):
    ret = ''
    skip = 0
    for c in line:
        if c == '[':
            skip += 1
        elif c == ']':
            skip -= 1
        elif skip == 0:
            ret += c
    return ret


def parse_text_poetry(txt):
    txt = remove_annotations(txt)
    txt = ''.join(ch for ch in txt if ch not in string.digits)
    for o, n in char_replace.items():
        txt = txt.replace(o, n)
    return txt


def parse_text_prose(txt):
    txt = remove_annotations(txt)
    txts = re.split('[./] (?=[A-Z])', txt)
    for i, t in enumerate(txts):
        t = ''.join(ch for ch in t if ch not in string.digits)
        for o, n in char_replace.items():
            t = t.replace(o, n)
        txts[i] = t

    return txts


def parse_line(line, txt_parser=parse_text_poetry):
    txt = line.text or ''
    for child in line.iterchildren():
        if child.tag == 'sup':
            if txt[-1] == 'w':
                txt += 'ith'
            else:
                txt += child.text
        if child.tail:
            txt += child.tail

    return txt_parser(txt)


read_poetry('manuscripts/', manuscripts)
read_poetry('edited/', poetic_texts)
read_prose('edited/', prose_texts)
