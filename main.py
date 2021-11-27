import os.path

from index import InvertedIndex
from preprocess import NewsData, PreProcess, Statistic
from query import Query

ORIGIN_DATA = {}
DATA_PATH = './data/news.xlsx'
SAVE_PATH = './data/index'
STATISTIC_PATH = './data/statistic'


def create_index_from_file():
    news_data = NewsData(DATA_PATH)
    prepro = PreProcess()
    for item in news_data.iter_items():
        doc_id = item['doc_id']
        ORIGIN_DATA[doc_id] = item
        text = item['content']
        if doc_id + 1 % 5000 == 0:
            Statistic.items[doc_id + 1] = Statistic.Item(tokens_before_stem=PreProcess.all_tokens_count,
                                                         tokens_after_stem=PreProcess.all_tokens_after_stem_count,
                                                         vocab_size=InvertedIndex().vocab_size)
        token_list = prepro.start(doc_id=doc_id, text=text)
        InvertedIndex.insert_doc_tokens(token_list)

    Statistic.save(STATISTIC_PATH)


def load_or_create_the_index():
    if os.path.isfile(SAVE_PATH):
        print('loading index from file')
        InvertedIndex.load(SAVE_PATH)
        Statistic.load(STATISTIC_PATH)
        news_data = NewsData(DATA_PATH)
        for item in news_data.iter_items():
            doc_id = item['doc_id']
            ORIGIN_DATA[doc_id] = item
    else:
        print('creating index')
        create_index_from_file()
        InvertedIndex.save(SAVE_PATH)


if __name__ == '__main__':
    load_or_create_the_index()
    print('files was loaded')
    while True:
        index_res = Query().best_search()
        origin_res = [ORIGIN_DATA[i] for i in index_res]
        print([i['title'] for i in origin_res])
