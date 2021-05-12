# -*- coding: utf-8 -*-
"""
Created on Wed May 12 17:16:18 2021

@author: ninai
"""

#Hypothesen:
#H1: Inselstaaten hatten einen späteren Pandemiebeginn als das Festland.
#H2: Die Impfdosen und die Verteilung ist auf der Nordhalbkugel weiter fortgeschritten als auf der Südhalbkugel.
#H3: In Länder mit kleiner Population sinken die Fallzahlen schneller als in Länder mit hoher Bevölkerungsdichte.
#H4: In Europa sind aktuell mehr positiv getestete Personen zuhause in Isolation als in Asien.
#H5: Je mehr positiv getestete Menschen, umso mehr Hospitalisierungen.



import pandas as pd
import plotly.express as px

import requests
import io

import numpy as np
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output


app = dash.Dash(__name__)

CSV_URL = 'https://covid.ourworldindata.org/data/owid-covid-data.csv'

csv_data = requests.get(CSV_URL).content 

df = pd.read_csv(io.StringIO(csv_data.decode('latin1')), sep=',')


df.replace("", 0, inplace=True)
df.replace(np.NaN, 0, inplace=True)


#negative Werte durch 0 ersetzen
num = df._get_numeric_data()
num[num < 0] = 0



app.layout = html.Div(children = [    
        
    html.H1("CORONA DASHBOARD - GRUPPE 4", 
            style = {'text-align': 'center', 'color': 'white','background-color': '#6c9176', 'padding': '25px'}),
    
    
    html.Div(children = [ 
        html.H3("Beschreibung", style = {'text-align': 'left', 'color': 'white', 'background-color': '#a7d6ab', 'padding': '10px'}),
      
        
     dcc.Dropdown(id='continent',
                 options = [{'label': continent, 'value': continent} for continent in df['continent'].unique()],
                 multi = False,
                 value='Europe',
                 style = {"width": "40%",'display': 'inline-block',  }),
 
#gaht ned :D es zeigt alli Länder so viel mal ah wies ide Spalte vor chömed
#kei ahnig wie mer chan vor filtere, dass es denn nur die Länder usem Kontinent azeigt wo mer vorher usgwählt het
    dcc.Dropdown(id='location',
                 
                    options=[{'label': location, 'value': location} for location in df['location'].unique()],
                    multi = False,
                    value='Germany',
                    style = {"width": "40%",'display': 'inline-block',  }), 
                    
    
         

#DatePicker Quelle: https://dash.plotly.com/dash-core-components/datepickerrange
        dcc.DatePickerRange(
            id='date-range',
            start_date_placeholder_text="Start Period",
            end_date_placeholder_text="End Period",
            calendar_orientation='horizontal',),  
 
    
#de Slider bruchemer glaub ned minere Meinig nah
        dcc.Slider(id='my-slider', min=0, max=100000, step=1000, value=0, 
               tooltip = { 'always_visible': True },
               marks={5000*i: '{}'.format(5000*i) for i in range(21)},),
    ], style={'background-color': '#a7d6ab', 'text-align': 'left'}),
    

#Balkendiagramm & Liniendiagramm
    html.Div(children = [   
        
    dcc.Graph(id='covidplot', figure = {}),    
    dcc.Graph(id='covidplot2', figure = {})], 
                               style={'display': 'inline-block', 
                                      'vertical-align': 'top', 
                                      'margin-left': '2vw', 'margin-top': '3vw',
                                      'width': '40vw', 'height': '40vh'}),

#Weltkarte & Streudiagramm 
    html.Div(children = [
        
    dcc.Graph(id='covidplot3', figure = {}),
    dcc.Graph(id='covidplot4', figure = {})], 
                               style={'display': 'inline-block', 
                                      'vertical-align': 'top', 
                                      'margin-left': '2vw', 'margin-top': '3vw',
                                      'width': '40vw', 'height': '40vh'})
])

@app.callback(
    [Output(component_id='covidplot', component_property='figure'),
     Output(component_id='covidplot2', component_property='figure'),
     Output(component_id='covidplot3', component_property='figure'),
     Output(component_id='covidplot4', component_property='figure')],
    [Input(component_id='location', component_property='value'),
     Input(component_id='my-slider', component_property='value')]
)

def update_graph(option_slctd, option_slctd2):
    dff = df.copy()
    dff = dff[dff["location"] == option_slctd]
    dff = dff[dff["new_cases"] > option_slctd2]    
    
# Plotly Express

#Balkendiagramm
    fig = px.bar(dff, x="date", y="total_cases", color="location",
                 title = "Total cases for "+option_slctd)


#Liniendiagramm
#Hypothese 1: Inselstaaten hatten einen späteren Pandemiebeginn als das Festland
    fig2 = px.line(dff, x='date', 
                  y=['new_cases','new_deaths','new_vaccinations',
                     'total_vaccinations_per_hundred'],
            title = "Line Graphs for Several Relevant Attributes for "+option_slctd)

#Weltkarte
#Hypothese Nummer 2: Die Impfdosen Verteilung ist auf der Nordhalbkugel weiter fortgeschritten als auf der Südhalbkugel
#Problem: total_vaccinations sind irgendwie immer bi 0
    fig3 = px.choropleth(df, locations="iso_code",
                    color="total_vaccinations",
                    hover_name="location",
                    animation_frame="date",
                    title = "Vaccine doses distributed",
                    color_continuous_scale=px.colors.sequential.YlGn)


#Streudiagramm
#Hypothese Nummer 5: Je mehr positiv getestete Menschen umso mehr Hospitalisierungen
#Problem: hosp_patients sind irgendwie immer bi 0
    fig4 = px.scatter(dff, x="positive_rate", y="hosp_patients", 
                     color = "hosp_patients", size = "positive_rate", hover_data = ['date'],
                     trendline = "ols",
                     title = "Correlations between positive_rate and hosp_patients "+option_slctd)


    

    return fig, fig2, fig3, fig4


if __name__ == '__main__':
    app.run_server(debug=False)