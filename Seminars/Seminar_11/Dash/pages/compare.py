import dash
from dash import Dash, html, dcc, Input, Output, callback
import pandas as pd
from urllib.request import urlopen
import json
import plotly.express as px

dash.register_page(__name__)

df = pd.read_csv("county_statistics.csv")
df = df[~pd.isnull(df.lat)]
df = df[~pd.isnull(df.percentage16_Donald_Trump)]

df_sample = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/laucnty16.csv')
df_sample['State FIPS Code'] = df_sample['State FIPS Code'].apply(lambda x: str(x).zfill(2))
df_sample['County FIPS Code'] = df_sample['County FIPS Code'].apply(lambda x: str(x).zfill(3))
df_sample['FIPS'] = df_sample['State FIPS Code'] + df_sample['County FIPS Code']

def replacing_words(x):
    x = x.split(",")[0]
    samples = [" County", "/town", " Parish", "/city"]
    for s in samples:
        x = x.replace(s, "")
    return x

def changing_state(x):
    x = x.split(", ")[-1]
    if x == 'District of Columbia':
        x = "DC"
    return x

df_sample["county"] = df_sample["County Name/State Abbreviation"].apply(lambda x: replacing_words(x))
df_sample["state"] = df_sample["County Name/State Abbreviation"].apply(lambda x: changing_state(x))
df_fips = pd.merge(df, df_sample[["county", "state", "FIPS"]], on=["county", "state"], how='left')

perc_data = pd.melt(df_fips[["county", "state", "White", "Black", "Hispanic", "Asian", "Pacific", "Native"]], id_vars=["county", "state"], var_name="Race", value_name="Perc")

fig_1 = px.pie(data_frame=perc_data, values="Perc", names="Race")
fig_1.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig_2 = px.pie(data_frame=perc_data, values="Perc", names="Race")
fig_2.update_layout(margin={"r":0,"t":0,"l":0,"b":0})


layout = html.Div(children=[
    html.Div([
        html.Div([
            dcc.Markdown('Select State'),
            dcc.Dropdown(df_fips.state.unique(), df_fips.state[0], id='state_1_dropdown'),
            dcc.Markdown('Select County'),
            dcc.Dropdown(df_fips.county.unique(), df_fips.county[0], id='county_1_dropdown'),
        ]),
        html.Div([
            dcc.Markdown('Select State'),
            dcc.Dropdown(df_fips.state.unique(), df_fips.state[0], id='state_2_dropdown'),
            dcc.Markdown('Select County'),
            dcc.Dropdown(df_fips.county.unique(), df_fips.county[0], id='county_2_dropdown'),
        ]),
    ], style={'columnCount': 2, 'align': 'center'}),

    html.Div([
        html.Div([
            dcc.Markdown('Race distribution'),
            dcc.Graph(
                id='Race_1_pie',
                figure=fig_1,
            ),
        ]),
        html.Div([
            dcc.Markdown('Race distribution'),
            dcc.Graph(
                id='Race_2_pie',
                figure=fig_2,
            ),
        ])
    ], style={'columnCount': 2, 'align': 'center'})
])

@callback(
    Output("county_1_dropdown", 'options'),
    Input("state_1_dropdown", "value")
)
def update_counties_1(val):
    res = df_fips[df_fips.state == val].county.unique()
    return res

@callback(
    Output("county_2_dropdown", 'options'),
    Input("state_2_dropdown", "value")
)
def update_counties_2(val):
    res = df_fips[df_fips.state == val].county.unique()
    return res

@callback(
    Output("Race_1_pie", 'figure'),
    Input("county_1_dropdown", "value"),
    Input("state_1_dropdown", "value")
)
def update_pue_1(county, state):
    fig_1 = px.pie(data_frame=perc_data[(perc_data.county == county) & (perc_data.state == state)], values="Perc", names="Race")
    fig_1.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig_1

@callback(
    Output("Race_2_pie", 'figure'),
    Input("county_2_dropdown", "value"),
    Input("state_2_dropdown", "value")
)
def update_pue_2(county, state):
    fig_2 = px.pie(data_frame=perc_data[(perc_data.county == county) & (perc_data.state == state)], values="Perc", names="Race")
    fig_2.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig_2