import plotly.graph_objects as go

def line_charts(monthly_data):
    months = list(monthly_data.keys())
    values = list(monthly_data.values())

    sorted_months_values = sorted(zip(months, values))
    months, values = zip(*sorted_months_values)

    # Plotly グラフの作成
    fig = go.Figure(
        go.Scatter(x=months, y=values, mode='lines+markers', name='Monthly Data'),
        layout=go.Layout(
            title="Monthly Data Overview",
            xaxis_title="Month",
            yaxis_title="Count",
            autosize=True,
            height=400,  # 高さを固定
            xaxis=dict(
                tickmode='array',
                tickvals=months,
                ticktext=months,
                tickangle=-45
            )
        )
    )
    return fig.to_html(full_html=False, include_plotlyjs='cdn')

def bar_chart(monthly_data):
    months = list(monthly_data.keys())
    values = list(monthly_data.values())

    sorted_months_values = sorted(zip(months, values))
    months, values = zip(*sorted_months_values)

    fig = go.Figure()
    fig.add_trace(go.Bar(x=months, y=values, name='Monthly Data'))

    fig.update_layout(
        title="Monthly Data Overview",
        xaxis_title="Month",
        yaxis_title="Count",
        autosize=True,
        height=400,  # 高さを固定
        xaxis=dict(
            tickmode='array',
            tickvals=months,
            ticktext=months,
            tickangle=-45
        )
    )
    return fig.to_html(full_html=False, include_plotlyjs='cdn')

def user_bar_chart(user_data):
    users = list(user_data.keys())
    values = list(user_data.values())

    sorted_users_values = sorted(zip(users, values), key=lambda x: x[1], reverse=True)
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


def user_active_time_chart(time_periods_count):
    # 時間帯の順序を保つためにソート
    sorted_time_periods = sorted(time_periods_count.items(), key=lambda x: (int(x[0].split(':')[0]), int(x[0].split('〜')[1].split(':')[0])))

    # カウント結果をラベルと値に分ける
    labels = tuple([item[0] for item in sorted_time_periods])
    values = tuple([item[1] for item in sorted_time_periods])
    # labels と values をタプルにまとめる
    # print("values",values)
    # print("labels",labels)
    # print("values",len(values))
    # print("labels",len(labels))

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