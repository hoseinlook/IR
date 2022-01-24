import pickle
from typing import Iterator

import pandas as pd
from gensim.models import Word2Vec
from hazm import stopwords_list
from numpy import dot
from numpy.linalg import norm

from configs import ABSOLUTE_DATA_PATH
from model import W2VecModel


class TOPICS:
    CULTURE = "culture"
    SPORT = "sport"
    SPORTS = "sports"
    POLITICAL = "political"
    POLITICS = "politics"
    ECONOMY = "economy"
    HEALTH = "health"


stop_words = stopwords_list()


def cal_vector(wv_model: Word2Vec, content: str):
    items = content.split()
    vector = None
    count = 0
    for word in items:
        if word in stop_words:
            continue

        try:
            new_vec = wv_model.wv.get_vector(word)
            if vector is None:
                vector = new_vec
            else:
                vector = vector + new_vec
            count += 1
        except KeyError:
            pass
    if vector is None: return None
    return vector / count


def iter_files_contents(filename) -> Iterator[dict]:
    real_model = W2VecModel()
    real_model.load_model(W2VecModel.PARSIVAR_MODEL_PATH)
    model = real_model.get_model()

    df = pd.read_excel(filename)

    for row in df.iterrows():
        yield {
            'content': row[1].get('content'),
            'topic': row[1].get('topic'),
            'url': row[1].get('url'),
            'vector': cal_vector(model, row[1]['content']),
        }


def vectorized_classified_data():
    doc_id = 1
    vectorized_list = []

    for filename in ['../data/groupby_data/IR00_3_11k News.xlsx', '../data/groupby_data/IR00_3_17k News.xlsx',
                     '../data/groupby_data/IR00_3_20k News.xlsx']:
        for item in iter_files_contents(filename):
            item['id'] = doc_id
            if item['vector'] is None: continue
            vectorized_list.append(item)
            doc_id += 1
            print(filename, doc_id)
        with open(f'{str(ABSOLUTE_DATA_PATH)}/groupby_data/vectorized_data.pickle', 'wb') as file:
            pickle.dump(vectorized_list, file, protocol=pickle.HIGHEST_PROTOCOL)


# vectorized_classified_data()

cos_similarity = lambda x, y: abs(dot(x, y) / (norm(x) * norm(y)))

with open(f'{str(ABSOLUTE_DATA_PATH)}/groupby_data/vectorized_data.pickle', 'rb') as handle:
    vectorized_list = pickle.load(handle)


class KNN:
    ORIGIN_DATA = {}
    CLASSIFIED_DATA = {
        TOPICS.SPORT: {},
        TOPICS.POLITICAL: {},
        TOPICS.ECONOMY: {},
        TOPICS.HEALTH: {},
        TOPICS.CULTURE: {},
    }

    def read_7K_news(self):
        doc_id = 0
        for item in iter_files_contents(f'{str(ABSOLUTE_DATA_PATH)}/news.xlsx'):
            item['id'] = doc_id
            self.ORIGIN_DATA[doc_id] = item
            print(doc_id)
            doc_id += 1

    def __init__(self, k=15):
        self.K = k

    def init(self):
        self.read_7K_news()
        self._calculate_knn()
        self.save()

    def _calculate_knn(self):
        print('START to train')
        for doc_id, doc in self.ORIGIN_DATA.items():
            print(doc_id)
            count_topics = {
                TOPICS.SPORT: 0,
                TOPICS.POLITICAL: 0,
                TOPICS.ECONOMY: 0,
                TOPICS.HEALTH: 0,
                TOPICS.CULTURE: 0,
            }
            score_vectorized_data = []
            doc_vector = doc['vector']
            for i, item in enumerate(vectorized_list):
                item_vector = item['vector']
                score = cos_similarity(doc_vector, item_vector)
                score_vectorized_data.append((i, score))

            score_vectorized_data.sort(key=lambda x: x[1],reverse =True)
            for i in score_vectorized_data[:self.K]:
                topic = vectorized_list[i[0]]['topic']
                if topic == TOPICS.POLITICS: topic = TOPICS.POLITICAL
                if topic == TOPICS.SPORTS: topic = TOPICS.SPORT
                count_topics[topic] += 1

            max_topic = None
            max_count = -1
            for topic, count in count_topics.items():
                if count > max_count:
                    max_topic = topic
                    max_count =count

            self.CLASSIFIED_DATA[max_topic][doc_id] = doc

    def save(self):
        with open(f'{str(ABSOLUTE_DATA_PATH)}/knn_index/original_data.pickle' ,'wb') as ori_file:
            with open(f'{str(ABSOLUTE_DATA_PATH)}/knn_index/classifier.pickle' , 'wb') as classifier_file:
                pickle.dump(self.ORIGIN_DATA, ori_file, protocol=pickle.HIGHEST_PROTOCOL)
                pickle.dump(self.CLASSIFIED_DATA, classifier_file, protocol=pickle.HIGHEST_PROTOCOL)

    @classmethod
    def load(cls) -> 'KNN':
        with open(f'{str(ABSOLUTE_DATA_PATH)}/knn_index/original_data.pickle') as ori_file:
            with open(f'{str(ABSOLUTE_DATA_PATH)}/knn_index/classifier.pickle') as classifier_file:
                knn = KNN()
                knn.ORIGIN_DATA = pickle.load(ori_file)
                knn.CLASSIFIED_DATA = pickle.load(classifier_file)
        return knn


KNN().init()
