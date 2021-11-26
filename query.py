from typing import List
import math
from preprocess import Token
from reverse_index import InvertedIndex, PostingsList, Postings


class Query:

    def start(self, ):
        while True:
            list_of_words = input().strip().split()
            query_tokens = [Token(doc_id=-1, word=word, posting=i) for i, word in enumerate(list_of_words)]
            result = self.search(query_tokens)
            print(result)

    def search(self, query_tokens: List[Token]) -> List[int]:
        all_results = []

        all_results += self._best_search(query_tokens)

        return all_results

    def _best_search(self, query_tokens: List[Token]) -> List[int]:

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
            return list(InvertedIndex.get_postings_list(query_tokens[0].word).keys())
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

        return list(merged_result.keys())
