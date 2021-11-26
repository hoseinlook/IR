import os.path
from pprint import pprint

from preprocess import NewsData, PreProcess
from query import Query
from reverse_index import InvertedIndex

ORIGIN_DATA = {}
DATA_PATH = './data/news.xlsx'
SAVE_PATH = './data/index'


def create_index_from_file():
    news_data = NewsData(DATA_PATH)
    prepro = PreProcess()
    for item in news_data.iter_items():
        doc_id = item['doc_id']
        ORIGIN_DATA[doc_id] = item
        text = item['content']
        token_list = prepro.start(doc_id=doc_id, text=text)
        InvertedIndex.insert_doc_tokens(token_list)


def load_or_create_the_index():
    if os.path.isfile(SAVE_PATH):
        print('loading index from file')
        InvertedIndex.load(SAVE_PATH)
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
        index_res = Query().start()
        origin_res = [ORIGIN_DATA[i] for i in index_res]
        print([i['title']for i in origin_res])
        
