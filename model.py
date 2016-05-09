from collections import Counter
import gensim
import pickle
import os


class ManuscriptParser(object):
    def __init__(self, dirname):
        self.dirname = dirname

    def __iter__(self):
        for fname in os.listdir(self.dirname):
            for line in open(os.path.join(self.dirname, fname)):
                words = line.strip().split()
                if words:
                    yield [word.decode('utf-8').lower().encode('utf-8') for word in words]


def train_gensim(d, f):
    sentences = ManuscriptParser(d)
    model = gensim.models.Word2Vec(sentences, sg=1, min_count=1)
    model.save(f)


def count_words(d, f):
    counter = Counter()
    sentences = ManuscriptParser(d)
    for sentence in sentences:
        counter.update(sentence)

    with open(f, 'wb') as output:
        pickle.dump(counter, output)


train_gensim('texts/', 'model/mideng-model')
count_words('texts/', 'model/mideng-count')
