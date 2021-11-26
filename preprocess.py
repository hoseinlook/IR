import dataclasses
from copy import deepcopy
from typing import List, Iterator
import pandas as pd
from hazm import word_tokenize, stopwords_list, Stemmer, Lemmatizer


class NewsData:
    def __init__(self, path):
        self.path = path

    def iter_items(self) -> Iterator[dict]:
        df = pd.read_excel(self.path)
        doc_id =0
        for row in df.iterrows():
            yield {
                'content': row[1]['content'],
                'title': row[1]['title'],
                'url': row[1]['url'],
                'doc_id': doc_id,
            }
            doc_id+=1


@dataclasses.dataclass
class Token:
    posting: int
    doc_id: int
    word: str

    def __repr__(self):
        return f'{self.doc_id}:{self.posting}:{self.word}'


class PreProcess:

    def __init__(self):
        self.stemmer = Stemmer()
        self.lemmatizer = Lemmatizer()
        self.stopwords = stopwords_list()

    def start(self, text, doc_id):
        token_list = word_tokenize(text)
        token_list = [Token(doc_id=doc_id, posting=i, word=word) for i, word in enumerate(token_list)]
        print(token_list)
        token_list = self._normalization(token_list)
        print(token_list)
        token_list = self._remove_stopwords(token_list)
        print(token_list)

        return token_list

    def _normalization(self, token_list: List[Token]):
        for i, token in enumerate(token_list):
            token_list[i].word = self.stemmer.stem(token.word)
            # token_list[i].word = self.lemmatizer.lemmatize(token.word)

        return token_list

    def _remove_stopwords(self, token_list: List[Token]):
        for token in token_list:
            if token.word in self.stopwords:
                token_list.remove(token)
        return token_list


if __name__ == '__main__':
    x = PreProcess().start('واکنش مرتضی حیدری به شوخی‌های فضای مجازی با سوالاتش', doc_id=2)

    for item in NewsData('./data/news.xlsx').iter_items():
        print(item)
        break
