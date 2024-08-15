from azure.cosmos import CosmosClient, exceptions
from datetime import datetime

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