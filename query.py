import itertools
from copy import deepcopy
from typing import List
import math
from preprocess import Token
from reverse_index import InvertedIndex, PostingsList, Postings


def iter_sub_array(arr, size):
    n = len(arr)
    for i in range(0, n):
        for j in range(i, n):
            if len(arr[i:j + 1]) == size:
                yield arr[i:j + 1]


# for item in iter_sub_array([1, 2, 3, 4], 1):
#     print(item)
# exit()


class Query:

    def start(self, query_text=None):
        if query_text is None:
            query_text = input().strip().split()

        list_of_words = query_text
        query_tokens = [Token(doc_id=-1, word=word, posting=i) for i, word in enumerate(list_of_words)]
        result = self.search(query_tokens)
        print(result)
        return result

    def search(self, query_tokens: List[Token]) -> List[int]:
        all_results = []

        all_results += list(self._best_search(query_tokens).keys())

        all_results += self._sub_search(query_tokens)


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

    def _best_search(self, query_tokens: List[Token]) -> PostingsList:

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

    def _sub_search(self, query_tokens: List[Token]):
        results = []
        for i in range(1, len(query_tokens)):
            items = list(iter_sub_array(query_tokens, i))
            setlist = []
            for query in items:
                doc_ids = set(self._best_search(query).keys())
                setlist.append(doc_ids)
            new_res = set.intersection(*setlist)
            results += new_res

        return results