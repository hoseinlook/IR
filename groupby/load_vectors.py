import pickle
from pathlib import Path
from typing import Iterator

import numpy as np
import pandas as pd
from gensim.models import Word2Vec
from hazm import stopwords_list
from numpy import dot
from numpy.linalg import norm

from configs import ABSOLUTE_DATA_PATH
from model import W2VecModel

real_model = W2VecModel()
real_model.load_model(W2VecModel.PARSIVAR_MODEL_PATH)
MODEL = real_model.get_model()
cos_similarity = lambda x, y: abs(dot(x, y) / (norm(x) * norm(y)))
euclidean_dist = lambda point1, point2: np.linalg.norm(point1 - point2)


class TOPICS:
    CULTURE = "culture"
    SPORT = "sport"
    POLITICAL = "political"
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
    df = pd.read_excel(filename)

    for row in df.iterrows():
        topic = row[1].get('topic')
        if topic == "politics": topic = TOPICS.POLITICAL
        if topic == 'sports': topic = TOPICS.SPORT
        yield {
            'content': row[1].get('content'),
            'topic': topic,
            'url': row[1].get('url'),
            'vector': cal_vector(MODEL, row[1]['content']),
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


if not Path(f'{str(ABSOLUTE_DATA_PATH)}/groupby_data/vectorized_data.pickle').is_file():
    vectorized_classified_data()

with open(f'{str(ABSOLUTE_DATA_PATH)}/groupby_data/vectorized_data.pickle', 'rb') as handle:
    vectorized_list = pickle.load(handle)
