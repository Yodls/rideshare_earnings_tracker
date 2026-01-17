from flask_login import current_user
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
from config import app, create_connection
import pandas as pd
import plotly.graph_objects as go

#Daily Plotly Line Graph
def fetch_daily():
    id = current_user.id
    conn = create_connection()
    cursor = conn.cursor()
    query = """
    SELECT date_value, take_home_earnings, miles, hours, per_mile_rate, per_hour_rate
    FROM "public"."Daily" WHERE id = %s;
    """
    cursor.execute(query, (id,))
    data = cursor.fetchall()
    return data

dailyPlot = Dash(__name__, server=app, url_base_pathname='/dailyPlot/', external_stylesheets=[dbc.themes.BOOTSTRAP])
dailyPlot.layout = html.Div([
    dcc.Graph(id='data-graph'),
    html.Div(id='hidden-div', style={'display': 'none'})
])

@dailyPlot.callback(
    Output('data-graph', 'figure'),
    [Input('hidden-div', 'children')]
)
def update_graph(_):
    data = fetch_daily()

    # Extract lists
    date_list = [row[0] for row in data]
    take_home_earnings_list = [row[1] for row in data]
    miles_list = [row[2] for row in data]
    hours_list = [row[3] for row in data]
    per_mile_rate_list = [row[4] for row in data]
    per_hour_rate_list = [row[5] for row in data]


    mode = 'lines+markers'

    # Initialize the figure
    fig = px.scatter()  # Dummy for layout initialization
    
    # Plot data
    fig.add_scatter(x=date_list, y=per_hour_rate_list, mode=mode, name='Per Hour Rate')
    fig.add_scatter(x=date_list, y=per_mile_rate_list, mode=mode, name='Per Mile Rate', yaxis="y2")
    fig.add_scatter(x=date_list, y=take_home_earnings_list, mode=mode, name='Take Home Earnings')
    fig.add_scatter(x=date_list, y=miles_list, mode=mode, name='Miles')
    fig.add_scatter(x=date_list, y=hours_list, mode=mode, name='Hours', yaxis="y2")

    # Update layout
    fig.update_layout(
        height=600,  # adjust as required
        margin=dict(t=10, b=10, l=10, r=10),  # reduces margin sizes
        yaxis_title='Earnings/Miles',
        yaxis2=dict(title='Rate/Hours', overlaying='y', side='right'),
    )

    return fig


#Weekly Plotly Line Graph
def fetch_weekly_data():
    id = current_user.id
    user_id = current_user.get_id()
    conn = create_connection()
    cursor = conn.cursor()
    query = """
    SELECT *
    FROM "public"."Weekly" WHERE id = %s;
    """
    cursor.execute(query, (id,))
    df = pd.read_sql(query, conn, params=(user_id,))
    df_sorted = df.sort_values(by='week_number')
    
    return df_sorted

weeklyPlot = Dash(__name__, server=app, url_base_pathname='/weeklyPlot/', external_stylesheets=[dbc.themes.BOOTSTRAP])
weeklyPlot.layout = html.Div([
    dcc.Graph(id='weekly-graph'),
    html.Div(id='hidden-div', style={'display':'none'})
])
@weeklyPlot.callback(
    Output('weekly-graph', 'figure'),
    [Input('hidden-div', 'children')]
)
def update_weekly_graph(_):
    df_sorted = fetch_weekly_data()


    mode = 'lines+markers'
    fig = go.Figure()

    # Plot data
    fig.add_trace(go.Scatter(x=df_sorted['my_reference'], y=df_sorted['take_home_earnings'], mode=mode, name='Take Home Earnings'))
    fig.add_trace(go.Scatter(x=df_sorted['my_reference'], y=df_sorted['miles'], mode=mode, name='Miles'))
    fig.add_trace(go.Scatter(x=df_sorted['my_reference'], y=df_sorted['per_hour_rate'], mode=mode, name='Per Hour Rate'))
    fig.add_trace(go.Scatter(x=df_sorted['my_reference'], y=df_sorted['hours'], mode=mode, name='Hours', yaxis="y2"))
    fig.add_trace(go.Scatter(x=df_sorted['my_reference'], y=df_sorted['per_mile_rate'], mode=mode, name='Per Mile Rate', yaxis="y2"))

    # Update layout
    fig.update_layout(
        yaxis_title='Earnings/Miles',
        yaxis2=dict(title='', overlaying='y', side='right'),  # Title set to an empty string to remove it.
        xaxis_tickangle=-45
    )

    return fig

#monthly Plotly Line Graph
def fetch_monthly_data():
    id = current_user.id
    user_id = current_user.get_id()
    conn = create_connection()
    cursor = conn.cursor()
    query = """
    SELECT * 
    FROM "public"."Monthly" WHERE id = %s;
    """
    cursor.execute(query, (id,))
    df = pd.read_sql(query, conn, params=(user_id,))
    conn.close()
    df_sorted1 = df.sort_values(by='month_prompt')
    
    return df_sorted1

monthlyPlot = Dash(__name__, server=app, url_base_pathname='/monthlyPlot/', external_stylesheets=[dbc.themes.BOOTSTRAP])
monthlyPlot.layout = html.Div([
    dcc.Graph(id='monthly-graph'),
    html.Div(id='hidden-div', style={'display':'none'})
])
@monthlyPlot.callback(
    Output('monthly-graph', 'figure'),
    [Input('hidden-div', 'children')]
)
def update_monthly_graph(_):
    df_sorted1 = fetch_monthly_data()


    mode = 'lines+markers'
    fig = go.Figure()

    df_sorted1['take_home_earnings'] = df_sorted1['take_home_earnings'].astype(str).str.replace(',', '').astype(float)
    df_sorted1['expenses'] = df_sorted1['expenses'].astype(str).str.replace(',', '').astype(float)
    df_sorted1['real_take_home_after_expenses'] = df_sorted1['real_take_home_after_expenses'].astype(str).str.replace(',', '').astype(float)
    fig.add_trace(go.Scatter(x=df_sorted1['my_reference'], y=df_sorted1['take_home_earnings'], mode=mode, name='Take Home Earnings'))
    fig.add_trace(go.Scatter(x=df_sorted1['my_reference'], y=df_sorted1['miles'], mode=mode, name='Miles'))
    fig.add_trace(go.Scatter(x=df_sorted1['my_reference'], y=df_sorted1['per_hour_rate'], mode=mode, name='Per Hour Rate', yaxis="y2"))
    fig.add_trace(go.Scatter(x=df_sorted1['my_reference'], y=df_sorted1['hours'], mode=mode, name='Hours', yaxis="y2"))
    fig.add_trace(go.Scatter(x=df_sorted1['my_reference'], y=df_sorted1['per_mile_rate'], mode=mode, name='Per Mile Rate', yaxis="y2"))



    fig.update_layout(
        yaxis_title='Earnings/Miles',
        yaxis2=dict(overlaying='y', side='right'),
        xaxis_tickangle=-45
    )

    return fig

