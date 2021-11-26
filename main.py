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
        text = item['title'] + ' ' + item['content']
        token_list = prepro.start(doc_id=doc_id, text=text)
        InvertedIndex.insert_doc_tokens(token_list)


if __name__ == '__main__':
    if os.path.isfile(SAVE_PATH):
        print('yes')
        InvertedIndex.load(SAVE_PATH)
        print(InvertedIndex()._index_dict['بازیکن'])
    else:
        print('No')
        create_index_from_file()
        InvertedIndex.save(SAVE_PATH)
