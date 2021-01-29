import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import betting as b
from datetime import datetime
from glob import glob
import time
import plotly.express as px

def load_data(filepath):
    df = pd.read_csv(filepath)
    df['time'] = pd.to_datetime(df['time'])
    df = df.set_index('time')
    return df

def sidebar_config():
    st.sidebar.header('Config')
    files = glob('*.csv')
    filepath = st.sidebar.selectbox("Files", options=files, index=0)

    df = load_data(filepath)
    teams = sorted(df['team'].unique().tolist())

    # matches = b.get_matches()
    selected_match = st.sidebar.multiselect('Teams', options=teams, default=[])
    # selected_match = st.sidebar.selectbox("Teams", options=matches, format_func=lambda x: " - ".join(x))
    return {'selected_match': selected_match, 'filepath': filepath}

def date_from_file(filepath):
    date = filepath.split('.csv')[0]
    return datetime.strptime(date, "%Y-%m-%d")

def sidebar_calc():
    st.sidebar.header('Bet Calculator')

    stake_a = st.sidebar.number_input('Stake A', min_value=0., value=0., step=0.01)
    odds_a = st.sidebar.number_input('Odds A', min_value=1., value=1., step=0.1)
    payout = stake_a * odds_a
    odds_b = st.sidebar.number_input('Target Odds', min_value=1., value=1., step=0.1)
    stake_b = payout / odds_b
    st.sidebar.text('Target -> ${:.2f}'.format(stake_b))

    total_stake = stake_a + stake_b

    st.sidebar.text('Total Stake: ${:.2f}'.format(total_stake))
    st.sidebar.text('Payout: ${:.2f}'.format(payout))
    st.sidebar.text('Profit: ${:.2f}'.format(payout - total_stake))

def info_to_plotly(info):
    time = ["%s:%02d" % item for item in info.index.tolist()]
    info['time'] = time
    info = info.set_index('time')
    return info

sidebar_calc()
cfg = sidebar_config()

selected_match = cfg['selected_match']

st.title("Live Feed")
stamp = st.text('Updated at: {}'.format(datetime.now()))

odds = load_data(cfg['filepath'])
info = b.game_info(odds, selected_match)

plotly_data = info_to_plotly(info)
plotly_fig = px.line(plotly_data)
plotly_fig.layout.update(showlegend=False, width=800)
chart = st.plotly_chart(plotly_fig)
recent = st.dataframe(info.tail(20), 1000, 1000)

while True:
    time.sleep(1)
    stamp.text('Updated at: {}'.format(datetime.now()))
    odds = load_data(cfg['filepath'])
    info = b.game_info(odds, selected_match)
    recent.dataframe(info.tail(20), 1000, 1000)

    # plotting the graph
    # ax = info.plot(figsize=(12, 8), grid=True)
    # ax.set_xticks(range(len(info.index)));
    # ax.set_xticklabels(["%s:%02d" % item for item in info.index.tolist()], rotation=90)
    # chart.pyplot(ax.get_figure())
    plotly_data = info_to_plotly(info)
    plotly_fig = px.line(plotly_data)
    plotly_fig.layout.update(showlegend=False, width=800)
    chart.plotly_chart(plotly_fig)
