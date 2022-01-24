import pickle

from configs import ABSOLUTE_DATA_PATH
from groupby.load_vectors import TOPICS, iter_files_contents, vectorized_list, cos_similarity, MODEL, cal_vector


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

            score_vectorized_data.sort(key=lambda x: x[1], reverse=True)
            for i in score_vectorized_data[:self.K]:
                topic = vectorized_list[i[0]]['topic']
                count_topics[topic] += 1

            max_topic = None
            max_count = -1
            for topic, count in count_topics.items():
                if count > max_count:
                    max_topic = topic
                    max_count = count

            self.CLASSIFIED_DATA[max_topic][doc_id] = doc

    def save(self):
        with open(f'{str(ABSOLUTE_DATA_PATH)}/knn_index/original_data.pickle', 'wb') as ori_file:
            with open(f'{str(ABSOLUTE_DATA_PATH)}/knn_index/classifier.pickle', 'wb') as classifier_file:
                pickle.dump(self.ORIGIN_DATA, ori_file, protocol=pickle.HIGHEST_PROTOCOL)
                pickle.dump(self.CLASSIFIED_DATA, classifier_file, protocol=pickle.HIGHEST_PROTOCOL)

    @classmethod
    def load(cls) -> 'KNN':
        with open(f'{str(ABSOLUTE_DATA_PATH)}/knn_index/original_data.pickle', 'rb') as ori_file:
            with open(f'{str(ABSOLUTE_DATA_PATH)}/knn_index/classifier.pickle', 'rb') as classifier_file:
                knn = KNN()
                knn.ORIGIN_DATA = pickle.load(ori_file)
                knn.CLASSIFIED_DATA = pickle.load(classifier_file)
        return knn

    def query(self, text_query: str, cat: str, count):
        if cat not in [TOPICS.SPORT, TOPICS.POLITICAL, TOPICS.HEALTH, TOPICS.CULTURE, TOPICS.ECONOMY]:
            print("bad category")
            return None

        vector = cal_vector(MODEL, text_query)
        items = self.CLASSIFIED_DATA[cat].values()
        result = []
        for item in items:
            score = cos_similarity(vector, item['vector'])
            result.append((item, score))

        result.sort(key=lambda x: x[1], reverse=True)

        return [i[0] for i in result[:count]], [i[1] for i in result[:count]]
