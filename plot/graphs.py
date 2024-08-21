import plotly.graph_objects as go

def line_charts(monthly_data):
    months = list(monthly_data.keys())
    values = list(monthly_data.values())

    sorted_months_values = sorted(zip(months, values))
    months, values = zip(*sorted_months_values)

    print("months", months)
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
