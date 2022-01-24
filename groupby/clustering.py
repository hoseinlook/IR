import pickle
import random
from typing import List

from numpy import ndarray

from configs import ABSOLUTE_DATA_PATH
from groupby.load_vectors import TOPICS, iter_files_contents, vectorized_list, cos_similarity, cal_vector, MODEL


class CalKMeans:
    class Center:
        def __init__(self, vector: ndarray, registered_vector_list: List[ndarray]):
            self.vector = vector
            self.registered_vector_list = registered_vector_list

        def __repr__(self):
            return str(len(self.registered_vector_list))

        def __hash__(self):
            return hash(str(self.vector))

    def find_closet_centroid(self, center_list: List['CalKMeans.Center'], vector: ndarray) -> 'CalKMeans.Center':
        a_list = [(c, cos_similarity(vector, c.vector)) for c in center_list]
        a_list.sort(key=lambda x: x[1], reverse=True)
        return a_list[0][0]

    def cluster_on_50k_data(self, k=20, iteration=2):
        center_list = [CalKMeans.Center(vector=i['vector'], registered_vector_list=[]) for i in random.choices(vectorized_list, k=k)]
        str_vector = sum(sum([c.vector for c in center_list]))
        epoch = 0
        for _ in range(iteration):
            print("EPOCH ", epoch)
            epoch += 1
            # renew registered node
            for center in center_list:
                center.registered_vector_list = []

            for node in vectorized_list:
                node_vector = node['vector']
                c = self.find_closet_centroid(center_list, node_vector)
                c.registered_vector_list.append(node)

            # recalculate center
            for center in center_list:
                new_center_vector = None
                for register_node in center.registered_vector_list:
                    new_center_vector = new_center_vector + register_node['vector'] if new_center_vector is not None else register_node['vector']
                new_center_vector = new_center_vector / len(center.registered_vector_list)
                center.vector = new_center_vector

            # new_str_vector = '_'.join([str(c.vector) for c in center_list])
            new_str_vector = sum(sum([c.vector for c in center_list]))
            if new_str_vector == str_vector:
                break
            str_vector = new_str_vector

        return center_list

    def start_and_save(self, k, iteration):
        center_list = self.cluster_on_50k_data(k, iteration)
        with open(f'{str(ABSOLUTE_DATA_PATH)}/kmeans_index/clustered.pickle', 'wb') as file:
            pickle.dump(center_list, file, protocol=pickle.HIGHEST_PROTOCOL)

    @classmethod
    def load_centers(cls) -> List['CalKMeans.Center']:
        with open(f'{str(ABSOLUTE_DATA_PATH)}/kmeans_index/clustered.pickle', 'rb') as file:
            centers = pickle.load(file)

        return centers


# CalKMeans().start_and_save(20, 200)


class KMeansIndex:
    ORIGIN_DATA = {}
    CLUSTERED_DATA = {

    }

    def read_7K_news(self):
        doc_id = 0
        for item in iter_files_contents(f'{str(ABSOLUTE_DATA_PATH)}/news.xlsx'):
            item['id'] = doc_id
            self.ORIGIN_DATA[doc_id] = item
            print(doc_id)
            doc_id += 1

    def init(self):
        self.read_7K_news()
        self.centers = CalKMeans.load_centers()
        self.CLUSTERED_DATA = {i: [] for i in self.centers}
        self._calculate_kmeans()
        self.save()

    def _calculate_kmeans(self):
        print("START")
        for item in self.ORIGIN_DATA.values():
            print(item['id'])
            item_vector = item['vector']
            best_center = max(self.centers, key=lambda x: cos_similarity(x.vector, item_vector))
            self.CLUSTERED_DATA[best_center].append(item)

    def save(self):
        with open(f'{str(ABSOLUTE_DATA_PATH)}/kmeans_index/original_data.pickle', 'wb') as ori_file:
            with open(f'{str(ABSOLUTE_DATA_PATH)}/kmeans_index/7k_news_clustered.pickle', 'wb') as classifier_file:
                pickle.dump(self.ORIGIN_DATA, ori_file, protocol=pickle.HIGHEST_PROTOCOL)
                pickle.dump(self.CLUSTERED_DATA, classifier_file, protocol=pickle.HIGHEST_PROTOCOL)

    @classmethod
    def load(cls) -> 'KMeansIndex':
        with open(f'{str(ABSOLUTE_DATA_PATH)}/kmeans_index/original_data.pickle', 'rb') as ori_file:
            with open(f'{str(ABSOLUTE_DATA_PATH)}/kmeans_index/7k_news_clustered.pickle', 'rb') as classifier_file:
                kmean = KMeansIndex()
                kmean.ORIGIN_DATA = pickle.load(ori_file)
                kmean.CLUSTERED_DATA = pickle.load(classifier_file)
        return kmean

    def query(self, text_query: str, count):
        vector = cal_vector(MODEL, text_query)

        best_center = max(self.CLUSTERED_DATA.keys(), key=lambda x: cos_similarity(x.vector, vector))

        results = [(i, cos_similarity(vector, i['vector'])) for i in self.CLUSTERED_DATA[best_center]]

        results.sort(key=lambda x: x[1], reverse=True)

        return [i[0] for i in results][:count], [i[1] for i in results][:count]


def find_rss_statistics():
    k_list = []
    score_list = []

    for k in range(2, 50):
        score = 0
        center_list: List[CalKMeans.Center] = CalKMeans().cluster_on_50k_data(k=k)
        for center in center_list:
            for node in center.registered_vector_list:
                score += cos_similarity(node['vector'], center.vector)
        score_list.append(score)
        k_list.append(k)

    return k_list, score_list
