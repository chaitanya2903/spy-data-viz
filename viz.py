from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import date
import vaex
import pandas as pd
import gcsfs

fs = gcsfs.GCSFileSystem(project = 'spy-data')
filename = fs.ls('spy_data_bucket')[0]
print('name',filename)
app = Dash(__name__)
server = app.server 
df = vaex.open("gs://"+filename, fs_options={'anon': True},
                   )

app.layout = html.Div(children=[
    html.H1(children='SPYing on Options Data',
            className='header card', style={'textAlign': 'center'}),
    html.Div(children=[
        html.Div(children=[
            html.Div(children=[
                html.Div(children=[
                    html.H4('Date Range Selector',
                            style={
                                'textAlign': 'center',
                                'fontFamily': 'serif'
                            }),
                    dcc.DatePickerRange(
                        id='my-date-picker-range',
                        min_date_allowed=date(2010, 1, 1),
                        max_date_allowed=date(2021, 12, 31),
                        start_date=date(2010, 1, 1),
                        end_date=date(2012, 1, 31)
                    ),
                ], className='row1-col1-row1 card',
                    style={'flex' : 1}),
                html.Div(children=[
                    html.H4('DTE Slider', style={
                        'textAlign': 'center', 'fontFamily': 'Arial'}),
                    dcc.RangeSlider(
                        min=df['daysTillExpiration'].min(),
                        max=df['daysTillExpiration'].max(),
                        step=None,
                        id='DTE_slider',
                        value=[0, 1100],
                        tooltip={'always_visible': True}
                    ),
                ], className='row1-col1-row2 card',
                    style={'flex' : 1}),
                html.Div(children=[
                    html.H4('Greek Selector / Slider 1',
                            style={'textAlign': 'center', 'fontFamily': 'Arial'}),
                    dcc.Dropdown(
                        options={
                            'delta_1545': 'Delta',
                            'gamma_1545': 'Gamma',
                            'theta_1545': 'Theta',
                            'vega_1545': 'Vega',
                            'implied_volatility_1545': 'Implied Volatility'
                        },
                        value='delta_1545',
                        id='greek_selector',
                    ),
                    dcc.RangeSlider(
                        min=-.5,
                        max=.5,
                        step=None,
                        id='greek_slider',
                        value=[-1, 1],
                        tooltip={'always_visible': False}
                    ),
                ], className='row1-col1-row3 card',
                    style={'flex' : 1}),
            ], className='row1-col1', style={'flex' : 1, 'display': 'flex', 'flexDirection': 'column'}),
            html.Div(children=[
                html.Div(children=[
                    html.H4('Call/Put Selector',
                            style={'textAlign': 'left', 'fontFamily': 'serif'}),
                    dcc.RadioItems(
                        ['Call', 'Put', 'Both'],
                        'Both',
                        id='call_put_selector',
                    ),
                ], className='row1-col2-row1 card',
                    style={'flex' : 1}),
                html.Div(children=[
                    html.H4('ITM/OTM Slider',
                            style={'textAlign': 'center', 'fontFamily': 'Arial'}),
                    dcc.RangeSlider(
                        min=-1.2,
                        max=1,
                        step=None,
                        id='ITM_slider',
                        value=[-1.2, 1],
                        tooltip={'always_visible': True}
                    )
                ], className='row1-col2-row2 card',
                    style={'flex' : 1}),
                html.Div(children=[html.H4('Greek Selector / Slider 2',
                                           style={'textAlign': 'center', 'fontFamily': 'Arial'}),
                                   dcc.Dropdown(
                    options={
                        'delta_1545': 'Delta',
                        'gamma_1545': 'Gamma',
                        'theta_1545': 'Theta',
                        'vega_1545': 'Vega',
                        'implied_volatility_1545': 'Implied Volatility'
                    },
                    value='implied_volatility_1545',
                    id='greek_selector2',
                ),
                    dcc.RangeSlider(
                        min=-.5,
                        max=.5,
                        step=None,
                        id='greek_slider2',
                        value=[0, 40],
                        tooltip={'always_visible': False}
                )], className='row1-col2-row3 card',
                    style={'flex' : 1}),
            ], className='row1-col2', style={'flex' : 1, 'display': 'flex', 'flexDirection': 'column'}),
            html.Div(children=[
                 dcc.Graph(id='cor_mat'),

            ], className='row1-col3 card',
                style={'flex' : 1}),
        ], className='row1', style={'flex' : 1, 'display': 'flex', 'flexDirection': 'row'}),
        html.Div(children=[
            html.Div(children = [dcc.Graph(id='hmap'),], className = 'row2-col1 card', style = {'flex' : 1}),
            html.Div(children = [dcc.Graph(id='itm_otm'),], className = 'row2-col2 card', style = {'flex' : 1}),
            html.Div(children = [dcc.Graph(id='pie_chart'),], className = 'row2-col3 card', style = {'flex' : 1}),
        ], className='row2', style={'flex' : 1, 'display' : 'flex', 'flexDirection':'row'}),
        html.Div(children=[
             dcc.Graph(id='opt_gain')
        ], className='row3 card', style={'flex' : 1}),
    ], className='container', style={'display': 'flex', 'flexDirection': 'column'})

]
)

