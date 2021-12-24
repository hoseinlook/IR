import math
import pickle
from typing import List, Set

from preprocess import Token


class Postings(list):
    pass


class PostingsList(dict):

    def get_related_postings(self, doc_id: int) -> Postings:
        return self.get(doc_id)

    def insert_a_post(self, doc_id, posting):
        if self.get_related_postings(doc_id) is None:
            self[doc_id] = Postings()
        self.get_related_postings(doc_id).append(posting)

    def intersection_keys(self, other) -> Set[int]:
        intersection_keys = set(self.keys()).intersection(set(other.keys()))
        return intersection_keys

    @property
    def count_all(self):
        return sum([len(i) for i in self.values()])


class InvertedIndex:
    _index_dict = {}

    @property
    def vocab_size(cls) -> int:
        return len(cls._index_dict.keys())

    @classmethod
    def get_counts(cls):
        return {
            i: value.count_all for i, value in cls._index_dict.items()
        }

    @classmethod
    def get_postings_list(cls, word) -> PostingsList:
        item = cls._index_dict.get(word)
        return item if item is not None else PostingsList()

    @classmethod
    def insert_doc_tokens(cls, token_list: List[Token]):
        for token in token_list:
            if token.word not in cls._index_dict:
                cls._index_dict[token.word] = item = PostingsList()
                item.insert_a_post(doc_id=token.doc_id, posting=token.posting)
            else:
                cls._index_dict[token.word].insert_a_post(doc_id=token.doc_id, posting=token.posting)

    @classmethod
    def save(cls, to_path):
        with open(to_path, 'wb') as handle:
            pickle.dump(cls._index_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)

    @classmethod
    def load(cls, from_path):
        with open(from_path, 'rb') as handle:
            cls._index_dict = pickle.load(handle)

    def __iter__(self):
        for item in self._index_dict.keys():
            yield item

    def __str__(self):
        return str(self._index_dict)

    def __repr__(self):
        return self.__str__()


class TFIndex:
    _index_dict = None
    _weight_dict = None
    _N = 0

    @classmethod
    def doc_id_size(cls, doc_id):
        return len(cls._index_dict[doc_id].keys())

    @classmethod
    def get_weight(cls, doc_id, term):
        return cls._weight_dict[doc_id][term] if cls._weight_dict[doc_id].get(term) is not None else 0

    @classmethod
    def initialize(cls):
        cls.load_index_from_inverted_index()
        cls.calculate_weights()

    @classmethod
    def load_index_from_inverted_index(cls):
        if cls._index_dict is not None: return
        cls._index_dict = {}
        for term in InvertedIndex():
            postings_list = InvertedIndex.get_postings_list(term)
            for doc_id in postings_list:
                if doc_id not in cls._index_dict:
                    cls._index_dict[doc_id] = {}

                cls._index_dict[doc_id][term] = len(postings_list.get_related_postings(doc_id))

        cls._N = len(cls._index_dict.keys())
        # cls._normalize()

    @classmethod
    def calculate_weights(cls, normalize=True):
        cls._weight_dict = {}
        doc_count = cls._N
        tf = lambda term_freq: math.log(term_freq) + 1

        for doc_id in cls._index_dict.keys():
            term_list = cls._index_dict[doc_id]
            for term, term_freq in term_list.items():
                if doc_id not in cls._weight_dict:
                    cls._weight_dict[doc_id] = {}
                cls._weight_dict[doc_id][term] = tf(term_freq)

        if normalize:
            cls._normalize()

    @classmethod
    def _normalize(cls):
        for doc_id in cls._weight_dict.keys():
            sum = 0
            doc__dict = cls._weight_dict[doc_id]
            for value in doc__dict.values():
                sum += value ** 2
            norm = math.sqrt(sum)
            for key in doc__dict.keys():
                doc__dict[key] = doc__dict[key] / norm

    def __str__(self):
        return str(self._index_dict)


class KChampionsList:
    _k_related_list = {}

    @classmethod
    def get(cls, key) -> list:
        return cls._k_related_list.get(key, [])

    def __init__(self, k=10):
        self.k = k

    def initialize(self):
        for term in InvertedIndex():
            doc_list = []
            for doc_id in InvertedIndex.get_postings_list(term):
                doc_weight = TFIndex.get_weight(doc_id, term)

                doc_list.append((doc_id, doc_weight))

            doc_list.sort(key=lambda x: x[1], reverse=True)

            self._k_related_list[term] = [i[0] for i in doc_list][:self.k]


if __name__ == '__main__':
    InvertedIndex.load('./data/index')
    # InvertedIndex.insert_doc_tokens([Token(1, 1, 'xx'), ])
    # InvertedIndex.insert_doc_tokens([Token(2, 1, 'xx'), ])
    # InvertedIndex.insert_doc_tokens([Token(3, 2, 'xx'), ])
    TFIndex().initialize()
    # print(TFIndex())
    KChampionsList().initialize()
    print('DOne')
    # InvertedIndex.save('./data/index')
    # InvertedIndex.load('./data/index')
    # print(InvertedIndex())
