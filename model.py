import ast
import json
import multiprocessing

from configs import ABSOLUTE_DATA_PATH
from preprocess import PreProcess, NewsData
import time
from gensim.models import Word2Vec

cores = multiprocessing.cpu_count()


class W2VecModel:
    DATA_PATH = f'{str(ABSOLUTE_DATA_PATH)}/news.xlsx'
    SAVE_MODEL_PATH = f'{str(ABSOLUTE_DATA_PATH)}/my_w2v.model'
    PARSIVAR_MODEL_PATH = f'{str(ABSOLUTE_DATA_PATH)}/w2v_150k_parsivar_300.model'

    @classmethod
    def create_list_of_tokens(cls):
        news_data = NewsData(cls.DATA_PATH)
        prepro = PreProcess()
        doc_list = []
        for item in news_data.iter_items():
            doc_id = item['doc_id']
            text = item['content']
            token_list = prepro.start(doc_id=doc_id, text=text)
            doc_list.append([i.word for i in token_list])
        return doc_list

    def __init__(self):
        self._model = None

    def get_model(self) -> Word2Vec:
        return self._model

    def train_model(self):
        train_data = self.create_list_of_tokens()
        w2v_model = Word2Vec(min_count=1, window=5, vector_size=300, alpha=0.03, workers=cores - 1)
        w2v_model.build_vocab(train_data)
        w2v_model_vocab_size = len(w2v_model.wv)
        print("vocab size ", w2v_model_vocab_size)
        start = time.time()
        w2v_model.train(train_data, total_examples=w2v_model.corpus_count, epochs=20)
        end = time.time()
        print("Duration: ", end - start)
        self._model = w2v_model

    def save_model(self):
        self._model.save(self.SAVE_MODEL_PATH)

    def load_model(self, path):
        self._model = Word2Vec.load(path)


if __name__ == '__main__':
    my_model = W2VecModel()
    real_model = W2VecModel()
    # my_model.train_model()
    # my_model.save_model()
    my_model.load_model(W2VecModel.SAVE_MODEL_PATH)
    real_model.load_model(W2VecModel.PARSIVAR_MODEL_PATH)
    model = my_model.get_model()
    print((model.wv.most_similar('پرسپولیس')))
    print((real_model.get_model().wv.get_vector('پرسپولیس')))
