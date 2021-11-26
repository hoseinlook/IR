import os.path

from preprocess import NewsData, PreProcess
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
        print('yes')
        InvertedIndex.load(SAVE_PATH)
        news_data = NewsData(DATA_PATH)
        for item in news_data.iter_items():
            doc_id = item['doc_id']
            ORIGIN_DATA[doc_id] = item
    else:
        print('No')
        create_index_from_file()
        InvertedIndex.save(SAVE_PATH)


if __name__ == '__main__':
    load_or_create_the_index()
    print(InvertedIndex()._index_dict['قطعه'])
