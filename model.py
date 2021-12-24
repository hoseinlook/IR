import ast
import json
import multiprocessing
from preprocess import PreProcess, NewsData
import time
from gensim.models import Word2Vec

cores = multiprocessing.cpu_count()
DATA_PATH = './data/news.xlsx'
SAVE_MODEL_PATH = './data/my_w2v.model'
PARSIVAR_MODEL_PATH ='./data/w2v_150k_parsivar_300.model'


def create_list_of_tokens():
    news_data = NewsData(DATA_PATH)
    prepro = PreProcess()
    doc_list = []
    for item in news_data.iter_items():
        doc_id = item['doc_id']
        text = item['content']
        token_list = prepro.start(doc_id=doc_id, text=text)
        doc_list.append([i.word for i in token_list])
    return doc_list


class W2VecModel:

    def __init__(self):
        self._model = None

    def get_model(self) -> Word2Vec:
        return self._model

    def train_model(self):
        train_data = create_list_of_tokens()
        w2v_model = Word2Vec(min_count=1, window=5, vector_size=300, alpha=0.03, workers=cores - 1)
        w2v_model.build_vocab(train_data)
        w2v_model_vocab_size = len(w2v_model.wv)
        print("vocab size ", w2v_model_vocab_size)
        start = time.time()
        w2v_model.train(train_data, total_examples=w2v_model.corpus_count, epochs=20)
        end = time.time()
        print("Duration: ", end - start)
        return w2v_model

    def save_model(self):
        self._model.save(SAVE_MODEL_PATH)

    def load_model(self, path):
        self._model = Word2Vec.load(path)


