import plotly.graph_objects as go

def line_charts(monthly_data):
    # 月ごとの集計データを x (月) と y (値) に分解
    months = list(monthly_data.keys())
    values = list(monthly_data.values())

    # 月ごとにソート
    sorted_months_values = sorted(zip(months, values))
    months, values = zip(*sorted_months_values)

    print("months",months)
    # Plotly グラフの作成
    fig = go.Figure(
        go.Scatter(x=months, y=values, mode='lines+markers', name='Monthly Data'),
        layout=go.Layout(
            title="Monthly Data Overview",
            xaxis_title="Month",
            yaxis_title="Count",
            width=800, height=400,
            xaxis=dict(
                tickmode='array',
                tickvals=months,
                ticktext=months,  # x軸のラベルとして月のみを表示
                tickangle=-45    # 月ごとのラベルが重ならないように角度を調整
            )
        )
    )
    return fig.to_html(include_plotlyjs=False)

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
        width=800, height=400,
        xaxis=dict(
            tickmode='array',
            tickvals=months,
            ticktext=months,
            tickangle=-45
        )
    )
    return fig.to_html(include_plotlyjs=False)