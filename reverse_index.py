import dataclasses
from typing import List

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


class InvertedIndex:
    _index_dict = {}

    @classmethod
    def insert_doc_tokens(cls, token_list: List[Token]):
        for token in token_list:
            if token.word not in cls._index_dict:
                cls._index_dict[token.word] = item = PostingsList()
                item.insert_a_post(doc_id=token.doc_id, posting=token.posting)
            else:
                cls._index_dict[token.word].insert_a_post(doc_id=token.doc_id, posting=token.posting)

    def __str__(self):
        return str(self._index_dict)

    def __repr__(self):
        return self.__str__()


if __name__ == '__main__':
    InvertedIndex.insert_doc_tokens([Token(1, 1, 'mamad'),Token(2, 1, 'mamad'),Token(3, 2, 'mamad')])
    print(InvertedIndex())
