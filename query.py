import itertools
from copy import deepcopy
from typing import List
import math
from preprocess import Token, PreProcess
from index import InvertedIndex, PostingsList, Postings, TFIndex, KChampionsList


def iter_sub_array(arr, size):
    n = len(arr)
    for i in range(0, n):
        for j in range(i, n):
            if len(arr[i:j + 1]) == size:
                yield arr[i:j + 1]


class Query:

    def __init__(self, query_text=None):
        if query_text is None:
            query_text = input()

        list_of_words = query_text.strip().split()
        self.query_text = query_text
        self.query_tokens = [Token(doc_id=-1, word=word, posting=i) for i, word in enumerate(list_of_words)]

    def full_search(self, ) -> List[int]:
        all_results = []

        all_results += self.best_search()

        all_results += self.sub_search()

        new_res = self.unique_results_with_order(all_results)

        return new_res

    def unique_results_with_order(self, all_results):
        temp = set()
        new_res = []
        for item in all_results:
            if item not in temp:
                new_res.append(item)
                temp.add(item)
        return new_res

    def _complete_combination_search(self, query_tokens: List[Token]) -> PostingsList:

        def merge(postings_list1, postings_list2, pos_diff) -> PostingsList:
            merged_result = PostingsList()
            intersection_keys = postings_list1.intersection_keys(postings_list2)
            for common_doc_id in intersection_keys:
                pos_list1 = postings_list1.get(common_doc_id)
                pos_list2 = postings_list2.get(common_doc_id)
                for pos in pos_list2:
                    if (pos - pos_diff) in pos_list1:
                        if merged_result.get(common_doc_id) is None:
                            merged_result[common_doc_id] = []
                        merged_result[common_doc_id].append(pos)
            return merged_result

        if len(query_tokens) == 1:
            return InvertedIndex.get_postings_list(query_tokens[0].word)
        token1 = query_tokens[0]
        token2 = query_tokens[1]
        postings_list1 = InvertedIndex.get_postings_list(token1.word)
        postings_list2 = InvertedIndex.get_postings_list(token2.word)
        pos_diff = int(math.fabs(token1.posting - token2.posting))
        last_pos = token2.posting
        merged_result = merge(postings_list1, postings_list2, pos_diff)
        for other_token in query_tokens[2:]:
            postings_list2 = InvertedIndex.get_postings_list(other_token.word)
            pos_diff = int(math.fabs(last_pos - other_token.posting))
            merged_result = merge(merged_result, postings_list2, pos_diff)
            last_pos = other_token.posting

        return merged_result

    def sub_search(self):
        query_tokens = self.query_tokens
        query_tokens: List[Token]

        results = []
        for i in range(1, len(query_tokens)):
            items = list(iter_sub_array(query_tokens, i))
            setlist = []
            for query in items:
                doc_ids = set(self._complete_combination_search(query).keys())
                setlist.append(doc_ids)
            new_res = set.intersection(*setlist)
            results += new_res

            new_res = set.union(*setlist)
            results += new_res

        return results

    def best_search(self):
        query_tokens = self.query_tokens
        query_tokens: List[Token]

        return list(self._complete_combination_search(query_tokens).keys())


class IndexEliminateQuery:

    def __init__(self, query=None):
        if query is None:
            query = input().strip()
        self.query = query

    def get_result(self):
        token_list = list(set(self.preprocess_query()))
        token_weight_dict = self.calculate_weights(token_list)
        token_weight_dict = self.normalize(token_weight_dict)

        scores_list = []
        related_doc_id_list = self.get_related_doc_id_list(token_list)

        for doc_id in related_doc_id_list:
            s = 0
            doc_size = TFIndex.doc_id_size(doc_id)
            for token in token_weight_dict.keys():
                term = token.word
                s += TFIndex.get_weight(doc_id, term) * token_weight_dict[token]
            scores_list.append((doc_id, s / doc_size))

        scores_list.sort(key=lambda x: x[1], reverse=True)
        return [i[0] for i in scores_list]

    def calculate_weights(self, token_list):
        doc_count = TFIndex()._N
        df = lambda term: math.log(doc_count / len(InvertedIndex.get_postings_list(term))) if term in InvertedIndex() else 0
        tf = lambda term_freq: math.log(term_freq) + 1
        token_weight_dict = {}
        for token in set(token_list):
            wt_q = tf(token_list.count(token)) * df(term=token.word)
            token_weight_dict[token] = wt_q

        return token_weight_dict

    def preprocess_query(self) -> List[Token]:
        return PreProcess().start(self.query, 1)


    def normalize(self, token_weight_dict):
        sum = 0
        for value in token_weight_dict.values():
            sum += value ** 2
        norm = math.sqrt(sum)

        for key in token_weight_dict.keys():
            token_weight_dict[key] = token_weight_dict[key] / norm

        return token_weight_dict

    def get_related_doc_id_list(self, token_list):
        doc_set = set()
        for token in token_list:
            term = token.word
            doc_set = doc_set.union(set(InvertedIndex.get_postings_list(term)))

        return list(doc_set)


class ChampionsListQuery(IndexEliminateQuery):

    def get_related_doc_id_list(self, token_list):
        doc_set = set()
        for token in token_list:
            term = token.word
            doc_set = doc_set.union(set(KChampionsList.get(term)))

        return list(doc_set)

    def get_result(self, count=10):
        return super().get_result()[:count]
