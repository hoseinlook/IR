import os.path

from index import InvertedIndex, TFIndex, KChampionsList, DocEmbedding
from model import W2VecModel
from preprocess import NewsData, PreProcess, Statistic
from query import Query, IndexEliminateQuery, ChampionsListQuery, W2VecModelQuery

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
        if (doc_id + 1) % 500 == 0:
            print('yes')
            Statistic.items[doc_id + 1] = Statistic.Item(tokens=PreProcess.all_tokens_count,
                                                         vocab_size=InvertedIndex().vocab_size)
        token_list = prepro.start(doc_id=doc_id, text=text)
        InvertedIndex.insert_doc_tokens(token_list)

    Statistic.save(STATISTIC_PATH)


def load_or_create_the_inverted_index():
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
    load_or_create_the_inverted_index()
    TFIndex.initialize()
    KChampionsList(k=10).initialize()
    ChampionsListQuery(query='asd')
    my_model = W2VecModel()
    my_model.load_model(W2VecModel.SAVE_MODEL_PATH)
    my_doc_embedding = DocEmbedding(my_model.get_model())
    my_doc_embedding.initialize()
    W2VecModelQuery(my_doc_embedding, "دانشگاه صنعتی امیرکبیر").get_result()


    print('files was loaded')
    while True:
        print(IndexEliminateQuery().get_result())
    # print(Statistic.items)
