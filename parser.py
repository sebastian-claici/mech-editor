from lxml import html
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


edited_texts = {
    'Robinson': 'http://quod.lib.umich.edu/c/cme/CT?rgn=main;view=fulltext',
    'Troilus': 'http://quod.lib.umich.edu/c/cme/Troilus?rgn=main;view=fulltext',
    'Pearl': 'http://quod.lib.umich.edu/c/cme/Pearl?rgn=main;view=fulltext',
}


char_replace = {
    u'\u00c0': 'A',
    u'\u00c1': 'A',
    u'\u00c2': 'A',
    u'\u00c3': 'A',
    u'\u00c4': 'A',
    u'\u00c5': 'A',

    u'\u00c8': 'E',
    u'\u00c9': 'E',
    u'\u00ca': 'E',
    u'\u00cb': 'E',

    u'\u00cc': 'I',
    u'\u00cd': 'I',
    u'\u00ce': 'I',
    u'\u00cf': 'I',

    u'\u00d2': 'O',
    u'\u00d3': 'O',
    u'\u00d4': 'O',
    u'\u00d5': 'O',
    u'\u00d6': 'O',

    u'\u00d9': 'U',
    u'\u00da': 'U',
    u'\u00db': 'U',
    u'\u00dc': 'U',

    u'\u00e0': 'a',
    u'\u00e1': 'a',
    u'\u00e2': 'a',
    u'\u00e3': 'a',
    u'\u00e4': 'a',
    u'\u00e5': 'a',

    u'\u00e8': 'e',
    u'\u00e9': 'e',
    u'\u00ea': 'e',
    u'\u00eb': 'e',

    u'\u00ec': 'i',
    u'\u00ed': 'i',
    u'\u00ee': 'i',
    u'\u00ef': 'i',

    u'\u00f2': 'o',
    u'\u00f3': 'o',
    u'\u00f4': 'o',
    u'\u00f5': 'o',
    u'\u00f6': 'o',

    u'\u00f9': 'u',
    u'\u00fa': 'u',
    u'\u00fb': 'u',
    u'\u00fc': 'u',

    u'\u2234': ' ',
    u'\u2235': ' ',
    u'\u00b6': '',

    '&': 'and'
    }


def read_edited():
    for m, l in edited_texts.items():
        if not os.path.isfile('edited/' + m + '.txt'):
            page = requests.get(l)
            tree = html.fromstring(page.content)
            lines = tree.xpath('//div[@class="line"]')
            with open('edited/' + m + '.txt', 'wb') as f:
                for line in lines:
                    f.write(parse_line(line).encode('utf-8'))
                    f.write('\n')
            print m + ' parsed!'


def read_manuscripts():
    for m, l in manuscripts.items():
        if not os.path.isfile('manuscripts/' + m + '.txt'):
            page = requests.get(l)
            tree = html.fromstring(page.content)
            lines = tree.xpath('//div[@class="line"]')
            with open('manuscripts/' + m + '.txt', 'wb') as f:
                for line in lines:
                    f.write(parse_line(line).encode('utf-8'))
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


def parse_line(line):
    txt = line.text
    for child in line.iterchildren():
        if child.tag == 'sup':
            if txt[-1] == 'w':
                txt += 'ith'
            else:
                txt += child.text
        if child.tail:
            txt += child.tail

    for o, n in char_replace.items():
        txt = txt.replace(o, n)

    txt = remove_annotations(txt)
    txt = ''.join(ch for ch in txt if ch not in string.punctuation)

    return txt


read_manuscripts()
read_edited()
