from collections import defaultdict

import editdistance
import difflib
import itertools
import operator
import gensim
import pickle

model = gensim.models.Word2Vec.load('model/mideng-model')
count = pickle.load(open('model/mideng-count', 'rb'))


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
        self.base = base
        self.alt = alt
        self.thresh = 0.6

        self.insertions = []
        self.alternatives = defaultdict(list)
        self.tostring = ''
        
        self.__post_process()

    def __post_process(self):
        # find intertextual differences
        delta_base = set(self.base) - set(self.alt)
        delta_alt = set(self.alt) - set(self.base)
        
        repr_list = self.alt[::]

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

                index = self.alt.index(pair[0][1])
                repr_list[index] = pair[0][0]

        base_str = ' '.join(self.base)
        alt_str = ' '.join(repr_list)
        self.__find_repr(base_str, alt_str)

    def __find_repr(self, base_str, alt_str):
        # s = difflib.SequenceMatcher(None, base_str, alt_str)
        # for tag, i1, i2, j1, j2 in s.get_opcodes():
        #     if tag == 'equal':
        #         self.tostring += base_str[i1:i2]
        #     if tag == 'insert':
        #         self.tostring += alt_str[j1:j2]

        self.tostring = base_str + '\t\t'
        for word in self.base:
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
        i, j = self.base.index(v), self.alt.index(w)
        cost = model.similarity(v, w)
        cost = cost * discount[min(abs(i - j), len(discount) - 1)]

        return cost


class TextMatcher(object):
    def __init__(self, mss, thresh=0.6):
        self.mss = mss
        self.thresh = thresh

    def match_mss(self, i, j):
        output = []

        texti = list(TextParser(self.mss[i]))
        textj = list(TextParser(self.mss[j]))
        for li, lj in itertools.izip(texti, textj):
            output.append(self.process_line(li, lj))

        return output

    def process_line(self, base, alt):
        return Line(base, alt)
