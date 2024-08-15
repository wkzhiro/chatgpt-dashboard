from django.views.generic import TemplateView  # ❶

from plot.functions import CosmosDBClient, unix_timestamp_to_month
from plot.graphs import line_charts, bar_chart

from dotenv import load_dotenv
import os

from collections import defaultdict

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

class ChartsView(TemplateView):  # ❶
    template_name = "plot.html"

    def get_context_data(self, **kwargs):
        context = super(ChartsView, self).get_context_data(**kwargs)
        context["line_chart"] = line_charts(monthly_summary)
        context["bar_chart"] = bar_chart(monthly_summary)
        return context