from django.views.generic import TemplateView  # ❶

from plot.functions import CosmosDBClient, unix_timestamp_to_month
from plot.graphs import line_charts, bar_chart

from dotenv import load_dotenv
import os

from collections import defaultdict

from janome.tokenizer import Tokenizer
from janome.charfilter import *
from janome.tokenfilter import *
from janome.analyzer import Analyzer

import pandas as pd
import collections
from wordcloud import WordCloud


from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from io import BytesIO
from django.conf import settings
from django.urls import reverse

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

# .envファイルを読み込む
load_dotenv()

# 月ごとの集計を格納する辞書
monthly_summary = defaultdict(int)

endpoint = os.getenv("ENDPOINT")
key = os.getenv("COSMOS_KEY")
database_name = os.getenv("DB_NAME")
container_name = os.getenv("CONTAINER_NAME")

db_client = CosmosDBClient(endpoint, key, database_name, container_name)
items = db_client.fetch_items("SELECT * FROM c")

for item in items:
    ts = item.get('_ts')
    if ts:
        month_year = unix_timestamp_to_month(ts)
        monthly_summary[month_year] += 1

question_list =[]

for item in items:
    messages = item.get('messages')
    if messages:
        question = messages[0]["content"]
        question_list.append(question)

t = Tokenizer()
results = []
for s in question_list: 
    tokens = list(t.tokenize(s, wakati=True))
    a = Analyzer(token_filters=[CompoundNounFilter()])
    result = [token.base_form for token in t.tokenize(s) if token.part_of_speech.split(',')[0] in ['名詞']]  # 全角スペースを削除 # リストに追加 results.extend(result)
    results.extend(result) 

# wordcloud
#日本語のフォントパス
font_path = 'ipag.ttc'
text = ' '.join(results) # 区切り文字を「・」にして文字列に変換
# 単語の最大表示数は500に設定
wordcloud = WordCloud(
    background_color='white',
    font_path=font_path,
    width=400,
    height=300,
    max_words=500
).generate(text)

wordcloud_image_path = save_wordcloud_image(wordcloud)
print(wordcloud_image_path)

class ChartsView(TemplateView):  # ❶
    template_name = "plot.html"

    def get_context_data(self, **kwargs):
        context = super(ChartsView, self).get_context_data(**kwargs)
        context["line_chart"] = line_charts(monthly_summary)
        context["bar_chart"] = bar_chart(monthly_summary)
        # 画像のURLをコンテキストに追加
        context["wordcloud_image_url"] = os.path.join(settings.MEDIA_URL, wordcloud_image_path)
        return context
