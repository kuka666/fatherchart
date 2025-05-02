from flask import Flask, render_template_string
import pandas as pd
import plotly.graph_objs as go
import plotly.io as pio
import numpy as np

app = Flask(__name__)

@app.route('/')
def index():
    # Загрузка данных
    tenge_df = pd.read_csv("Официальные (рыночные) курсы валют (1).csv")
    oil_df = pd.read_csv("RBRTEm.csv")

    # Подготовка данных
    tenge_df['Date'] = pd.to_datetime(tenge_df['Date'], format='%d.%m.%Y')
    tenge_df = tenge_df.set_index('Date').resample('M').mean()

    oil_df.columns = ['Date', 'Brent_Price']
    oil_df['Date'] = pd.to_datetime(oil_df['Date']) + pd.offsets.MonthEnd(0)
    oil_df = oil_df.set_index('Date')

    df = pd.merge(tenge_df, oil_df, left_index=True, right_index=True)

    # Основной график: курс и нефть
    trace1 = go.Scatter(x=df.index, y=df['USD'], name='USD/KZT', yaxis='y1')
    trace2 = go.Scatter(x=df.index, y=df['Brent_Price'], name='Brent Price (USD)', yaxis='y2')
    layout1 = go.Layout(
        title='Зависимость курса тенге от цены нефти',
        xaxis=dict(title='Дата'),
        yaxis=dict(title='Курс USD/KZT', side='left'),
        yaxis2=dict(title='Цена Brent (USD)', overlaying='y', side='right'),
        legend=dict(x=0, y=1.1, orientation="h")
    )
    fig1 = go.Figure(data=[trace1, trace2], layout=layout1)
    graph1 = pio.to_html(fig1, full_html=False)

    # Корреляция
    df['USD_Returns'] = np.log(df['USD'] / df['USD'].shift(1))
    df['Oil_Returns'] = np.log(df['Brent_Price'] / df['Brent_Price'].shift(1))
    corr_matrix = df[['USD', 'Brent_Price', 'USD_Returns', 'Oil_Returns']].corr()
    heatmap = go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.index,
        colorscale='RdBu',
        zmin=-1, zmax=1,
        colorbar=dict(title="Корреляция")
    )
    layout2 = go.Layout(title="Корреляция между показателями")
    fig2 = go.Figure(data=[heatmap], layout=layout2)
    graph2 = pio.to_html(fig2, full_html=False)

    # Месячная доходность
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=df.index, y=df['USD_Returns'], name='Доходность USD/KZT', line=dict(color='red')))
    fig3.add_trace(go.Scatter(x=df.index, y=df['Oil_Returns'], name='Доходность Brent', line=dict(color='blue')))
    fig3.update_layout(title="Месячная логарифмическая доходность", xaxis_title="Дата", yaxis_title="Доходность")
    graph3 = pio.to_html(fig3, full_html=False)

    # HTML шаблон
    html = '''
    <html>
    <head>
        <title>График: нефть и тенге</title>
    </head>
    <body style="font-family:Arial;padding:20px;background:#f4f4f4;">
        <h1>Арипжанов Галымжан</h1>
        <h2>Интерактивный график: курс тенге и нефть</h2>
        {{ graph1|safe }}
        <h2>Корреляция</h2>
        {{ graph2|safe }}
        <h2>Месячная доходность</h2>
        {{ graph3|safe }}
    </body>
    </html>
    '''

    return render_template_string(html, graph1=graph1, graph2=graph2, graph3=graph3)

if __name__ == '__main__':
    app.run(debug=True)
