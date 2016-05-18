from collections import defaultdict
import numpy as np
import editdistance
import difflib
import itertools
import operator
import gensim
import pickle

model = gensim.models.Word2Vec.load('model/mideng-model')
count = pickle.load(open('model/mideng-count', 'rb'))


class Manuscript(object):
    def __init__(self, name, filename):
        self.name = name
        self.filename = filename
        self.text = list(TextParser(self.filename))


class TextParser(object):
    def __init__(self, f):
        self.f = f

    def __iter__(self):
        for line in open(self.f):
            words = line.strip().split()
            if words:
                yield [word.decode('utf-8').lower().encode('utf-8') for word in words]


class Line(object):
    def __init__(self, base, alt):
        self.base_line = base
        self.alt_line = alt

        self.thresh = 0.6

        self.insertions = []
        self.alternatives = defaultdict(list)
        self.tostring = ''

        self.__post_process()

    def __post_process(self):
        # find intertextual differences
        delta_base = set(self.base_line) - set(self.alt_line)
        delta_alt = set(self.alt_line) - set(self.base_line)

        repr_list = self.alt_line[::]

        simil = {}
        for v in delta_base:
            for w in delta_alt:
                simil[v, w] = self.__cost(v, w)

        ordered_pairs = sorted(simil.items(), key=operator.itemgetter(1), reverse=True)
        for pair in ordered_pairs:
            if pair[0][0] in delta_base and pair[0][1] in delta_alt:
                self.alternatives[pair[0][0]].append((pair[0][1], pair[1]))
                delta_base.remove(pair[0][0])
                delta_alt.remove(pair[0][1])

                index = self.alt_line.index(pair[0][1])
                repr_list[index] = pair[0][0]

        base_str = ' '.join(self.base_line)
        alt_str = ' '.join(repr_list)
        self.__find_repr(base_str, alt_str)

    def __find_repr(self, base_str, alt_str):
        self.tostring += base_str + '\t\t'
        for word in self.base_line:
            if word in self.alternatives:
                alt_words = [w[0] for w in self.alternatives[word]]
                kept_alts = []
                for alt_word in alt_words:
                    if editdistance.eval(alt_word, word) > 1:
                        kept_alts.append(alt_word)
                if kept_alts:
                    self.tostring += ' ]' + word + ': ' + '; '.join(kept_alts) + '];'

    def __cost(self, v, w):
        discount = [1.0, 0.8, 0.4, 0.2, 0.1, 0.05]
        i, j = self.base_line.index(v), self.alt_line.index(w)
        cost = model.similarity(v, w)
        cost = cost * discount[min(abs(i - j), len(discount) - 1)]

        return cost


class TextMatcher(object):
    def __init__(self, mss, thresh=0.6):
        self.mss = mss
        self.thresh = thresh

    def match_mss(self, i, j, i1=0, i2=None, j1=0, j2=None):
        output = []

        texti = self.mss[i].text[i1:i2]
        textj = self.mss[j].text[j1:j2]
        alignedi, alignedj, tags = self.align_texts(texti, textj)

        for li, lj in itertools.izip(alignedi, alignedj):
            output.append(Line(li, lj))

        return output, tags

    def align_texts(self, fst, scd):
        def similar(l1, l2):
            simil = difflib.SequenceMatcher(None, ' '.join(l1), ' '.join(l2)).ratio()
            return (simil > self.thresh)

        n, m = len(fst), len(scd)
        align = np.zeros((n + 1, m + 1))
        for i in range(n + 1):
            align[i, 0] = i
        for j in range(m + 1):
            align[0, j] = j

        for i in range(1, n + 1):
            for j in range(1, m + 1):
                if similar(fst[i - 1], scd[j - 1]):
                    align[i, j] = align[i - 1, j - 1]
                else:
                    align[i, j] = min(align[i - 1, j] + 1,
                                      align[i, j - 1] + 1,
                                      align[i - 1, j - 1] + 1)

        aligned_fst = []
        aligned_scd = []
        tags = []
        while n > 0 and m > 0:
            if similar(fst[n - 1], scd[m - 1]):
                aligned_fst.append(fst[n - 1])
                aligned_scd.append(scd[m - 1])
                n, m = n - 1, m - 1
            elif align[n, m] == align[n - 1, m] + 1:
                tags.append(('delete', n - 1, m - 1, fst[n - 1]))
                n, m = n - 1, m
            elif align[n, m] == align[n, m - 1] + 1:
                tags.append(('insert', n - 1, m - 1, scd[m - 1]))
                n, m = n, m - 1
            else:
                tags.append(('substitute', n - 1, m - 1, fst[n - 1], scd[m - 1]))
                n, m = n - 1, m - 1

        return reversed(aligned_fst), reversed(aligned_scd), reversed(tags)
