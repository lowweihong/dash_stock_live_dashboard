# -*- coding: utf-8 -*-
"""
Created on Tue Jun 19 22:17:15 2018

@author: Low Wei Hong
"""
import dash
from dash.dependencies import Output, Event
import dash_core_components as dcc
import dash_html_components as html
import requests
from bs4 import BeautifulSoup
import plotly
import plotly.graph_objs as go
from collections import deque
from crawldash import crawl
import dash_table_experiments as dt



url = 'https://www.investing.com/indices/ftse-malaysia-klci-components'

agent = {"User-Agent":'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
respond = requests.get(url,headers=agent)
soup = BeautifulSoup(respond.text)

index = soup.findAll('span',{'class':'arial_26 inlineblock pid-29078-last'})[0].text
times = soup.findAll('span',{'class':'bold pid-29078-time'})[0].text

X = deque(maxlen=20)
X.append(times)
Y = deque(maxlen=20)
Y.append(float(index.replace(',','')))
df = crawl()[1] ##KEXIN
df.iloc[:,1:5]= df.iloc[:,1:5].astype('float')
df['Chg.%'] = df['Chg.%'].map(lambda x: float(x[:-1]),
               na_action=None)

df.Volume = (df.Volume.replace(r'[KM]+$', '', regex=True).astype(float) * df.Volume.str.extract(r'[\d\.]+([KM]+)', expand=False).fillna(1).replace(['K','M'], [10**3, 10**6]).astype(int))

app_colors = {
    'background': '#0C0F0A',
    'text': '#FFFFFF',
    'sentiment-plot':'#41EAD4',
    'volume-bar':'#FBFC74',
    'someothercolor':'#FF206E',
}

app = dash.Dash(__name__)
app.layout = html.Div(
    [   
        html.Div(className='container-fluid', children=[
                html.H2('Bursa Malaysia', style={'color':"#CECECE"}),#,'width':'98%','margin-left':10,'margin-right':10,'max-width':50000}),
        ]),
     
        html.Div([
                html.Div([
                        dcc.Graph(id='live-graph-index', animate=False)], 
                         className='six columns'),
                html.Div([
                        dcc.Graph(id='sentiment-pie', animate=False)],
                         className='six columns'),
        ],className='row'),

        #html.Div(className='row', children=[html.Div(dcc.Graph(id='sentiment-pie', animate=False), className='col s12 m6 l6')]),        
        
        html.Div(className="row",children=[
               html.H4('Top 30 Stocks details table',style={'color':"#CECECE"}),
                       dt.DataTable(
                               rows=df.to_dict('records'),
            
                                # optional - sets the order of columns
                                columns=df.columns,
                                #row_update = True,
                                row_selectable=True,
                                filterable=True,
                                sortable=True,
                                selected_row_indices=[],
                        id='live-table'
                        ),  
            ]),                
        dcc.Interval(
            id='graph-update',
            interval=25*1000 #in millisecond 1*1000= 1 second
        ),
    ], style={'backgroundColor': app_colors['background'],}# 'margin-top':'-30px',},#, 'height':'2000px',},

)

app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})    
    
@app.callback(Output('live-graph-index', 'figure'),
              events=[Event('graph-update', 'interval')])
def update_graph_scatter():
   
    temp=crawl()[0]
    index = temp[0]
    times = temp[1]
    X.append(times)
    Y.append(float(index.replace(',','')))
    data = plotly.graph_objs.Scatter(
            x=list(X),
            y=list(Y),
            name='Scatter',
            mode= 'lines+markers'
            )

    return {'data': [data],'layout' : go.Layout(title='KLSE recent 20 points',
                                                xaxis=dict(range=[min(X),max(X)]),
                                                yaxis=dict(range=[min(Y),max(Y)]),
                                                font={'color':app_colors['text']},
                                                plot_bgcolor = app_colors['background'],
                                                paper_bgcolor = app_colors['background'],)}
    

@app.callback(Output('sentiment-pie', 'figure'),
              events=[Event('graph-update'
                            , 'interval')])    
def update_pie_chart():
    
    temp=crawl()[2]
    pos = temp[0]
    neg = temp[1]
    neu = temp[2]
   
    labels = ['Positive','Negative','Neutral']

    values = [pos,neg,neu]
    colors = ['#007F25', '#800000', '#FF206E']

    trace = go.Pie(labels=labels, values=values,
                   hoverinfo='label+percent', textinfo='value', 
                   textfont=dict(size=20, color=app_colors['text']),
                   marker=dict(colors=colors, 
                               line=dict(color=app_colors['background'], width=2)))

    return {"data":[trace],'layout' : go.Layout(
                                                  title='Pie Chart of percentage of movement of 30 stocks',
                                                  font={'color':app_colors['text']},
                                                  plot_bgcolor = app_colors['background'],
                                                  paper_bgcolor = app_colors['background'],
                                                  showlegend=True)}

##KEXIN    
    
@app.callback(Output('live-table', 'rows'),#selected_row_indices'),
              events=[Event('graph-update', 'interval')])    
def update_table():
    temp2 = crawl()[1]
    temp2.iloc[:,1:5]= temp2.iloc[:,1:5].astype('float')
    temp2['Chg.%'] = temp2['Chg.%'].map(lambda x: float(x[:-1]),na_action=None)

    temp2.Volume = (temp2.Volume.replace(r'[KM]+$', '', regex=True).astype(float) * temp2.Volume.str.extract(r'[\d\.]+([KM]+)', expand=False).fillna(1).replace(['K','M'], [10**3, 10**6]).astype(int))

    return temp2.to_dict('records')

if __name__ == '__main__':
    app.run_server(debug=True)
    

    
# default browser = 127.0.0.1:8050
