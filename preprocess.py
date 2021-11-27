import dataclasses
import pickle
import re
from copy import deepcopy
from typing import List, Iterator

import pandas as pd
from hazm import word_tokenize, stopwords_list, Lemmatizer
from parsivar import FindStems, Normalizer

bad_chars = ['/', '//', '\\', '\/', '@', '$', '%', '^', '&', '&', '*', '(', ')', '[', ']', '!', '#',
             '{', '}', '(', ')', '~', '!', '+', ',', '=']


class Statistic:
    @dataclasses.dataclass
    class Item:
        tokens_before_stem: int
        tokens_after_stem: int
        vocab_size: int

    items = {

    }

    @classmethod
    def save(cls, to_path):
        with open(to_path, 'wb') as handle:
            pickle.dump(cls.items, handle, protocol=pickle.HIGHEST_PROTOCOL)

    @classmethod
    def load(cls, from_path):
        with open(from_path, 'rb') as handle:
            cls.items = pickle.load(handle)


class NewsData:
    def __init__(self, path):
        self.path = path

    def iter_items(self) -> Iterator[dict]:
        df = pd.read_excel(self.path)
        doc_id = 0
        for row in df.iterrows():
            yield {
                'content': row[1]['content'],
                'title': row[1]['title'],
                'url': row[1]['url'],
                'doc_id': doc_id,
            }
            doc_id += 1


@dataclasses.dataclass
class Token:
    posting: int
    doc_id: int
    word: str

    def __repr__(self):
        return f'{self.doc_id}:{self.posting}:{self.word}'


class PreProcess:
    all_tokens_count = 0
    all_tokens_after_stem_count = 0

    def __init__(self):
        self.stemmer = FindStems()
        self.lemmatizer = Lemmatizer()
        self.stopwords = stopwords_list()

    def start(self, text, doc_id) -> List[Token]:
        text = self._normalize_text(text)
        token_list = word_tokenize(text)
        token_list = [Token(doc_id=doc_id, posting=i, word=word) for i, word in enumerate(token_list)]

        token_list = self.remove_stopwords(token_list)
        PreProcess.all_tokens_count += len(token_list)
        token_list = self.stem(token_list)
        PreProcess.all_tokens_after_stem_count += len(token_list)

        return token_list

    @staticmethod
    def remove_punctuations(text):
        text = re.sub(r'[:;?!-_.,/()،؛~% \\ »«٪”…<>؟$《 》═=&|”“′‘ # @ \+ \* \^ \" \' \{ \}  ]', ' ', text)
        return text

    @staticmethod
    def remove_links(text):
        text = re.sub(r'(https?|t\.me|www\.)(\S+)\s?', '', text, flags=re.MULTILINE | re.IGNORECASE)
        return text

    def _normalize_text(self, txt: str):
        my_normalizer = Normalizer(statistical_space_correction=True)
        txt = my_normalizer.normalize(txt)

        txt = self.remove_links(txt)
        txt = self.remove_punctuations(txt)

        return txt

    def stem(self, token_list: List[Token]) -> List[Token]:
        for i, token in enumerate(deepcopy(token_list)):
            token_list[i].word = self.stemmer.convert_to_stem(token.word)
            # token_list[i].word = self.lemmatizer.lemmatize(token.word)

        return token_list

    def remove_stopwords(self, token_list: List[Token]) -> List[Token]:
        for token in deepcopy(token_list):
            if token.word in self.stopwords or len(token.word) <= 1:
                token_list.remove(token)

        return token_list


if __name__ == '__main__':
    text = 'سلام'
    x = PreProcess().start(text, doc_id=2)

    print(x)
