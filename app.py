import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import datetime
from dash.exceptions import PreventUpdate

vac = pd.read_csv(
    'https://data.cdc.gov/api/views/unsk-b7fc/rows.csv?accessType=DOWNLOAD')
vac_state = vac[['Date', 'Location',
                 'Administered_Dose1_Pop_Pct', 'Series_Complete_Pop_Pct']]
vac_state['Date'] = pd.to_datetime(vac_state['Date'])
vac_state['Date_num'] = (
    vac_state['Date'] - vac_state['Date'].values[-1]).map(lambda x: x.days)

vac_2 = pd.read_csv(
    'https://data.cdc.gov/api/views/8xkx-amqh/rows.csv?accessType=DOWNLOAD')
vac_county = vac_2[['Date', 'FIPS', 'Recip_County', 'Recip_State',
                    'Administered_Dose1_Pop_Pct', 'Series_Complete_Pop_Pct']]
vac_county['Date'] = pd.to_datetime(vac_county['Date'])
vac_county['Date_num'] = (
    vac_county['Date'] - vac_county['Date'].values[-1]).map(lambda x: x.days)

states = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI',
          'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI',
          'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC',
          'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT',
          'VT', 'VA', 'WA', 'WV', 'WI', 'WY']

tran = pd.read_csv(
    'https://data.cdc.gov/api/views/8396-v7yb/rows.csv?accessType=DOWNLOAD', na_values='suppressed')
tran.dropna(inplace=True)
us_state_to_abbrev = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
    "District of Columbia": "DC",
    "American Samoa": "AS",
    "Guam": "GU",
    "Northern Mariana Islands": "MP",
    "Puerto Rico": "PR",
    "United States Minor Outlying Islands": "UM",
    "U.S. Virgin Islands": "VI",
}

tran['state'] = tran['state_name'].map(us_state_to_abbrev)
tran['cases_per_100K_7_day_count_change'] = tran.cases_per_100K_7_day_count_change.str.replace(
    ',', '').astype('float64')
tran['report_date'] = pd.to_datetime(tran['report_date'])
tran['Date_num'] = (tran['report_date'] -
                    tran['report_date'].values[0]).map(lambda x: x.days)

from urllib.request import urlopen
import json
with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)

app = dash.Dash(__name__)

app.layout = html.Div([
    # title
    html.H1(
        children='US COVID-19 DATA TRACKER',
        style={'textAlign': 'center', 'color': '#111111'}),
    # first row
    html.Div([
        html.Div([
            dcc.RadioItems(
                id='full-vac',
                options=[{'label': i, 'value': i}
                         for i in ['Fully Vaccinated', 'At Least One Dose']],
                value='Linear',
                labelStyle={'display': 'inline-block'}
            )], style={'width': '100%', 'text-align': 'center', 'display': 'inline-block'}),
        dcc.Graph(id='graph-state'),
        html.Div(id='us-date'),
        dcc.Slider(
            id='year_slider',
            min=vac_state['Date_num'].min(),
            max=vac_state['Date_num'].max(),
            value=vac_state['Date_num'].max()
        )
    ]),

    html.Div([
        html.Div([
            dcc.Dropdown(
                id='chose-state',
                options=[{'label': i, 'value': i} for i in states],
                value='NY'
            ),
            dcc.RadioItems(
                id='county-full-vac',
                options=[{'label': i, 'value': i}
                         for i in ['Fully Vaccinated', 'At Least One Dose']],
                value='Linear',
                labelStyle={'display': 'inline-block'}
            )], style={'width': '100%', 'text-align': 'center', 'display': 'inline-block'}),
        html.Div([
            dcc.Graph(id='graph-county')
        ]),
        html.Div(id='county-date'),
        html.Div([
            dcc.Slider(
                id='county-year_slider'
            )], style={'display': 'inline-block', 'width': '100%'})
    ]),

    html.Div([
        html.Div([
            dcc.Dropdown(
                id='chose-county'
            ),
            dcc.RangeSlider(
                id='range-slider'
            )], style={'width': '100%', 'text-align': 'center', 'display': 'inline-block'}),
        html.Div(id='range-date'),
        html.Div("Note: You may encounter callback error at the first time you open this app. Please drag the date range slider, it will automatically disappear :)"),
        html.Div([
            dcc.Graph(id='graph-positive')
        ], style={'display': 'inline-block', 'width': '48%'}),
        html.Div([
            dcc.Graph(id='graph-case')
        ], style={'display': 'inline-block', 'width': '48%'})
    ])
])


@ app.callback(
    Output('us-date', 'children'),
    Input('year_slider', 'value'))
def update_text(d):
    return 'Up to: ' + str(pd.Timestamp(vac_state['Date'].values[-1]) + datetime.timedelta(days=d))


@ app.callback(
    Output('county-date', 'children'),
    Input('county-year_slider', 'value'))
def update_text(d):
    return 'Up to: ' + str(pd.Timestamp(vac_county['Date'].values[-1]) + datetime.timedelta(days=d))


@ app.callback(
    Output('range-date', 'children'),
    [Input('range-slider', 'value')])
def update_text(d):
    date_low = d[0]
    date_high = d[1]
    return 'Start Date: ' + str(pd.Timestamp(tran['report_date'].values[0]) + datetime.timedelta(days=date_low)) + '; End Date: ' + str(pd.Timestamp(tran['report_date'].values[0]) + datetime.timedelta(days=date_high))


