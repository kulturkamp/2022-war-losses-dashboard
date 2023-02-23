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

st.set_page_config(page_title='russian military loses', layout='wide')

st.markdown("<h1 style='text-align: center; color: #8c785d;'>rUSSIAN INVASION OF UKRAINE</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; color: #8c785d;'>Day {}</h1>".format(day_latest), unsafe_allow_html=True)

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

#print(st.columns(len(cols)//2))



with st.container():
    st.markdown("<h3 style='text-align: center; color: #8c785d;'>russian loses by military unit</h1>", unsafe_allow_html=True)
    _, col221, _ = st.columns([3, 1, 3])
    with col221:
        attribute_ = st.selectbox(
            label='Select unit', 
            options=cols, 
            index=2
        )

    fig = make_subplots(2, 1, subplot_titles=['Total losses', 'Daily losses'], shared_xaxes=True, vertical_spacing = 0.1)
    fig.add_trace(
        go.Scatter(
            x=df_equipment['date'],
            y=df_equipment[attribute_],
            mode='lines',
            hovertemplate='%{x}<br />lost to this date: %{y} <extra></extra>',
            marker_color=clrs.qualitative.Antique[9]
            
        ),
        row=1, 
        col=1
    )
    fig.add_trace(
        go.Bar(
            x=df_equipment_daily['date'], 
            y=df_equipment_daily[attribute_],
            marker_color=clrs.qualitative.Antique[9],
            hovertemplate='%{x}<br />lost: %{y} <extra></extra>',
            # text=df_equipment_daily[attribute_]
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
            size=15,
            family='Aerial Black'
        ),
        showarrow=False,    
    )
    fig.update_layout(
        # paper_bgcolor='rgba(0,0,0,0)',
        # plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=37, label='last month', step='day', stepmode='backward'),
                    dict(count=7, label='last week', step='day', stepmode='backward'),
                    dict(label='all time', step='all')
                ]),
                bgcolor=clrs.qualitative.Antique[9],
                font=dict(
                    family='Aerial Black',
                    color='white',
                )
            ),
            showgrid=False,
            tickfont=dict(
                family='Aerial Black',
            )
        ),
        yaxis=dict(
            fixedrange=True,
            tickfont=dict(
                family='Aerial Black',
            )
        ),
        yaxis2=dict(
            fixedrange=True,
            tickfont=dict(
                family='Aerial Black',
            )
        ),
        xaxis2_showgrid=False,
        xaxis2_rangeslider_visible=True,
        xaxis2_rangeslider_thickness=0.05,
        xaxis2_type='date',
        showlegend=False,
        height=850         
    )
    fig.update_annotations(
        font=dict(
            family='Aerial Black'
        )
    )
    fig.update_xaxes(matches='x')
    st.plotly_chart(fig, use_container_width=True)

with st.container():
    st.markdown("<h3 style='text-align: center; color: #8c785d;'>russian loses of personnel</h1>", unsafe_allow_html=True)
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=df_personnel_daily['date'],
            y=df_personnel_daily['personnel'],
            marker_color=clrs.qualitative.Antique[9],
            hovertemplate='%{x}<br />lost: %{y} <extra></extra>'
        )
    )   
    fig.add_trace(
        go.Bar(
            x=df_personnel_daily['date'],
            y=df_personnel_daily['POW'],
            marker_color=clrs.qualitative.Set2[6],
            hovertemplate='%{x}<br />captured: %{y} <extra></extra>'
        )
    )
    fig.update_layout(
        barmode='stack',
        # paper_bgcolor='rgba(0,0,0,0)',
        # plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=31, label='last month', step='day', stepmode='backward'),
                    dict(count=7, label='last week', step='day', stepmode='backward'),
                    dict(label='all time', step='all')
                ]),
                bgcolor=clrs.qualitative.Antique[9],
                font=dict(
                    family='Aerial Black',
                    color='white'
                )
            ),
            rangeslider=dict(
                visible=True,
                thickness=0.05
            ),
            tickfont=dict(
                family='Aerial Black',
            ),
            type='date'
        ),
        yaxis=dict(
            fixedrange=True,
            tickfont=dict(
                family='Aerial Black',
            )
        ),
        showlegend=False,
        height=850         
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown(
        '''
        Also check out [Ukraine Air-alerts dashboard](https://kulturkamp-air-alerts-dashboard-air-alerts-dashboard-24cjge.streamlit.app/)
        '''
    )
    with st.container():
        col311, _ = st.columns([2, 3])
        with col311:
            with st.expander('Credits and data sources'):
                st.markdown(
                    '''
                    - Thanks to [Petro Ivaniuk](https://github.com/PetroIvaniuk) for data and inspiration
                    - [russian loses dataset on github](https://github.com/PetroIvaniuk/2022-Ukraine-Russia-War-Dataset) (json, updated daily)
                    - [russian loses dataset on kaggle](https://www.kaggle.com/datasets/piterfm/2022-ukraine-russian-war) (csv, updated daily)
                    '''
                )
        
        col321, _ = st.columns([2, 3])
        with col321:
            with st.expander('Acronyms'):
                st.markdown(
                    '''
                    - MRL - Multiple Rocket Launcher
                    - APC - Armored Personnel Carrier
                    '''
                )