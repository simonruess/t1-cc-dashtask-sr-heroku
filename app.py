import os
from random import randint

import flask
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd

server = flask.Flask(__name__)
server.secret_key = os.environ.get('secret_key', str(randint(0, 1000000)))

external_stylesheets = ['https://raw.githubusercontent.com/simonruess/t1-cc-dashtask-sr-heroku/master/assets/typography.css']

app = dash.Dash(__name__, server = server, external_stylesheets = external_stylesheets)

data = pd.read_csv('nama_10_gdp/nama_10_gdp_1_Data.csv', error_bad_lines = False, engine = 'python', na_values = [':', 'NaN'])

eu_values = [
    'European Union (current composition)',
    'European Union (without United Kingdom)',
    'European Union (15 countries)',
    'Euro area (EA11-2000, EA12-2006, EA13-2007, EA15-2008, EA16-2010, EA17-2013, EA18-2014, EA19)',
    'Euro area (19 countries)',
    'Euro area (12 countries)'
            ]

eu_filter = data['GEO'].isin(eu_values)

data = data.loc[~eu_filter.values].reset_index(drop = True)
data['NA_ITEM_UNIT'] = data['NA_ITEM'] + ' (' + data['UNIT'] + ')'

available_indicators = data['NA_ITEM_UNIT'].unique()
available_countries = data['GEO'].unique()

app.layout = html.Div([
    html.Div([
        html.H1(
            children = 'Task 1'
        ),
        html.Div([
            html.P(
                children = 'Select the first indicator:'
            ),
            dcc.Dropdown(
                id = 'xaxis-column1',
                options = [{'label': i, 'value': i} for i in available_indicators],
                value = available_indicators[0]
            ),
            dcc.RadioItems(
                id = 'xaxis-type1',
                options = [{'label': i, 'value': i} for i in ['Linear', 'Log']],
                value = 'Linear',
                labelStyle = {'display': 'inline-block'}
            )
        ],
        style = {'width': '48%', 'display': 'inline-block'}),

        html.Div([
            html.P(
                children = 'Select the second indicator:'
            ),
            dcc.Dropdown(
                id = 'yaxis-column1',
                options = [{'label': i, 'value': i} for i in available_indicators],
                value = available_indicators[1]
            ),
            dcc.RadioItems(
                id = 'yaxis-type1',
                options = [{'label': i, 'value': i} for i in ['Linear', 'Log']],
                value = 'Linear',
                labelStyle = {'display': 'inline-block'}
            )
        ], style = {'width': '48%', 'float': 'right', 'display': 'inline-block'})
    ]),

    dcc.Graph(id = 'indicator-graphic1'),
    html.Div([
        dcc.Slider(
            id = 'year--slider1',
            min = data['TIME'].min(),
            max = data['TIME'].max(),
            value = data['TIME'].max(),
            step = None,
            marks = {str(year): str(year) for year in data['TIME'].unique()}
        )
    ], 
        style = {'margin' : '10px 40px'}
    ),
    html.Div([
    ], 
        style = {'margin': '50px 10px 20px 10px', 'background-color': 'black', 'height': '2px'}
    ),
    html.Div([
        html.H1(
            children = 'Task 2',
            style = {'text-align': 'center'}
        ),
        html.Div([
            html.P(
                children = 'Select a country:'
            ),
            dcc.Dropdown(
                id = 'country2',
                options = [{'label': i, 'value': i} for i in available_countries],
                value = available_countries[0]
            )
        ],
        style = {'width': '48%', 'display': 'inline-block', 'height': '130px'}),

        html.Div([
            html.P(
                children = 'Select an indicator:'
            ),
            dcc.Dropdown(
                id = 'yaxis-column2',
                options = [{'label': i, 'value': i} for i in available_indicators],
                value = available_indicators[0]
            )
        ],
        style = {'width': '48%', 'float': 'right', 'display': 'inline-block'})
    ], 
        style = {'margin-top': '20px'}
    ),

    dcc.Graph(id = 'indicator-graphic2')
])

@app.callback(
    dash.dependencies.Output('indicator-graphic1', 'figure'),
    [dash.dependencies.Input('xaxis-column1', 'value'),
     dash.dependencies.Input('yaxis-column1', 'value'),
     dash.dependencies.Input('xaxis-type1', 'value'),
     dash.dependencies.Input('yaxis-type1', 'value'),
     dash.dependencies.Input('year--slider1', 'value')])

def update_graph(xaxis_column_name, yaxis_column_name,
                 xaxis_type, yaxis_type,
                 year_value):
    dff = data[data['TIME'] == year_value]
    
    return {
        'data': [go.Scatter(
            x = dff[dff['NA_ITEM_UNIT'] == xaxis_column_name]['Value'],
            y = dff[dff['NA_ITEM_UNIT'] == yaxis_column_name]['Value'],
            text = dff[dff['NA_ITEM_UNIT'] == yaxis_column_name]['GEO'],
            mode = 'markers',
            marker = {
                'size': 15,
                'opacity': 0.5,
                'line': {'width': 0.5, 'color': 'white'}
            }
        )],
        'layout': go.Layout(
            xaxis = {
                'title': xaxis_column_name,
                'type': 'linear' if xaxis_type == 'Linear' else 'log'
            },
            yaxis = {
                'title': yaxis_column_name,
                'type': 'linear' if yaxis_type == 'Linear' else 'log'
            },
            margin = {'l': 40, 'b': 40, 't': 40, 'r': 40},
            hovermode = 'closest'
        )
    }

@app.callback(
    dash.dependencies.Output('indicator-graphic2', 'figure'),
    [dash.dependencies.Input('country2', 'value'),
     dash.dependencies.Input('yaxis-column2', 'value')])

def update_graph(country_name, yaxis_column_name):    
    
    return {
        'data': [go.Scatter(
            x = data[(data['GEO'] == country_name) & (data['NA_ITEM_UNIT'] == yaxis_column_name)]['TIME'].values,
            y = data[(data['GEO'] == country_name) & (data['NA_ITEM_UNIT'] == yaxis_column_name)]['Value'].values,
            mode = 'lines'
        )],
        'layout': go.Layout(
            yaxis = {
                'title': yaxis_column_name,
                'titlefont': {'size': 10},
                'type': 'linear'
            },
            margin = {'l': 40, 'b': 40, 't': 40, 'r': 40},
            hovermode = 'closest'
        )
    }

if __name__ == '__main__':
    app.server.run(debug = True, threaded = True)