@app.callback(
    Output('greek_slider', 'min'),
    Output('greek_slider', 'max'),
    Output('greek_slider2', 'min'),
    Output('greek_slider2', 'max'),
    Input('greek_selector', 'value'),
    Input('greek_selector2', 'value'))
def pick_greek(greek_selector, greek_selector2):
    if not greek_selector or not greek_selector2:
        return (-.5, .5, -.5, .5)
    if greek_selector == 'implied_volatility_1545':
        temp_min = 0
        temp_max = 1
    else:
        temp_min = df[greek_selector].min()
        temp_max = df[greek_selector].max()
    if greek_selector2 == 'implied_volatility_1545':
        temp_min2 = 0
        temp_max2 = 1
    else:
        temp_min2 = df[greek_selector2].min()
        temp_max2 = df[greek_selector2].max()
    return (temp_min, temp_max, temp_min2, temp_max2)


@app.callback(
    Output('opt_gain', 'figure'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date'),
    Input('call_put_selector', 'value'),
    Input('ITM_slider', 'value'),
    Input('DTE_slider', 'value'),
    Input('greek_selector', 'value'),
    Input('greek_slider', 'value'),
    Input('greek_selector2', 'value'),
    Input('greek_slider2', 'value'))
def get_time_series(start_date, end_date, call_put_selector, ITM_slider, DTE_slider, greek_selector, greek_slider, greek_selector2, greek_slider2):
    if call_put_selector == 'Put':
        ddf = df[(df.option_type == 'P') & (df.quote_date >= start_date) & (df.quote_date <= end_date) & (
                    df.ITM_OTM >= ITM_slider[0]) & (df.ITM_OTM <= ITM_slider[1]) & (
                                 df.daysTillExpiration >= DTE_slider[0]) & (
                                 df.daysTillExpiration <= DTE_slider[1]) & (
                                 df[greek_selector] >= greek_slider[0]) & (df[greek_selector] <= greek_slider[1]) & (
                                 df[greek_selector2] >= greek_slider2[0]) & (df[greek_selector2] <= greek_slider2[1])]
    elif call_put_selector == 'Call':
        ddf = df[(df.option_type == 'C') & (df.quote_date >= start_date) & (df.quote_date <= end_date) & (
                    df.ITM_OTM >= ITM_slider[0]) & (df.ITM_OTM <= ITM_slider[1]) & (
                                 df.daysTillExpiration >= DTE_slider[0]) & (
                                 df.daysTillExpiration <= DTE_slider[1]) & (
                                 df[greek_selector] >= greek_slider[0]) & (df[greek_selector] <= greek_slider[1])& (
                                 df[greek_selector2] >= greek_slider2[0]) & (df[greek_selector2] <= greek_slider2[1])]
    else:
        ddf = df[(df.quote_date >= start_date) & (df.quote_date <= end_date) & (df.ITM_OTM >= ITM_slider[0]) & (
                    df.ITM_OTM <= ITM_slider[1]) & (df.daysTillExpiration >= DTE_slider[0]) & (
                                 df.daysTillExpiration <= DTE_slider[1]) & (
                                 df[greek_selector] >= greek_slider[0]) & (df[greek_selector] <= greek_slider[1])& (
                                 df[greek_selector2] >= greek_slider2[0]) & (df[greek_selector2] <= greek_slider2[1])]


    ddf = ddf.groupby('quote_date').agg({'optionGain': 'mean', 'underlying_bid_eod': 'mean'})
    ddf = ddf.to_pandas_df()
    ddf.quote_date = pd.to_datetime(ddf.quote_date, format='%Y-%m-%d')
    ddf.sort_values(by='quote_date', inplace=True)

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(x = ddf['quote_date'], y = ddf['optionGain'], mode = 'lines', name = 'Option Gain', line=dict(color=px.colors.qualitative.D3[4])),
        secondary_y = False,
    )
    fig.add_trace(
        go.Scatter(x = ddf.quote_date, y = ddf.underlying_bid_eod, mode = 'lines', name = 'Underlying Price', line=dict(color=px.colors.qualitative.D3[8])),
        secondary_y = True,
    )
    
    fig.update_yaxes(
        title_text="Option Gain",
        secondary_y=False)
    fig.update_yaxes(
        title_text="Underlying Price",
        secondary_y=True)

    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(count=1, label="YTD", step="year", stepmode="todate"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(step="all")
            ])
        ))
    fig.update_layout(title_x=0.5, title_text = 'Option Gain and Underlying Performance')
    return fig



