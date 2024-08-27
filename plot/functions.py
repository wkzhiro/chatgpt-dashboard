from azure.cosmos import CosmosClient, exceptions
from datetime import datetime

from janome.tokenizer import Tokenizer
from janome.charfilter import *
from janome.tokenfilter import CompoundNounFilter
from janome.analyzer import Analyzer

from io import BytesIO
from wordcloud import WordCloud
from django.conf import settings

import os


class CosmosDBClient:
    def __init__(self, endpoint, key, database_name, container_name):
        self.endpoint = endpoint
        self.key = key
        self.database_name = database_name
        self.container_name = container_name
        self.client = CosmosClient(self.endpoint, self.key)
        self.database = self.client.get_database_client(self.database_name)
        self.container = self.database.get_container_client(self.container_name)

    def fetch_items(self, query):
        """
        Cosmos DBからアイテムをクエリして取得するメソッド
        """
        try:
            items = self.container.query_items(
                query=query,
                enable_cross_partition_query=True  # パーティションを越えてクエリを実行するオプション
            )
            return list(items)
        except exceptions.CosmosHttpResponseError as e:
            print(f"Cosmos DBのクエリに失敗しました: {e}")
            return None
        
def unix_timestamp_to_month(ts):
    """
    Unixエポックタイムスタンプを月ごとの形式に変換する関数
    """
    date = datetime.fromtimestamp(ts)
    return date.strftime('%Y-%m')  # 'YYYY-MM'形式

def unix_timestamp_to_hour(ts):
    """
    Unixエポックタイムスタンプを時間単位の datetime オブジェクトに変換する関数
    """
    return datetime.fromtimestamp(ts)


# WordCloudの画像を保存する
def save_wordcloud_image(wordcloud):
    # BytesIOオブジェクトに画像を保存
    buffer = BytesIO()
    wordcloud.to_image().save(buffer, format='PNG')
    image_content = buffer.getvalue()

    # Djangoのファイルストレージに保存
    image_file_name = 'wordcloud_image.png'
    file_path = os.path.join(settings.MEDIA_ROOT, image_file_name)

    # ファイルに保存
    with open(file_path, 'wb') as f:
        f.write(image_content)

    return file_path

def generate_and_save_wordcloud(question_list, font_path='ipag.ttc', width=400, height=300, max_words=500):
    # WordCloudを生成
    t = Tokenizer()
    results = []
    for s in question_list: 
        tokens = list(t.tokenize(s, wakati=True))
        a = Analyzer(token_filters=[CompoundNounFilter()])
        #名刺のみ抽出
        result =  [token.base_form for token in a.analyze(s) if token.part_of_speech.split(',')[0] in ['名詞']]  # 全角スペースを削除 
        results.extend(result) 
    
    text = ' '.join(results)

    wordcloud = WordCloud(
        background_color='white',
        font_path=font_path,
        width=width,
        height=height,
        max_words=max_words
    ).generate(text)

    wordcloud_image_path = save_wordcloud_image(wordcloud)


    return wordcloud_image_path