@ app.callback(
    Output('graph-state', 'figure'),
    Input('year_slider', 'value'),
    Input('full-vac', 'value'))
def update_figure(d, fully):
    df = vac_state.loc[vac_state['Date_num'] == d]
    fig = go.Figure(data=go.Choropleth(
        locations=df['Location'],  # Spatial coordinates
        # Data to be color-coded
        z=df['Series_Complete_Pop_Pct'] if fully == 'Fully Vaccinated' else df['Administered_Dose1_Pop_Pct'],
        locationmode='USA-states',  # set of locations match entries in `locations`
        colorscale='Viridis',
        colorbar_title="%",
    ))

    fig.update_layout(
        geo_scope='usa',  # limite map scope to USA
    )

    return fig


@ app.callback(
    Output('graph-county', 'figure'),
    Input('chose-state', 'value'),
    Input('county-year_slider', 'value'),
    Input('county-full-vac', 'value'))
def update_figure(state, d, fully):
    df = vac_county.loc[vac_county['Date_num'] == d]
    df = df.loc[df['Recip_State'] == state]
    fully_var = 'Series_Complete_Pop_Pct' if fully == 'Fully Vaccinated' else 'Administered_Dose1_Pop_Pct'
    fig = px.choropleth(df, geojson=counties, locations='FIPS', color=fully_var,
                        color_continuous_scale="Viridis", range_color=(0, 100), scope="usa", labels={'Series_Complete_Pop_Pct': 'Fully Vaccinated %', 'Administered_Dose1_Pop_Pct': 'At Least One Dose %'})
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    return fig


@ app.callback(
    Output('chose-county', 'options'),
    Input('chose-state', 'value'))
def set_county_options(selected_state):
    return [{'label': i, 'value': i} for i in list(vac_county.loc[vac_county['Recip_State'] == selected_state, 'Recip_County'])]


@ app.callback(
    Output('chose-county', 'value'),
    [Input('chose-county', 'options')])
def set_cities_value(available_options):
    return available_options[0]['value']


@ app.callback(
    Output('county-year_slider', 'min'),
    Input('chose-state', 'value'))
def set_slider_options(selected_state):
    df = vac_county.loc[vac_county['Recip_State'] == selected_state]
    return df['Date_num'].min()


@ app.callback(
    Output('county-year_slider', 'max'),
    Input('chose-state', 'value'))
def set_slider_options(selected_state):
    df = vac_county.loc[vac_county['Recip_State'] == selected_state]
    return df['Date_num'].max()


@ app.callback(
    Output('county-year_slider', 'value'),
    Input('chose-state', 'value'))
def set_slider_options(selected_state):
    df = vac_county.loc[vac_county['Recip_State'] == selected_state]
    return df['Date_num'].max()


@ app.callback(
    Output('range-slider', 'min'),
    Input('chose-state', 'value'),
    Input('chose-county', 'value'))
def set_slider_options(selected_state, selected_county):
    df = tran.loc[(tran['state'] == selected_state) &
                  (tran['county_name'] == selected_county)]
    return df['Date_num'].min()


@ app.callback(
    Output('range-slider', 'max'),
    Input('chose-state', 'value'),
    Input('chose-county', 'value'))
def set_slider_options(selected_state, selected_county):
    df = tran.loc[(tran['state'] == selected_state) &
                  (tran['county_name'] == selected_county)]
    return df['Date_num'].max()


@ app.callback(
    Output('range-slider', 'value'),
    Input('chose-state', 'value'),
    Input('chose-county', 'value'))
def set_slider_options(selected_state, selected_county):
    df = tran.loc[(tran['state'] == selected_state) &
                  (tran['county_name'] == selected_county)]
    return [df['Date_num'].min(), df['Date_num'].max()]


@ app.callback(
    Output('graph-positive', 'figure'),
    [Input('range-slider', 'value')],
    Input('chose-state', 'value'),
    Input('chose-county', 'value'))
def update_figure(d, s, c):
    date_low = d[0]
    date_high = d[1]
    df = tran.loc[(tran['state'] == s) & (tran['county_name'] == c) & (
        tran['Date_num'] >= date_low) & (tran['Date_num'] <= date_high)]
    df = df.sort_values(by='Date_num')
    if len(df) == 0:
        raise PreventUpdate
    fig = px.line(df, x='report_date',
                  y='percent_test_results_reported_positive_last_7_days')
    fig.update_layout(title='Daily % Positivity - 7 Day Moving Averages',
                      xaxis_title="Date", yaxis_title="Positivity (%)")

    return fig


@ app.callback(
    Output('graph-case', 'figure'),
    [Input('range-slider', 'value')],
    Input('chose-state', 'value'),
    Input('chose-county', 'value'))
def update_figure(d, s, c):
    date_low = d[0]
    date_high = d[1]
    df = tran.loc[(tran['state'] == s) & (tran['county_name'] == c) & (
        tran['Date_num'] >= date_low) & (tran['Date_num'] <= date_high)]
    df = df.sort_values(by='Date_num')
    if len(df) == 0:
        raise PreventUpdate
    fig = px.line(df, x='report_date',
                  y='cases_per_100K_7_day_count_change')
    fig.update_layout(title='Daily Cases - 7 Day Moving Averages',
                      xaxis_title="Date", yaxis_title="Cases")

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
