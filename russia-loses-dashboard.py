from pyparsing import col
import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.colors as clrs

url_equipment = 'https://raw.githubusercontent.com/PetroIvaniuk/2022-Ukraine-Russia-War-Dataset/main/data/russia_losses_equipment.json'
url_personnel = 'https://raw.githubusercontent.com/PetroIvaniuk/2022-Ukraine-Russia-War-Dataset/main/data/russia_losses_personnel.json'

response_equipment = requests.get(url_equipment)
response_personnel = requests.get(url_personnel)

df_equipment = pd.DataFrame(response_equipment.json())
df_personnel = pd.DataFrame(response_personnel.json())

df_equipment.date = pd.to_datetime(df_equipment.date)
df_equipment.day = df_equipment.day.astype(int)

to_sum = ['military auto', 'fuel tank', 'vehicles and fuel tanks']
to_drop = to_sum + ['greatest losses direction', 'mobile SRBM system']
df_equipment['military and supply vehicles'] = df_equipment[to_sum].sum(axis=1)
df_equipment = df_equipment.drop(to_drop, axis=1)

df_equipment_daily = df_equipment.copy().set_index(['date', 'day'])
df_equipment_daily = df_equipment_daily.diff().fillna(df_equipment_daily).fillna(0).reset_index()

df_equipment_sum = df_equipment_daily.sum()

df_equipment_last_day = df_equipment_daily.iloc[-1].copy()

df_personnel = df_personnel.drop(['personnel*'], axis=1)
df_personnel.date = pd.to_datetime(df_personnel.date)

df_personnel_daily = df_personnel.copy().set_index(['date', 'day'])
df_personnel_daily = df_personnel_daily.diff().fillna(df_personnel_daily).reset_index()

df_personnel_last_day = df_personnel_daily.iloc[-1].copy()

good_russians = int(df_personnel_daily.sum()['personnel'])

cols = df_equipment_daily.columns[2:]

date_latest = df_equipment_daily.iloc[-1]['date']
day_latest = df_equipment_daily.iloc[-1]['day']

st.set_page_config(page_title='russian military losses', layout="wide")

st.markdown("<h1 style='text-align: center; color: #FF9900;'>rUSSIAN INVASION OF UKRAINE</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; color: #FF9900;'>Day {}</h1>".format(day_latest), unsafe_allow_html=True)

with st.container():
    _, col111, col112, _ = st.columns([2, 1, 1, 2])

    with col111:
        col111.metric('Total good russians', good_russians, int(df_personnel_last_day['personnel']))

    with col112:
        col112.metric('Total military units lost', int(df_equipment_sum.drop('day').sum()), int(df_equipment_last_day.iloc[2:].sum()))

    


with st.container():
    page_cols = [*st.columns(len(cols)//2),
                 *st.columns(len(cols)//2)]


    for i, col in enumerate(page_cols):
        col.metric(cols[i], int(df_equipment_sum[cols[i]]), int(df_equipment_last_day[cols[i]]))

print(st.columns(len(cols)//2))



with st.container():
    st.markdown("<h3 style='text-align: center; color: #FF9900;'>russian loses by military unit</h1>", unsafe_allow_html=True)
    _, col221, _ = st.columns([3, 1, 3])
    with col221:
        attribute_ = st.selectbox(
            label='Select unit', 
            options=cols, 
            index=6
        )

    fig = make_subplots(2, 1, subplot_titles=['Total losses', 'Daily losses'], shared_xaxes=True, vertical_spacing = 0.1)
    fig.add_trace(
        go.Scatter(
            x=df_equipment['date'],
            y=df_equipment[attribute_],
            mode='lines+markers',
            hovertemplate='%{x}<br />lost to this date: %{y} <extra></extra>',
            marker_color=clrs.qualitative.T10[1]
            
        ),
        row=1, 
        col=1
    )
    fig.add_trace(
        go.Bar(
            x=df_equipment_daily['date'], 
            y=df_equipment_daily[attribute_],
            marker_color=clrs.qualitative.G10[1],
            hovertemplate='%{x}<br />lost: %{y} <extra></extra>',
            text=df_equipment_daily[attribute_]
        ),
        row=2,
        col=1
    )
    fig.add_annotation(
    text='*Use slider above to slice by date',
    xref='paper',
    yref='paper',
    x=0.05,
    y=-0.2,
    font=dict(
        size=15
    ),
    showarrow=False,
    
)

    fig.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=37, label='last month', step='day', stepmode='backward'),
                    dict(count=13, label='last week', step='day', stepmode='backward'),
                    dict(label='all time', step='all')
                ]),
                bgcolor=clrs.qualitative.G10[2]
            )
        ),
        xaxis2_rangeslider_visible=True,
        xaxis2_rangeslider_thickness=0.05,
        xaxis2_type='date',
        showlegend=False,
        height=850         
    )
    fig.update_xaxes(matches='x')
    st.plotly_chart(fig, use_container_width=True)