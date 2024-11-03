import plotly.graph_objects as go

def line_charts(data, period_type):
    x = list(data.keys())
    y = list(data.values())

    fig = go.Figure(data=go.Scatter(x=x, y=y, mode='lines+markers'))
    
    title = f"使用回数 ({get_period_type_label(period_type)})"
    fig.update_layout(
        title=title,
        xaxis_title=get_period_type_label(period_type),
        yaxis_title="使用回数",
        height=500,  # グラフの高さを500ピクセルに設定
        margin=dict(l=50, r=50, t=50, b=50),  # マージンを調整
        xaxis=dict(
            tickformat=get_tick_format(period_type),
            tickmode='array',
            tickvals=x
        )
    )

    return fig.to_html(full_html=False, config={'responsive': True})

def bar_chart(data, period_type):
    x = list(data.keys())
    y = list(data.values())

    fig = go.Figure(data=go.Bar(x=x, y=y))
    
    title = f"使用回数 ({get_period_type_label(period_type)})"
    fig.update_layout(
        title=title,
        xaxis_title=get_period_type_label(period_type),
        yaxis_title="使用回数",
        height=500,  # グラフの高さを500ピクセルに設定
        margin=dict(l=50, r=50, t=50, b=50),  # マージンを調整
        xaxis=dict(
            tickformat=get_tick_format(period_type),
            tickmode='array',
            tickvals=x
        )
    )

    return fig.to_html(full_html=False, config={'responsive': True})

def get_tick_format(period_type):
    if period_type == 'yearly':
        return '%Y'
    elif period_type == 'quarterly':
        return '%Y-Q%q'
    else:  # monthly
        return '%Y-%m'

def get_period_type_label(period_type):
    if period_type == 'yearly':
        return '年'
    elif period_type == 'quarterly':
        return '四半期'
    else:
        return '月'

def group_bar_chart(user_data):
    groups = list(user_data.keys())
    values = list(user_data.values())

    sorted_groups_values = sorted(zip(groups, values), key=lambda x: x[1], reverse=True)
    if not sorted_groups_values:  # 空の場合の処理を追加
        return "データがありません"
    groups, values = zip(*sorted_groups_values)

    fig = go.Figure()
    fig.add_trace(go.Bar(x=groups, y=values, name='Data by User'))

    fig.update_layout(
        title="Data by Group",
        xaxis_title="Groups",
        yaxis_title="Count",
        autosize=True,
        height=400,  # 高さを固定
        xaxis=dict(
            tickmode='array',
            tickvals=groups,
            ticktext=groups,
            tickangle=-45
        )
    )
    return fig.to_html(full_html=False, include_plotlyjs='cdn')

def user_bar_chart(user_data):
    users = list(user_data.keys())
    values = list(user_data.values())

    sorted_users_values = sorted(zip(users, values), key=lambda x: x[1], reverse=True)
    if not sorted_users_values:
        return "ユーザーのデータがありません"
    users, values = zip(*sorted_users_values)

    fig = go.Figure()
    fig.add_trace(go.Bar(x=users, y=values, name='Data by User'))

    fig.update_layout(
        title="Data by User",
        xaxis_title="Users",
        yaxis_title="Count",
        autosize=True,
        height=400,  # 高さを固定
        xaxis=dict(
            tickmode='array',
            tickvals=users,
            ticktext=users,
            tickangle=-45
        )
    )
    return fig.to_html(full_html=False, include_plotlyjs='cdn')


# def category_bar_chart(user_data):
#     users = list(user_data.keys())
#     values = list(user_data.values())

#     sorted_users_values = sorted(zip(users, values), key=lambda x: x[1], reverse=True)
#     if not sorted_users_values:
#         return "ユーザーのデータがありません"
#     users, values = zip(*sorted_users_values)

#     fig = go.Figure()
#     fig.add_trace(go.Bar(x=users, y=values, name='category by User'))

#     fig.update_layout(
#         title="category by User",
#         xaxis_title="category",
#         yaxis_title="Count",
#         autosize=True,
#         height=400,  # 高さを固定
#         xaxis=dict(
#             tickmode='array',
#             tickvals=users,
#             ticktext=users,
#             tickangle=-45
#         )
#     )
#     return fig.to_html(full_html=False, include_plotlyjs='cdn')

def category_pie_chart(user_data):
    # "unknown" カテゴリを除外し、その件数を計算
    unknown_count = user_data.pop('Unknown', 0)

    # unknownを除外した後のユーザーとカウントのリストを取得
    users = list(user_data.keys())
    values = list(user_data.values())

    # データが空の場合の処理
    if not users:
        return "ユーザーのデータがありません"

    # カテゴリと値を並べ替え
    sorted_users_values = sorted(zip(users, values), key=lambda x: x[1], reverse=True)
    users, values = zip(*sorted_users_values)

    # グラフの作成
    fig = go.Figure()
    fig = go.Figure(data=[go.Pie(labels=users, values=values,direction='clockwise')])

    fig.update_layout(
        autosize=True,
        height=400,  # 高さを固定
        margin=dict(l=20, r=20, t=50, b=50),
    )
    # グラフのHTML表現を取得
    graph_html = fig.to_html(full_html=False, include_plotlyjs='cdn')

    # unknownの件数をメッセージとして追加
    unknown_message = f"<p>unknown の件数: {unknown_count}</p>" if unknown_count > 0 else ""

    # unknownメッセージとグラフを連結して返す
    return unknown_message + graph_html



def user_active_time_chart(time_periods_count):
    # 全てのカウントがゼロかを確認
    if all(count == 0 for count in time_periods_count.values()):
        return "ユーザーのデータはありません"
    # 時間帯の順序を保つためにソート
    sorted_time_periods = sorted(time_periods_count.items(), key=lambda x: (int(x[0].split(':')[0]), int(x[0].split('〜')[1].split(':')[0])))

    # カウント結果をラベルと値に分ける
    labels = tuple([item[0] for item in sorted_time_periods])
    values = tuple([item[1] for item in sorted_time_periods])

    # 時間帯ごとの利用数を棒グラフとして作成
    fig = go.Figure()
    fig.add_trace(go.Bar(x=labels, y=values, name='Usage Count'))

    fig.update_layout(
        title="利用時間ごとの利用数",
        xaxis_title="時間帯",
        yaxis_title="利用数",
        autosize=True,
        height=400,
        xaxis=dict(
            tickmode='array',
            tickvals=labels,
            ticktext=labels,
            tickangle=-45
        )
    )
    return fig.to_html(full_html=False, include_plotlyjs='cdn')



def pie_chart(user_data):
    labels = list(user_data.keys())
    values = list(user_data.values())

    fig = go.Figure(data=[go.Pie(labels=labels, values=values)])

    fig.update_layout(
        title="Data Distribution",
        height=400,
        margin=dict(l=50, r=50, t=50, b=50)
    )
    return fig.to_html(full_html=False, include_plotlyjs='cdn')