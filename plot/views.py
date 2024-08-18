from django.views.generic import TemplateView
from django.conf import settings

from plot.functions import CosmosDBClient, unix_timestamp_to_month, generate_and_save_wordcloud
from plot.graphs import line_charts, bar_chart, user_bar_chart

from dotenv import load_dotenv
import os

from collections import defaultdict

import pandas as pd
import collections

# from plot.csv import csvdownload
from django.http import HttpResponse
import csv
import io
import urllib.request

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

#月別に集計
for item in items:
    ts = item.get('_ts')
    if ts:
        month_year = unix_timestamp_to_month(ts)
        monthly_summary[month_year] += 1

#ユーザー(oid)別に利用回数を集計
user_use_count = defaultdict(int)
for item in items:
    oid = item.get('oid')
    if oid:
        user_use_count[oid] += 1

#wordcloudの作成と会話データの取得
question_list =[]
csv_list = []

for item in items:
    messages = item.get('messages')
    category = item.get('category')

    if messages:
        question = messages[0]["content"]
        question_list.append(question)
        if category:
            csv_list.append([",".join(category), question])
        else:
            csv_list.append(["", question])

wordcloud_image_path = generate_and_save_wordcloud(question_list)




class ChartsView(TemplateView):  # ❶
    template_name = "plot.html"

    def get_context_data(self, **kwargs):
        context = super(ChartsView, self).get_context_data(**kwargs)
        context["line_chart"] = line_charts(monthly_summary)
        context["bar_chart"] = bar_chart(monthly_summary)
        context["user_bar_chart"] = user_bar_chart(user_use_count)
        # 画像のURLをコンテキストに追加
        context["wordcloud_image_url"] = os.path.join(settings.MEDIA_URL, wordcloud_image_path)
        return context


def csv_export(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    filename = urllib.parse.quote(('data.csv'))
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
    # Add BOM to the response to help Excel recognize UTF-8 encoding
    response.write('\ufeff'.encode('utf-8'))
    writer = csv.writer(response)
    writer.writerow(['カテゴリ', '会話'])
    writer.writerows(csv_list)
    return response