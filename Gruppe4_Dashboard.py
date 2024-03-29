# -*- coding: utf-8 -*-
#Verwendete Browser: Chrome und Firefox

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

from datetime import date, datetime, timedelta

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


yesterday = datetime.now() - timedelta(1)
yesterday_date = datetime.strftime(yesterday, '%Y-%m-%d')
yesterday_date2 = datetime.strftime(yesterday, '%d.%m.%Y')




app.layout = html.Div(children = [    
        
    #header mit Titel
    html.Div(children = [
        html.H1("Covid-19 Dashboard")
    ], className="header"),
    
     
    #Container für die Diagramme 
    html.Div(children = [

        #Diagramme allgemein
        html.Div(children = [
            #Titel der Inputs
            html.Div(children = [
                html.H2("Choose a continent", className="dropdown-title"),
                html.H2("Choose a Date-Range", className="dropdown-title"),
                html.H2("Choose a country for the line graph", className="dropdown-title")
            ], className="dropdown-titles"),
            
            #Dropdowns
            html.Div(children = [
                
                html.Div(
                    dcc.Dropdown(id='continent',
                                 options = [
                                     {"label": "Africa", "value": 'Africa'},
                                     {"label": "Asia", "value": 'Asia'},
                                     {"label": "Europe", "value": 'Europe'},
                                     {"label": "North America", "value": 'North America'},
                                     {"label": "Oceania", "value": 'Oceania'},
                                     {"label": "South America", "value": 'South America'}],
                                 multi = False,
                                 value='Europe',
                                 className="dropdown"),
                        className="dropdown-menu"
                    ),
                
                html.Div(
                    dcc.DatePickerRange(
                        id='date-range',
                        min_date_allowed=date(2020, 1, 1),
                        max_date_allowed=yesterday_date,
                        initial_visible_month=yesterday_date,
                        start_date=date(2021, 5, 1),
                        end_date=yesterday_date
                    ),
                    className="dropdown-menu"
                ),
                
                html.Div(
                    dcc.Dropdown(id='location',
                    options=[{'label': location, 'value': location} for location in df['location'].unique()],
                    multi = False,
                    value='Switzerland',
                    className="dropdown"),
                className="dropdown-menu"
                )
            ], className="dropdown-menues"),
            
            #Diagramme
            html.Div(children = [
                
                html.Div(children = [
                    html.Div("New Covid-19 cases per million people"),
                    dcc.Graph(id='covidplot', figure = {}),
                    ], className="graph"
                ),
                
                html.Div(children = [
                    html.Div("Line graph for different attributes for the selected country"),
                    dcc.Graph(id='covidplot2', figure = {}),
                    ], className="graph"
                ),
                
                html.Div(children = [
                    html.Div("Vaccine doses distributed"),
                    dcc.Graph(id='covidplot3', figure = {}),
                    ], className="graph"
                ),
                
                html.Div(children = [
                    html.Div("Correlations between the positivity rate and hospitalized patients"),
                    dcc.Graph(id='covidplot4', figure = {}),
                    ], className="graph"
                )
                
            ], className="graphs"),
        ], className="wrapper-graphs"),
    ], className="graph-container"),
    
    #footer mit Infos zum Projekt
    html.Div(children = [
        html.Div(children = [
            html.Div("This dashboard is intended exclusively as an exercise for creating a dynamic user interface. Please be patient while loading the data! Filtering can be defined in the upper area and each individual chart has further zoom options. The selected continent and data-range apply to the bar chart, to the world map and to the scatter plot. The line chart shows the data for the selected country. If the value is set to 0, it means that there is no corresponding data in the data source. Negative values and undefined values in the data set have been replaced with 0."),
            html.Div("Source of the Covid-19 data set:"),
            html.A("ourworldindata.org", href="https://ourworldindata.org/coronavirus-source-data", className="link", target="_blank")
        ])
    ], className="footer"),
], className="container")  
        

@app.callback(
    [Output(component_id='covidplot', component_property='figure'),
     Output(component_id='covidplot2', component_property='figure'),
     Output(component_id='covidplot3', component_property='figure'),
     Output(component_id='covidplot4', component_property='figure'),],
    [Input(component_id='continent', component_property='value'),
     Input('date-range', 'start_date'),
     Input('date-range', 'end_date'),
     Input(component_id='location', component_property='value'),]
)
def update_graph(option_slctd, start_date, end_date, option_slctd1):
    dff = df.copy()
    
    df1 = dff[dff["continent"] == option_slctd]
    df2 = df1[(df1['date'] >= start_date)&(df1['date']<= end_date)]
    df3 = dff[dff["location"] == option_slctd1]
    df4 = df3[(df3['date'] >= start_date)&(df3['date']<= end_date)]
   

    
# Plotly Express

#Balkendiagramm
    fig = px.bar(df2, x="date", y="new_cases_per_million", color="location")
    fig.update_layout(plot_bgcolor="#cbcbcb", paper_bgcolor="#cbcbcb", font_color="#6D7993", margin=dict(pad=8))
    fig.update_yaxes(title=None)
    fig.update_xaxes(title=None)



#Liniendiagramm
#Hypothese 1: Inselstaaten hatten einen späteren Pandemiebeginn als das Festland
    fig2 = px.line(df4, x='date', 
                  y=['new_cases','new_deaths','new_tests',
                     'new_vaccinations', 'handwashing_facilities'])
    fig2.update_layout(plot_bgcolor="#cbcbcb", paper_bgcolor="#cbcbcb", font_color="#6D7993")
    fig2.update_yaxes(title=None)
    fig2.update_xaxes(title=None)
    

#Weltkarte
#Hypothese Nummer 2: Die Impfdosen Verteilung ist auf der Nordhalbkugel weiter fortgeschritten als auf der Südhalbkugel
    fig3 = px.choropleth(df2, locations="iso_code",
                    color="total_vaccinations",
                    hover_name="location",
                    color_continuous_scale=px.colors.sequential.YlGn,
                    projection="natural earth")
    fig3.update_layout(plot_bgcolor="#cbcbcb", paper_bgcolor="#cbcbcb", geo=dict(bgcolor="#cbcbcb"), font_color="#6D7993", margin={"r":0,"t":0,"l":0,"b":0})



#Streudiagramm
#Hypothese Nummer 5: Je mehr positiv getestete Menschen umso mehr Hospitalisierungen
#Problem: Nicht jedes Land hat hierzu Daten
    fig4 = px.scatter(df2, x="positive_rate", y="hosp_patients", 
                     color = "location", size = "positive_rate", hover_data = ['date'],
                     trendline = "ols")
    fig4.update_layout(plot_bgcolor="#cbcbcb", paper_bgcolor="#cbcbcb", font_color="#6D7993")
    fig4.update_yaxes(title="hospitalized patients")
    fig4.update_xaxes(title="positive rate")


    return fig, fig2, fig3, fig4



if __name__ == '__main__':
    app.run_server(debug=False)

