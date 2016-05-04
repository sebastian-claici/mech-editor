import gensim
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

sentences = ManuscriptParser("edited/")
model = gensim.models.Word2Vec(sentences)
