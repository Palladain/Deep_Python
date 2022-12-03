from dash import Dash, html, dcc, Input, Output, callback
import pandas as pd
from urllib.request import urlopen
import json
import plotly.express as px
import dash

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

with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)

# Отрисовка изначальных карт

fig = px.choropleth(df_fips, geojson=counties, locations='FIPS', color='White',
                           color_continuous_scale="Viridis",
                           range_color=(0, 100),
                            scope="usa",
                            fitbounds='locations',
                           hover_data=["state", "county", "percentage16_Donald_Trump"]
                          )
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

perc_data = pd.melt(df_fips[["county", "state", "White", "Black", "Hispanic", "Asian", "Pacific", "Native"]], id_vars=["county", "state"], var_name="Race", value_name="Perc")
walk_data = pd.melt(df_fips[["county", "state", 'Drive', 'Carpool', 'Transit', 'Walk', 'OtherTransp', 'WorkAtHome']], id_vars=["county", "state"], var_name="Walk", value_name="Perc")
work_data = pd.melt(df_fips[["county", "state", 'PrivateWork', 'PublicWork', 'SelfEmployed', 'FamilyWork', 'Unemployment']], id_vars=["county", "state"], var_name="Work", value_name="Perc")

fig_1 = px.pie(data_frame=perc_data, values="Perc", names="Race")
fig_1.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig_2 = px.pie(data_frame=walk_data, values="Perc", names="Walk")
fig_2.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig_3 = px.pie(data_frame=work_data, values="Perc", names="Work")
fig_3.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

layout = html.Div(children=[
    html.Div([
        dcc.Markdown('Select State'),
        dcc.Dropdown(df_fips.state.unique(), df_fips.state[0], id='state_dropdown'),
    ]),

    dcc.Graph(
        id='US_map',
        figure=fig,
        clickData={'points': [{'customdata': ['SC', 'Horry']}]}
    ),

    html.Div([
        html.Div([
            dcc.Markdown('Race distribution'),
            dcc.Graph(
                id='Race_pie',
                figure=fig_1,
            ),
        ]),
        html.Div([
            dcc.Markdown('Transport distribution'),
            dcc.Graph(
                id='Walk_pie',
                figure=fig_2,
            ),
        ]),
        html.Div([
            dcc.Markdown('Work distribution'),
            dcc.Graph(
                id='Work_pie',
                figure=fig_3,
            ),
        ])
    ], style={'columnCount': 3, 'align': 'center'})
])


@callback(
    Output('US_map', 'figure'),
    Input('state_dropdown', 'value')
)
def update_map(state):
    fig = px.choropleth(df_fips[df_fips.state == state], geojson=counties, locations='FIPS', color='percentage16_Donald_Trump',
                        color_continuous_scale="Viridis",
                        range_color=(0, 1),
                        scope="usa",
                        fitbounds='locations',
                        hover_data=["state", "county", "percentage16_Donald_Trump"]
                        )
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig


@callback(
    Output('Race_pie', 'figure'),
    Input('US_map', 'clickData')
)
def display_click_data_race(clickData):
    state = clickData["points"][0]["customdata"][0]
    county = clickData["points"][0]["customdata"][1]
    fig_1 = px.pie(data_frame=perc_data[(perc_data.county == county) & (perc_data.state == state)], values="Perc", names="Race")
    fig_1.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig_1

@callback(
    Output('Walk_pie', 'figure'),
    Input('US_map', 'clickData')
)
def display_click_data_walk(clickData):
    state = clickData["points"][0]["customdata"][0]
    county = clickData["points"][0]["customdata"][1]
    fig_2 = px.pie(data_frame=walk_data[(walk_data.county == county) & (walk_data.state == state)], values="Perc", names="Walk")
    fig_2.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig_2

@callback(
    Output('Work_pie', 'figure'),
    Input('US_map', 'clickData')
)
def display_click_data_work(clickData):
    state = clickData["points"][0]["customdata"][0]
    county = clickData["points"][0]["customdata"][1]
    fig_3 = px.pie(data_frame=work_data[(work_data.county == county) & (work_data.state == state)], values="Perc", names="Work")
    fig_3.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig_3