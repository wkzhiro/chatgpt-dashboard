from django.views.generic import TemplateView
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from plot.functions import CosmosDBClient, unix_timestamp_to_month, generate_and_save_wordcloud
from plot.graphs import line_charts, bar_chart, user_bar_chart

from dotenv import load_dotenv
import os

from collections import defaultdict

import pandas as pd
import collections

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

def get_date_range_and_period_type(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    period_type = request.GET.get('period_type', 'monthly')

    if not start_date:
        start_date = (timezone.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    if not end_date:
        end_date = timezone.now().strftime('%Y-%m-%d')

    return start_date, end_date, period_type

class ChartsView(TemplateView):
    template_name = "plot.html"

    def get_context_data(self, **kwargs):
        context = super(ChartsView, self).get_context_data(**kwargs)

        start_date, end_date, period_type = get_date_range_and_period_type(self.request)

        filtered_items = self.filter_items_by_date(items, start_date, end_date)

        summary = self.get_summary(filtered_items, period_type)
        user_use_count = self.get_user_use_count(filtered_items)
        question_list = self.get_question_list(filtered_items)

        context["line_chart"] = line_charts(summary, period_type)
        context["bar_chart"] = bar_chart(summary, period_type)
        context["user_bar_chart"] = user_bar_chart(user_use_count)
        
        # WordCloudの生成
        wordcloud_image_path = generate_and_save_wordcloud(question_list)
        context["wordcloud_image_url"] = os.path.join(settings.MEDIA_URL, wordcloud_image_path)

        context["start_date"] = start_date
        context["end_date"] = end_date
        context["period_type"] = period_type

        return context

    def get_summary(self, items, period_type):
        summary = defaultdict(int)
        for item in items:
            ts = item.get('_ts')
            if ts:
                date = datetime.fromtimestamp(ts)
                if period_type == 'yearly':
                    key = date.strftime('%Y')
                elif period_type == 'quarterly':
                    quarter = (date.month - 1) // 3 + 1
                    key = f"{date.year}-Q{quarter}"
                else:  # monthly
                    key = date.strftime('%Y-%m')
                summary[key] += 1
        return summary


    def filter_items_by_date(self, items, start_date, end_date):
        start_ts = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp())
        end_ts = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp())
        return [item for item in items if start_ts <= item.get('_ts', 0) <= end_ts]

    def get_monthly_summary(self, items):
        summary = defaultdict(int)
        for item in items:
            ts = item.get('_ts')
            if ts:
                month_year = unix_timestamp_to_month(ts)
                summary[month_year] += 1
        return summary

    def get_user_use_count(self, items):
        count = defaultdict(int)
        for item in items:
            oid = item.get('oid')
            if oid:
                count[oid] += 1
        return count

    def get_question_list(self, items):
        return [item['messages'][0]['content'] for item in items if item.get('messages')]


def csv_export(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    csv_list = []
    
    # GETパラメータから期間を取得
    start_date, end_date, _ = get_date_range_and_period_type(request)

    # 期間でフィルタリングしたデータを取得
    filtered_items = ChartsView().filter_items_by_date(items, start_date, end_date)
    
    for item in filtered_items:
        messages = item.get('messages')
        category = item.get('category')

        if messages:
            question = messages[0]["content"]
            if category:
                csv_list.append([",".join(category), question])
            else:
                csv_list.append(["", question])
    
    filename = urllib.parse.quote(('data.csv'))
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
    # Add BOM to the response to help Excel recognize UTF-8 encoding
    response.write('\ufeff'.encode('utf-8'))
    writer = csv.writer(response)
    writer.writerow(['カテゴリ', '会話'])
    writer.writerows(csv_list)
    return response