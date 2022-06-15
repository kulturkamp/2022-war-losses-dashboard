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
to_drop = to_sum + ['greatest losses direction']
df_equipment['military and supply vehicles'] = df_equipment[to_sum].sum(axis=1)
df_equipment = df_equipment.drop(to_drop, axis=1)

df_equipment_daily = df_equipment.copy().set_index(['date', 'day'])
df_equipment_daily = df_equipment_daily.diff().fillna(df_equipment_daily).fillna(0).reset_index()



fig = make_subplots(2, 1, subplot_titles=['Total losses', 'Daily losses'], shared_xaxes=True)
fig.add_trace(
    go.Scatter(
        x=df_equipment['date'],
        y=df_equipment['tank'],
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
        y=df_equipment_daily['tank'],
        marker_color=clrs.qualitative.G10[1],
        hovertemplate='%{x}<br />lost: %{y} <extra></extra>',
        text=df_equipment_daily['tank']
    ),
    row=2,
    col=1
)
fig.update_layout(
    xaxis=dict(
        rangeselector=dict(
            buttons=list([
                dict(count=1, label='last month', step='month', stepmode='backward'),
                dict(count=7, label='last week', step='day', stepmode='backward'),
                dict(label='all time', step='all')
            ])
        )
    ),
    xaxis2_rangeslider_visible=True,
    xaxis2_rangeslider_thickness=0.05,
    xaxis2_type="date",
    paper_bgcolor='white',
    showlegend=False,
    height=1000         
)


st.plotly_chart(fig, use_container_width=True)