from django.views.generic import TemplateView
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from plot.functions import CosmosDBClient, unix_timestamp_to_month, generate_and_save_wordcloud, unix_timestamp_to_hour
from plot.graphs import line_charts, bar_chart, user_bar_chart, pie_chart, user_active_time_chart, category_bar_chart

from dotenv import load_dotenv
import os

from collections import defaultdict

import pandas as pd
import collections

from django.http import HttpResponse
import csv
import io
import urllib.request
from django.utils.decorators import method_decorator

# .envファイルを読み込む
load_dotenv()

# # 月ごとの集計を格納する辞書
# monthly_summary = defaultdict(int)

endpoint = os.getenv("ENDPOINT")
key = os.getenv("COSMOS_KEY")
database_name = os.getenv("DB_NAME")
container_name = os.getenv("CONTAINER_NAME")

db_client = CosmosDBClient(endpoint, key, database_name, container_name)
# items = db_client.fetch_items("SELECT * FROM c")

def get_date_range_and_period_type(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    period_type = request.GET.get('period_type', 'monthly')

    if not start_date:
        start_date = (timezone.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    if not end_date:
        end_date = (timezone.now()+ timedelta(days=1)).strftime('%Y-%m-%d')

    return start_date, end_date, period_type

def fetch_items_within_date_range(start_date, end_date):
    start_ts = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp())
    end_ts = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp())
    query = f"SELECT * FROM c WHERE c._ts >= {start_ts} AND c._ts <= {end_ts}"
    return db_client.fetch_items(query)

class ChartsView(TemplateView):
    template_name = "plot.html"

    @method_decorator(settings.AUTH.login_required)
    def dispatch(self, *args, **kwargs):
        return super(ChartsView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ChartsView, self).get_context_data(**kwargs)

        start_date, end_date, period_type = get_date_range_and_period_type(self.request)
        type = self.request.GET.get('type', '')

        # 指定した期間内のデータを取得
        filtered_items = fetch_items_within_date_range(start_date, end_date)

        summary = self.get_summary(filtered_items, period_type, type)
        user_use_count = self.get_user_use_count(filtered_items)
        question_list = self.get_question_list(filtered_items)
        time_periods_count = self.get_user_active_time(filtered_items)
        category_count = self.get_category_count(filtered_items)
        # print("filtered_items",category_count)

        context["line_chart"] = line_charts(summary, period_type)
        context["bar_chart"] = bar_chart(summary, period_type)
        context["user_bar_chart"] = user_bar_chart(user_use_count)
        context["user_active_time_chart"] = user_active_time_chart(time_periods_count)
        context["category_bar_chart"] = category_bar_chart(category_count)
        
        # WordCloudの生成
        wordcloud_image_path = generate_and_save_wordcloud(question_list)
        context["wordcloud_image_url"] = os.path.join(settings.MEDIA_URL, wordcloud_image_path)

        context["start_date"] = start_date
        context["end_date"] = end_date
        context["period_type"] = period_type
        context["type"] = type  # type引数をコンテキストに追加


        return context

    def get_summary(self, items, period_type, type=None):
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

        if type == "total":
            cumulative_sum = 0
            for key in sorted(summary.keys()):
                cumulative_sum += summary[key]
                summary[key] = cumulative_sum  # 累計値に変更

        return summary

    def filter_items_by_date(self, items, start_date, end_date):
        start_ts = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp())
        end_ts = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp())
        return [item for item in items if start_ts <= item.get('_ts', 0) <= end_ts]

    # def get_monthly_summary(self, items):
    #     summary = defaultdict(int)
    #     for item in items:
    #         ts = item.get('_ts')
    #         if ts:
    #             month_year = unix_timestamp_to_month(ts)
    #             summary[month_year] += 1
    #     return summary

    def get_user_use_count(self, items):
        count = defaultdict(int)
        for item in items:
            oid = item.get('oid')
            if oid:
                count[oid] += 1
        return count
    
    def get_category_count(self, items):
        count = defaultdict(int)
        for item in items:
            categories = item.get('category', [])
            if isinstance(categories, list):
                for category in categories:
                    count[category] += 1
            else:
                count[categories] += 1
        return count
    
    def get_user_active_time(self, items):
        time_periods_count = defaultdict(int)

        early_morning_range = range(0, 9)     # 0:00〜8:59
        morning_range = range(9, 18)          # 9:00〜17:59
        evening_range = range(18, 24)         # 18:00〜23:59

        time_periods_count['0:00〜9:00'] = 0
        time_periods_count['18:00〜24:00'] = 0

        for hour in morning_range:
            time_periods_count[f'{hour}:00〜{hour+1}:00'] = 0

        for item in items:
            ts = item.get('_ts')
            if ts:
                # タイムスタンプを月および時間に変換
                dt = unix_timestamp_to_hour(ts)
                # print(dt)
                hour = dt.hour  # 時間を取得

                if hour in early_morning_range:
                    time_periods_count['0:00〜9:00'] += 1
                elif hour in morning_range:
                    time_periods_count[f'{hour}:00〜{hour+1}:00'] += 1
                elif hour in evening_range:
                    time_periods_count['18:00〜24:00'] += 1
        
        time_periods_count['18:00〜24:00'] += time_periods_count.pop('24:00〜25:00', 0)
        # print(time_periods_count)
        return time_periods_count

    def get_question_list(self, items):
        return [item['messages'][0]['content'] for item in items if item.get('messages')]
    


def csv_export(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    csv_list = []
    
    # GETパラメータから期間を取得
    start_date, end_date, _ = get_date_range_and_period_type(request)

    # 指定した期間内のデータを取得
    filtered_items = fetch_items_within_date_range(start_date, end_date)
    
    for idx, item in enumerate(filtered_items, start=1):  # インデックスを1から開始
        name = item.get('name')
        messages = item.get('messages')
        category = item.get('category')
        ts = item.get('_ts')

        if messages and ts:
            date = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
            conversation = []
            for message in messages[:20]:  # 最大20個まで取得
                role = message.get('role')
                content = message.get('content')
                if role in ['user', 'assistant']:
                    conversation.append(f"{role}: {content}")
            conversation_text = "\n".join(conversation)  # 改行で結合して1つの文字列にする
            if category:
                csv_list.append([idx, name, conversation_text, ",".join(category), date])
            else:
                csv_list.append([idx, name, conversation_text, "", date])
    
    filename = urllib.parse.quote(('data.csv'))
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
    # Add BOM to the response to help Excel recognize UTF-8 encoding
    response.write('\ufeff'.encode('utf-8'))
    writer = csv.writer(response)
    writer.writerow(['NO', '名前', '会話', 'カテゴリ', '日付'])  # ヘッダーにNOを追加
    writer.writerows(csv_list)
    return response