# -*- coding: utf-8 -*-

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

from datetime import date
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
        
    html.H2("CORONA DASHBOARD - GRUPPE 4", 
            style = {'text-align': 'center', 'color': 'white','background-color': '#6c9176', 'padding': '10px'}),
    
    

    
        html.Div(children = [ 
            dcc.ConfirmDialogProvider(children=html.Button('More information', style = {'float': 'right', 'width': '10vw', 'height': '5vh','padding': '2px'}), id='informationBox',
                                              message=('Dieses Dashboard ist ausschliesslich zur Übung für eine Erstellung eines dynamischen User Interfaces angedacht. Bitte um Geduld beim Laden der Daten! Die Filterung kann jeweils im oberen Bereich definiert werden und jedes einzelne Diagramm hat weitere Zoom Möglichkeiten. Umso stärker die Farbe wird, umso grösser wird die entsprechende Zahl. Falls der Wert auf 0 steht, bedeutet dies, dass es aus der Datenquelle keine Daten gibt!')),
          
    #Dropdown für location, hier kann entweder ein einzelnes Land oder auch ein ganzer Kontinent gewählt werden
    #man kann auch World eingeben und sieht die Daten für die ganze Welt 
    #würden gerne zwei Dropdowns einfügen. Ein Dropdown um den Kontinent auszuwählen und ein Dropdown um das Land auszuwählen.
    #Im zweiten Dropdown sollten dann, nur die Länder aufgelistet werden, die zum ausgewählten Kontinent gehören. Hat leider noch nicht geklappt.
            
            html.Div(children = [ 
                    html.H3("Chose a continent or a country", style={'color':'white'}),
                    dcc.Dropdown(id='location',
                                options=[{'label': location, 'value': location} for location in df['location'].unique()],
                                multi = False,
                                value='Switzerland',
                                style = {"width": "60%"}),
                    ], style = {'display': 'inline-block', 
                                      'vertical-align': 'top', 
                                      'width': '40vw', 'height': '15vh'}),
                    
                    
                
            #DatePicker Quelle: https://dash.plotly.com/dash-core-components/datepickerrange
            
            
            html.Div(children = [
                 html.H3("Chose a Date-Range", style={'color':'white'}),
                   dcc.DatePickerRange(id='date-range',
                                min_date_allowed=date(2020, 1, 1),
                                initial_visible_month=date(2021, 5, 1),
                                start_date= date(2020, 6, 1),
                                end_date= date(2020, 6, 30),
                                style = {"width": "60%"}),
                   ], style = {'display': 'inline-block', 
                                      'vertical-align': 'top', 
                                      'width': '40vw', 'height': '15vh'}),
            
            
       ], style ={'text-align': 'left', 'background-color': '#a7d6ab', 'padding': '5px'}),
    
 
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
                                      'width': '40vw', 'height': '40vh'}),
])

@app.callback(
    [Output(component_id='covidplot', component_property='figure'),
     Output(component_id='covidplot2', component_property='figure'),
     Output(component_id='covidplot3', component_property='figure'),
     Output(component_id='covidplot4', component_property='figure'),
     Output('container-button-timestamp', 'children')],
    [Input(component_id='location', component_property='value'),
     Input('date-range', 'start_date'),
     Input('date-range', 'end_date'),
     Input('btn-nclicks-1', 'n_clicks'),]
)
def update_graph(option_slctd, start_date, end_date):
    dff = df.copy()
    dff = dff[dff["location"] == option_slctd]
    df2 = dff[(dff['date'] >= start_date)&(dff['date']<= end_date)]

    
# Plotly Express

#Balkendiagramm
    fig = px.bar(df2, x="date", y="total_cases", color="location",
                 title = "Total cases for "+option_slctd)


#Liniendiagramm
#Hypothese 1: Inselstaaten hatten einen späteren Pandemiebeginn als das Festland
    fig2 = px.line(df2, x='date', 
                  y=['new_cases','new_deaths','new_vaccinations',
                     'total_vaccinations_per_hundred'],
            title = "Line Graphs for Several Relevant Attributes for "+option_slctd)

#Weltkarte
#Hypothese Nummer 2: Die Impfdosen Verteilung ist auf der Nordhalbkugel weiter fortgeschritten als auf der Südhalbkugel
    fig3 = px.choropleth(df, locations="iso_code",
                    color="total_vaccinations",
                    hover_name="location",
                    animation_frame="date",
                    title = "Vaccine doses distributed",
                    color_continuous_scale=px.colors.sequential.YlGn)


#Streudiagramm
#Hypothese Nummer 5: Je mehr positiv getestete Menschen umso mehr Hospitalisierungen
#Problem: Nicht jedes Land hat hierzu Daten
    fig4 = px.scatter(df2, x="positive_rate", y="hosp_patients", 
                     color = "hosp_patients", size = "positive_rate", hover_data = ['date'],
                     trendline = "ols",
                     title = "Correlations between positive_rate and hosp_patients "+option_slctd)


    

    return fig, fig2, fig3, fig4

def displayClick(btn1):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'btn-nclicks-1' in changed_id:
        msg = 'Button 1 was most recently clicked'
    return html.Div(msg)

if __name__ == '__main__':
    app.run_server(debug=False)