@app.callback(
    Output('hmap', 'figure'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date'),
    Input('call_put_selector', 'value'),
    Input('ITM_slider', 'value'),
    Input('DTE_slider', 'value'),
    Input('greek_selector', 'value'),
    Input('greek_slider', 'value'),
    Input('greek_selector2', 'value'),
    Input('greek_slider2', 'value'))
def heat_map(start_date, end_date, call_put_selector, ITM_slider, DTE_slider, greek_selector, greek_slider, greek_selector2, greek_slider2):
    if call_put_selector == 'Put':
        hmap_df = df[(df.option_type == 'P') & (df.quote_date >= start_date) & (df.quote_date <= end_date) & (
                    df.ITM_OTM >= ITM_slider[0]) & (df.ITM_OTM <= ITM_slider[1]) & (
                                 df.daysTillExpiration >= DTE_slider[0]) & (
                                 df.daysTillExpiration <= DTE_slider[1]) & (
                                 df[greek_selector] >= greek_slider[0]) & (df[greek_selector] <= greek_slider[1]) & (
                                 df[greek_selector2] >= greek_slider2[0]) & (df[greek_selector2] <= greek_slider2[1])]
    elif call_put_selector == 'Call':
        hmap_df = df[(df.option_type == 'C') & (df.quote_date >= start_date) & (df.quote_date <= end_date) & (
                    df.ITM_OTM >= ITM_slider[0]) & (df.ITM_OTM <= ITM_slider[1]) & (
                                 df.daysTillExpiration >= DTE_slider[0]) & (
                                 df.daysTillExpiration <= DTE_slider[1]) & (
                                 df[greek_selector] >= greek_slider[0]) & (df[greek_selector] <= greek_slider[1]) & (
                                 df[greek_selector2] >= greek_slider2[0]) & (df[greek_selector2] <= greek_slider2[1])]
    else:
        hmap_df = df[(df.quote_date >= start_date) & (df.quote_date <= end_date) & (df.ITM_OTM >= ITM_slider[0]) & (
                    df.ITM_OTM <= ITM_slider[1]) & (df.daysTillExpiration >= DTE_slider[0]) & (
                                 df.daysTillExpiration <= DTE_slider[1]) & (
                                 df[greek_selector] >= greek_slider[0]) & (df[greek_selector] <= greek_slider[1]) & (
                                 df[greek_selector2] >= greek_slider2[0]) & (df[greek_selector2] <= greek_slider2[1])]
    hmap_df = hmap_df.groupby(['ITM_OTM', 'daysTillExpiration']).agg({'optionGain': 'mean'})[
        ['ITM_OTM', 'daysTillExpiration', 'optionGain']]
    hmap_df = hmap_df.to_pandas_df()
    hmap_df.sort_values(by = 'ITM_OTM', inplace=True)

    fig = px.density_heatmap(
        hmap_df,
        x='daysTillExpiration',
        y='ITM_OTM',
        z='optionGain',
        histfunc="avg",
        labels={
            'daysTillExpiration': 'Days Until Expiration',
            'ITM_OTM': 'In the Money/ Out the Money Range',
        },
        color_continuous_midpoint = 0,
        title = 'Option Gain by DTE and ITM/OTM',
        color_continuous_scale='rdylgn'
    )
    fig.update_layout(title_x=0.5)
    return fig




@app.callback(
    Output('itm_otm', 'figure'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date'),
    Input('call_put_selector', 'value'),
    Input('ITM_slider', 'value'),
    Input('DTE_slider', 'value'),
    Input('greek_selector', 'value'),
    Input('greek_slider', 'value'),
    Input('greek_selector2', 'value'),
    Input('greek_slider2', 'value'))
def update_scatter(start_date, end_date, call_put_selector, ITM_slider, DTE_slider, greek_selector, greek_slider, greek_selector2, greek_slider2):
    if call_put_selector == 'Put':
        fdf = df[(df.option_type == 'P') & (df.quote_date >= start_date) & (df.quote_date <= end_date) & (
                df.ITM_OTM >= ITM_slider[0]) & (df.ITM_OTM <= ITM_slider[1]) & (
                               df.daysTillExpiration >= DTE_slider[0]) & (
                               df.daysTillExpiration <= DTE_slider[1]) & (
                               df[greek_selector] >= greek_slider[0]) & (df[greek_selector] <= greek_slider[1]) & (
                                 df[greek_selector2] >= greek_slider2[0]) & (df[greek_selector2] <= greek_slider2[1])]
    elif call_put_selector == 'Call':
        fdf = df[(df.option_type == 'C') & (df.quote_date >= start_date) & (df.quote_date <= end_date) & (
                df.ITM_OTM >= ITM_slider[0]) & (df.ITM_OTM <= ITM_slider[1]) & (
                               df.daysTillExpiration >= DTE_slider[0]) & (
                               df.daysTillExpiration <= DTE_slider[1]) & (
                               df[greek_selector] >= greek_slider[0]) & (df[greek_selector] <= greek_slider[1]) & (
                                 df[greek_selector2] >= greek_slider2[0]) & (df[greek_selector2] <= greek_slider2[1])]
    else:
        fdf = df[
            (df.quote_date >= start_date) & (df.quote_date <= end_date) & (df.ITM_OTM >= ITM_slider[0]) & (
                    df.ITM_OTM <= ITM_slider[1]) & (df.daysTillExpiration >= DTE_slider[0]) & (
                    df.daysTillExpiration <= DTE_slider[1]) & (
                    df[greek_selector] >= greek_slider[0]) & (df[greek_selector] <= greek_slider[1]) & (
                                 df[greek_selector2] >= greek_slider2[0]) & (df[greek_selector2] <= greek_slider2[1])]
    fdf = fdf.groupby('daysTillExpiration').agg({'trade_volume': 'mean', 'ITM_OTM': 'mean'})[
        ['daysTillExpiration', 'ITM_OTM', 'trade_volume']]
    fdf = fdf.to_pandas_df()
    fig = px.scatter(fdf, x='daysTillExpiration', y='ITM_OTM', size='trade_volume', labels={
        'ITM_OTM': 'In the Money/Out the Money',
        'daysTillExpiration': 'Days Until Expiration'}, title = 'Option Volume')
    fig.update_layout(title_x = 0.5)
    return fig



@app.callback(
    Output('pie_chart', 'figure'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date'),
    Input('call_put_selector', 'value'),
    Input('ITM_slider', 'value'),
    Input('DTE_slider', 'value'),
    Input('greek_selector', 'value'),
    Input('greek_slider', 'value'),
    Input('greek_selector2', 'value'),
    Input('greek_slider2', 'value'))
def pie_chart(start_date, end_date, call_put_selector, ITM_slider, DTE_slider, greek_selector, greek_slider, greek_selector2, greek_slider2):
    if call_put_selector == 'Put':
        pie_df = df[(df.option_type == 'P') & (df.quote_date >= start_date) & (df.quote_date <= end_date) & (
                df.ITM_OTM >= ITM_slider[0]) & (df.ITM_OTM <= ITM_slider[1]) & (
                               df.daysTillExpiration >= DTE_slider[0]) & (
                               df.daysTillExpiration <= DTE_slider[1]) & (
                               df[greek_selector] >= greek_slider[0]) & (df[greek_selector] <= greek_slider[1]) & (
                                 df[greek_selector2] >= greek_slider2[0]) & (df[greek_selector2] <= greek_slider2[1])]
    elif call_put_selector == 'Call':
        pie_df = df[(df.option_type == 'C') & (df.quote_date >= start_date) & (df.quote_date <= end_date) & (
                df.ITM_OTM >= ITM_slider[0]) & (df.ITM_OTM <= ITM_slider[1]) & (
                               df.daysTillExpiration >= DTE_slider[0]) & (
                               df.daysTillExpiration <= DTE_slider[1]) & (
                               df[greek_selector] >= greek_slider[0]) & (df[greek_selector] <= greek_slider[1]) & (
                                 df[greek_selector2] >= greek_slider2[0]) & (df[greek_selector2] <= greek_slider2[1])]
    else:
        pie_df = df[
            (df.quote_date >= start_date) & (df.quote_date <= end_date) & (df.ITM_OTM >= ITM_slider[0]) & (
                    df.ITM_OTM <= ITM_slider[1]) & (df.daysTillExpiration >= DTE_slider[0]) & (
                    df.daysTillExpiration <= DTE_slider[1]) & (
                    df[greek_selector] >= greek_slider[0]) & (df[greek_selector] <= greek_slider[1]) & (
                                 df[greek_selector2] >= greek_slider2[0]) & (df[greek_selector2] <= greek_slider2[1])]
    pie_df = pie_df.groupby(['option_type', 'profit']).agg({'trade_volume': 'sum'})['option_type', 'profit', 'trade_volume']
    pie_df = pie_df.to_pandas_df()
    fig = px.sunburst(pie_df, path = ['option_type', 'profit'], values = 'trade_volume', title = 'Call/Put Volume and Profitability Ratios', color = 'option_type')

    if call_put_selector == 'Both':
        fig.update_traces(
            marker_colors=[
                px.colors.qualitative.D3[2],  px.colors.qualitative.D3[2], px.colors.qualitative.D3[3], px.colors.qualitative.D3[3], px.colors.qualitative.D3[0], px.colors.qualitative.D3[1]
            ],
            leaf_opacity=0.9)
    elif call_put_selector == 'Call':
        fig.update_traces(
            marker_colors=[
                px.colors.qualitative.D3[2],  px.colors.qualitative.D3[3], px.colors.qualitative.D3[0]
            ],
            leaf_opacity=0.9)
    elif call_put_selector == 'Put':
        fig.update_traces(
            marker_colors=[
                px.colors.qualitative.D3[2],  px.colors.qualitative.D3[3], px.colors.qualitative.D3[1]
            ],
            leaf_opacity=0.9)

    fig.update_layout(title_x = 0.5)
    return fig


@app.callback(
    Output('cor_mat', 'figure'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date'),
    Input('call_put_selector', 'value'),
    Input('ITM_slider', 'value'),
    Input('DTE_slider', 'value'),
    Input('greek_selector', 'value'),
    Input('greek_slider', 'value'),
    Input('greek_selector2', 'value'),
    Input('greek_slider2', 'value'))
def cor_matrix(start_date, end_date, call_put_selector, ITM_slider, DTE_slider, greek_selector, greek_slider, greek_selector2, greek_slider2):
    if call_put_selector == 'Put':
        cor_mat_df = df[(df.option_type == 'P') & (df.quote_date >= start_date) & (df.quote_date <= end_date) & (
                    df.ITM_OTM >= ITM_slider[0]) & (df.ITM_OTM <= ITM_slider[1]) & (
                                 df.daysTillExpiration >= DTE_slider[0]) & (
                                 df.daysTillExpiration <= DTE_slider[1]) & (
                                 df[greek_selector] >= greek_slider[0]) & (df[greek_selector] <= greek_slider[1]) & (
                                 df[greek_selector2] >= greek_slider2[0]) & (df[greek_selector2] <= greek_slider2[1])]
    elif call_put_selector == 'Call':
        cor_mat_df = df[(df.option_type == 'C') & (df.quote_date >= start_date) & (df.quote_date <= end_date) & (
                    df.ITM_OTM >= ITM_slider[0]) & (df.ITM_OTM <= ITM_slider[1]) & (
                                 df.daysTillExpiration >= DTE_slider[0]) & (
                                 df.daysTillExpiration <= DTE_slider[1]) & (
                                 df[greek_selector] >= greek_slider[0]) & (df[greek_selector] <= greek_slider[1]) & (
                                 df[greek_selector2] >= greek_slider2[0]) & (df[greek_selector2] <= greek_slider2[1])]
    else:
        cor_mat_df = df[(df.quote_date >= start_date) & (df.quote_date <= end_date) & (df.ITM_OTM >= ITM_slider[0]) & (
                    df.ITM_OTM <= ITM_slider[1]) & (df.daysTillExpiration >= DTE_slider[0]) & (
                                 df.daysTillExpiration <= DTE_slider[1]) & (
                                 df[greek_selector] >= greek_slider[0]) & (df[greek_selector] <= greek_slider[1]) & (
                                 df[greek_selector2] >= greek_slider2[0]) & (df[greek_selector2] <= greek_slider2[1])]
    cor_mat_df = cor_mat_df[
        ['optionGain', 'trade_volume', 'daysTillExpiration', 'ITM_OTM', 'implied_volatility_1545', 'delta_1545', 'gamma_1545', 'theta_1545', 'vega_1545'
          ]]
    cor_mat_df = cor_mat_df.to_pandas_df()
    cor_mat_df.columns = ['Option Gain', 'Volume', 'DTE', 'ITM_OTM', 'IV', 'Delta', 'Gamma', 'Theta', 'Vega']
    cor_mat_final = cor_mat_df.corr()
    fig = px.imshow(cor_mat_final, text_auto='0.02f',
                    title='Correlation Matrix',
                    color_continuous_scale='rdylgn',
                    color_continuous_midpoint=0,
                    aspect='auto')
    fig.update_layout(title_x=0.5)
    return fig

if __name__ == "__main__":
    app.run_server()