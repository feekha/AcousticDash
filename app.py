# -*- coding: utf-8 -*-
"""
Created on Tue Nov 22 13:05:03 2022

@author: HENROG
"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import plotly.express as px
from dash import html, Dash, Output, Input, State, dcc, dash_table
import dash_bootstrap_components as dbc
#import tkinter as tk # git  library doesnt work like this when deployed...
from weather import get_weatherdata, daily_mean, get_locs_lats_lons # import weather data funtions
import pickle
from datetime import date, timedelta
from copy import deepcopy
import dash_daq as daq
from dash.exceptions import PreventUpdate
# import dash_auth

# basic authentification --> maybe change GPO (Group Policy Object)
# when basic auth works, uncomment and save into protected file
# VALID_USERNAME_PASSWORD_PAIRS = [['hello', 'world']]

def dump_df(df):
    '''
    Dumps excel-df as pickle file --> cache
    '''
    with open('cache/df_data.pickle', 'wb') as handle:
        pickle.dump(df, handle, protocol=pickle.HIGHEST_PROTOCOL)

def load_df():
    '''
    Loads excel-df from cache
    '''
    with open('cache/df_data.pickle', 'rb') as handle:
        df = pickle.load(handle)
    return df

def dump_weather(all_weather_dict): 
    '''
    Dumps weather-dict as pickle file --> cache
    '''
    with open('cache/weather_data.pickle', 'wb') as handle:
        pickle.dump(all_weather_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
def load_weather():
    '''
    Loads weather-dict from cache
    '''
    with open('cache/weather_data.pickle', 'rb') as handle:
        all_weather_dict = pickle.load(handle)
    return all_weather_dict

def dump_org_cols(df_original_cols): 
    '''
    Dumps original column names as pickle file --> cache
    '''
    with open('cache/df_oroginal_cols.pickle', 'wb') as handle:
        pickle.dump(df_original_cols, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
def load_org_cols():
    '''
    Loads original column names from cache to export excel correctly
    '''
    with open('cache/weather_data.pickle', 'rb') as handle:
        df_original_cols = pickle.load(handle)
    return df_original_cols

def get_map_height():
    '''
    Define minimum height of the map, which also defines the size.
    '''
    #root = tk.Tk() # will not work like this when deployed 
    #screen_height = root.winfo_screenheight()
    screen_height = 900
    map_height = min(screen_height, 900)
    return map_height

def get_daily_weather(all_weather_dict):
    '''
    Determine daily averages for WS, WS at 100m and WD.
    '''
    daily_weather = {}
    for key, weather_df in all_weather_dict.items():
        daily_weather[key] = daily_mean(weather_df, 'wind_speed', 'wind_speed_100m', 'wind_direction')
    days = list(list(daily_weather.values())[0]['day'].astype(str)) # getting all the days from weather data
    return daily_weather, days 

def get_project_managers(df):
    '''
    Determine all projectmanagers from excel-df.
    '''
    project_managers = df['DNV PM'].unique()
    project_managers = [p for p in project_managers if pd.isnull(p)==False]
    project_managers.insert(0, 'Alle PM') # insert Alle PM as an option to get all locations
    return project_managers

def get_locations(pm,df):
    '''
    Get sites from a given project manager
    '''
    pm = str(pm)
    if pm == 'Alle PM':
        locations = df['Messort'].unique()
    else:
        locations = df[df['DNV PM']==pm]['Messort'].unique()
    locations = [l for l in locations if l==l] # remove nan values that occur when empty pm field in table
    return locations

def nested_dicts(dictdf):
    '''
    Deprecated function. Nested df --> nested dict
    '''
    d = deepcopy(dictdf)
    for k, v in d.items():
        d[k] = v.to_dict()
    return d

def nested_df(dictdict):
    '''
    Deprecated function. Nested dict --> nested df
    '''
    d = deepcopy(dictdict)
    for k, v in d.items():
        d[k] = pd.DataFrame(v)
    return d

def sort_wd(one_day_df):
    '''
    Bins wind directions
    '''
    wds = []
    dirs = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'] # provides order for windrose
    for wd in one_day_df['wind_direction']:
        if wd > 337:
            wds.append('N') # N
        elif wd > 292:
            wds.append('NW') # NW
        elif wd > 247:
            wds.append('W') # W
        elif wd > 202:
            wds.append('SW') # SW
        elif wd > 157:
            wds.append('S') # S
        elif wd > 112:
            wds.append('SE') # SE
        elif wd > 67:
            wds.append('E') # E
        elif wd > 22:
            wds.append('NE') # NE
        elif wd <= 22:
            wds.append('N') # N
        elif wd in dirs:
            wds.append(wd)
    return wds, dirs

def default_map():
    '''
    Builds the default when no data available
    '''
    map_fig = go.Figure(go.Scattergeo())
    map_fig.update_geos(
        # visible=False,
        resolution=50, scope="europe", # important settings
        showcountries=True, countrycolor="Black",
        showsubunits=True, subunitcolor="Black",
        showland=True, landcolor="rgba(230, 230, 230, 0.5)",
        )
    map_fig.update_layout(height=get_map_height(),margin={"r":0,"t":30,"l":0,"b":0})
    map_fig.update_layout(
        geo = dict(
            projection_scale=3, #zoom
            center=dict(lat=53.55, lon=9.99), #center on hamburg
            ))
    return map_fig

def build_map_figure(map_day,pm,df,all_weather_dict,min_ws,max_ws):
    '''
    Builds map figure and applies filter.
    '''

    day = str(map_day)
    pm = str(pm)
    if pm == 'Alle PM':
        df_pm = df
    else:
        df_pm = df[df['DNV PM']==pm] # filter sites
        
    # maybe put this somewhere else later
    # get locations, latitudes and longitudes where all three parameters are available
    locs, lats, lons = get_locs_lats_lons(df_pm, all_WT=True) 
    
    if len(locs) == 0:
        map_fig = default_map() # in case no site given
    else:
        daily_weather = get_daily_weather(all_weather_dict)[0]
        
        df_list = []
        for key, daily_df in daily_weather.items(): # create a new dataframe with all sites
            daily_loc_df = daily_df.loc[daily_df['day'].astype(str) == day].copy() # filter for specific day
            daily_loc_df['Messort'] = key
            df_list.append(daily_loc_df)
        new_daily_df = pd.concat(df_list).reset_index(drop=True)
        
        # filter sites
        filtered_df = df.loc[locs.index] 
        new_daily_df['Messort'] = new_daily_df['Messort'].astype(str)
        filtered_df['Messort'] = filtered_df['Messort'].astype(str)
        for messort in filtered_df['Messort'].unique():
            if messort not in new_daily_df['Messort'].values:
                filtered_df.drop(filtered_df[filtered_df['Messort']==messort].index, inplace=True)
        
        # join site-filtered and daily average df
        filtered_daily_df = filtered_df.join(new_daily_df.set_index('Messort'), on = 'Messort') 
        
        # bin wind directions
        wds, dirs = sort_wd(filtered_daily_df)
        filtered_daily_df['WD'] = wds
        filtered_daily_df['WEA X von Y'] = filtered_daily_df['WEA X von Y'].fillna(' ') # fill nan
        filtered_daily_df['bevorz.  WR (falls bekannt)'] =  filtered_daily_df['bevorz.  WR (falls bekannt)'].fillna('all') # empty WD will allow all WD as green
        filtered_daily_df['wind_speed'] = np.round(filtered_daily_df['wind_speed'],2) # round WS
        filtered_daily_df['wind_speed_100m'] = np.round(filtered_daily_df['wind_speed_100m'],2) # round WS 100m
        filtered_daily_df['min. Wind speed needed'].fillna(0, inplace=True) # default lower WS for green
        filtered_daily_df['max. Wind speed needed'].fillna(100, inplace=True) # default higher WS for green

        valid_ws = [filtered_daily_df['wind_speed'][i]>filtered_daily_df['min. Wind speed needed'][i]
                   and filtered_daily_df['wind_speed'][i]<filtered_daily_df['max. Wind speed needed'][i]
                   for i in filtered_daily_df.index] # boolean statement for WS
        valid_wd =  [filtered_daily_df['WD'][i] in
                    [s.strip() for s in filtered_daily_df['bevorz.  WR (falls bekannt)'][i].split(',')]
                    or filtered_daily_df['bevorz.  WR (falls bekannt)'][i] == 'all'
                    for i in filtered_daily_df.index] # boolean statement for WD                                         
        
        # apply boolean statements to set green=1, yellow=0.5 and red=0 on map          
        filtered_daily_df['green WS'] = [1 if (valid_ws[i] and valid_wd[i]) == True
                                          else 0.5 if valid_ws[i] == True 
                                          else 0 for i in range(0,len(filtered_daily_df))]    
        
        filtered_daily_df = filtered_daily_df.loc[(filtered_daily_df['wind_speed']>=min_ws)] # WS filter
        filtered_daily_df = filtered_daily_df.loc[(filtered_daily_df['wind_speed']<=max_ws)] # WS filter
        
        if filtered_daily_df.empty==True:
            map_fig = default_map()
        else:   
            map_fig = px.scatter_geo(
                filtered_daily_df,
                lat='Breitengrad',
                lon='Längengrad',
                custom_data=['Messort','WEA X von Y', 'wind_speed', 'WD'], # define variables for hover template
                color='green WS',
                # color_continuous_scale=[(0,'rgb(0,255,0)'),(1,'rgb(255,0,0)')],
                color_continuous_scale=[(0,'rgb(255,0,0)'),(0.5,'rgb(255,255,0)'),(1,'rgb(0,255,0)')], # red, yellow, green
                size='wind_speed',
                range_color=[0,1], # needed for color scale
                )
            map_fig.update_geos(
                # visible=False,
                resolution=50, scope="europe",
                showcountries=True, countrycolor="Black",
                showsubunits=True, subunitcolor="Black",
                showland=True, landcolor="rgba(230, 230, 230, 0.5)",
                )
            map_fig.update_traces(
                hovertemplate='<b>%{customdata[0]}</b><br>%{customdata[1]}<br>WS: %{customdata[2]} m/s<br>WD: %{customdata[3]}'
                )
            # map_fig.update_coloraxes(colorbar_thickness=15,
            #                          colorbar_len = 0.7,
            #                          colorbar_title_text = 'm/s',
            #                          colorbar_x = 1.15)
            map_fig.update_coloraxes(showscale=False)
            map_fig.update_layout(height=get_map_height(),margin={"r":0,"t":30,"l":0,"b":0})
            map_fig.update_layout(
                geo = dict(
                    projection_scale=3, #zoom
                    center=dict(lat=53.55, lon=9.99), #center on hamburg
                    ))
    return map_fig

def build_weather_figure(location,all_weather_dict):
    '''
    Builds weather forecast figure 
    '''
    if location in all_weather_dict:
        daily_weather_df = daily_mean(all_weather_dict[location], 'temperature') # calcuate daily mean for given paramemeters

        weather_figure = make_subplots(specs=[[{'secondary_y': True}]]) # to get axis on left and right side
        weather_figure.add_trace(
            go.Scatter(
                x = all_weather_dict[location]['timestamp'],
                y = all_weather_dict[location]['precipitation'].multiply(100), # to get %
                name = 'Nd.',
                mode = 'lines',
                line_color = 'rgb(152,143,134)',
                line_dash = 'dot',
                ),
            secondary_y = True # y axis on right side
            )
        weather_figure.add_trace(
            go.Scatter(
                x = all_weather_dict[location]['timestamp'],
                y = np.round(all_weather_dict[location]['wind_speed'],2),
                name = 'WS',
                mode = 'lines',
                line_color = 'rgb(153,217,240)',
                ),
            secondary_y = False # y axis on left side
            )
        weather_figure.add_trace(
            go.Scatter(
                x = all_weather_dict[location]['timestamp'],
                y = np.round(all_weather_dict[location]['wind_speed_100m'],2),
                name = 'WS 100m',
                mode = 'lines',
                line_color = 'rgb(15,32,75)',
                ),
            secondary_y = False # y axis on left side
            )
        weather_figure.update_layout(
            plot_bgcolor = 'rgba(0,0,0,0)',
            font_family = 'Arial',
            font_color = 'black',
            grid_ygap = 0.1,
            )
        weather_figure.update_xaxes(
            dtick = 'D1', # daily ticks on x axis
            showgrid = True,
            gridwidth = 1,
            gridcolor = 'rgb(204,204,204)',
            )
        weather_figure.update_yaxes(
            range = [0,100], # 0 - 100 % precipitation
            visible = True,
            showgrid = False,
            title_text = 'Niederschlag in %',
            secondary_y = True # y axis on right side
            )
        weather_figure.update_yaxes(
            title_text = 'WS in m/s',
            showgrid = False,
            secondary_y = False # y axis on left side
            )
    else:
       weather_figure = {'data': []} # defalt figure when no data available
    return weather_figure

def build_windrose(day,all_weather_dict):
    '''
    Builds windrose for daily data
    '''
    if day == None:
        windrose_fig = {'data': []} # default figure when no weather data available
    else:
        day = str(day)
        location, day = day.rsplit(' ',1) # get location and day from dropdown value   
        one_day_df = all_weather_dict[location].loc[all_weather_dict[location]['day'].astype(str) == day] # get selected day from excel-df
        
        wds, dirs = sort_wd(one_day_df) # bin wind directions   
        
        # count wind speeds for every WD --> frequency
        wds_count = []        
        for d in dirs:
            wds_count.append(wds.count(d)) # check if this is further needed
        d = {
            'wind_direction': wds,
            'wind_speed': list(one_day_df['wind_speed']),            
            }
        wd_df = pd.DataFrame(data=d)
        
        grp = wd_df.groupby(['wind_direction', 'wind_speed']).size().reset_index(name="frequency") # group every WD
        for direction in dirs:
            if direction not in grp['wind_direction']:
                grp.loc[len(grp.index)] = [direction, 0, 0] # fill empty WD with zero values
        grp['wind_direction'] = pd.Categorical(grp['wind_direction'], categories=dirs, ordered=True) # Categorical to sort by category
        grp = grp.sort_values(['wind_direction', 'wind_speed'], ignore_index=True) # sort by WD to get windrose in correct order
        grp['wind_speed'] = np.round(grp['wind_speed'],2) # round WS
        
        windrose_fig = px.bar_polar(grp,
            r ='frequency',
            theta ='wind_direction',
            color = 'wind_speed', # color based on WS
            custom_data=['wind_speed'], # needed for hovortemplate
            color_continuous_scale=[(0,'rgb(255,0,0)'),(1,'rgb(0,255,0)')], # color scale
            range_color=[0,20],
            )
        windrose_fig.update_layout(margin_t = 0,
                                   margin_b = 0,
                                   margin_l = 30,
                                   margin_r = 30,
                                   polar_radialaxis_showticklabels=False,
                                   polar_radialaxis_gridcolor = 'rgb(204,204,204)',
                                   polar_angularaxis_gridcolor = 'rgb(204,204,204)',
                                   polar_bgcolor = 'white',
                                   font_family = 'Arial',
                                   font_color = 'black',)
        windrose_fig.update_traces(
                hovertemplate='Häufigkeit: %{r}<br>WS: %{customdata[0]} m/s'
                )
        windrose_fig.update_coloraxes(colorbar_thickness=5,
                                      colorbar_len = 0.5,
                                      colorbar_title_text = 'm/s',
                                      colorbar_x = 1.15)
        windrose_fig.update_coloraxes(showscale=True)
    return windrose_fig

def sixhourssummary(day, all_weather_dict):
    '''
    Summarize day in six hours steps
    '''
    if day == None:
        h_list = ['-','-','-','-'] # default description when no data available
    else:
        # filter the day
        day = str(day)
        location, day = day.rsplit(' ',1) # get location and day from dropdown value
        one_day_df = all_weather_dict[location].loc[all_weather_dict[location]['day'].astype(str) == day]
        
        # In case of error double check the time format
        times = [' 00:00:00+00:00',' 06:00:00+00:00',' 12:00:00+00:00',' 18:00:00+00:00']
        h_list = []
        
        # need to include all missing conditions here
        # creates Unicode symbols for weather conditions
        condition_icons = {
            'dry-cloudy': '\U00002601',
            'dry-partly-cloudy-day': '\U0001F324',
            'dry-partly-cloudy-night': '\U0000263E'+'\U00002601',
            'rain-rain': '\U0001F327',
            'rain-cloudy': '\U0001F327',
            'rain-partly-cloudy-day': '\U0001F326',
            'rain-partly-cloudy-night': '\U0000263E'+'\U00002601',
            'fog-fog': '\U0001F32B',
            'sleet-sleet': '\U0001F327'+'Hagel',
            'snow-snow': '\U0001F327',
            'rain-wind': '\U0001F32C'+'\U000026C6',
            'dry-wind': '\U0001F32C',
            'dry-clear-day': '\U0000263C',
            'dry-clear-night': '\U0000263E',
            'hail-hail': 'Hagel',
            'thunderstorm-thunderstorm': '\U000026C8',
            }
        
        # create text to display and append to list
        for t in times:
            t_df = one_day_df.loc[one_day_df['timestamp'].astype(str) == (day + t)]
            cond = t_df['condition'].iloc[0]
            icon = t_df['icon'].iloc[0]
            # put something here for the case of None in cond or icon
            cond_icon = cond + '-' + icon
            if cond_icon in condition_icons:
                t_md = dcc.Markdown(f'''#### {condition_icons[cond_icon]} ''') # Markdown gives different size
                t_text = f"Temperatur: {t_df['temperature'].iloc[0]} °C" # Use css size here            
            else:
                t_md = f"{cond} {icon} - - - - - -" # when no condition is given
                t_text = f"Temperatur: {t_df['temperature'].iloc[0]} °C"
            h_list.append([t_md, t_text])
    return h_list

def build_datatable(data):
    '''
    Create table from (filtered) excel data
    '''
    data_table=data.to_dict('records') # dash component can only read specific dict formats
    table = dash_table.DataTable(
        id='table',
        columns=[{'id': c, 'name': c} for c in data.columns], # need to define columns here
        data=data_table,
        editable=True, # set this to false when editing table is forbidden
        row_deletable=True, # set this to false when rows shouldnt be deleted
        hidden_columns=['Index','Alle_Index'], # hide unnnecessary columns here
        style_table={
            'margin-bottom': '0px',
            },
        style_header={
            'fontFamily': 'Arial',
            },
        style_data={
            'fontFamily': 'Arial',
            }
        )
    return table

dbc_css = 'assets/style.css' # load style sheet

app = Dash(__name__,external_stylesheets=[dbc_css])
server = app.server # important for deploying, otherwise not needed

# create basic authentication here when its allowed in GPO
# auth = dash_auth.BasicAuth(
#     app,
#     VALID_USERNAME_PASSWORD_PAIRS
# )

# define app layout
# !!! classnames define css style --> see assets/style.css !!!
app.layout = html.Div(
    [
     # header 
     html.Div(className='row',
              children=[
                  html.Div(className='two columns',
                           children=[
                                   html.Img(className="Logo",
                                            src=app.get_asset_url('DNV_Logo.png')                                       
                                   )
                               ] 
                           ),   
                  html.Div(className='seven columns',
                           children=[
                               html.H4('Schallmessungen - Schnellansicht ' + '\U0001F600', className='app__header__title'),
                               html.P('Bitte Standort auswählen')
                               ],                           
                           ),
                  html.Div(className='one column Selector',
                      children=[
                              html.Button('Update Wetter', id='update-weather-button', n_clicks=0, className='Weather-button'),
                          ]
                      ),
                  html.Div(className='two columns Selector',
                           children=[
                               dcc.Dropdown(get_project_managers(load_df()),
                                            value=get_project_managers(load_df())[0],
                                            id='pm-selector',
                                            clearable=False),
                               dcc.Dropdown(get_locations('Alle PM',load_df()),
                                            value=get_locations('Alle PM',load_df())[0],
                                            id='location-selector',
                                            clearable=False)
                               ],                           
                           ),
                  ]
              ),
     html.Div(className='row',
              # Map
                           children=[
                               html.Div(className='seven columns',
                                        children=[
                                            dcc.Graph(
                                               # figure = map_fig,
                                               id='map',
                                               )
                                            ]
                                        ),
                               html.Div(className='one column',
                                        children=[
                                        html.Div(className='Legend-map',
                                        children=[
                                            '\U0001F7E2 - WS + WD im Messbereich', # legend green
                                            html.Br(), # empty row
                                            html.Br(),
                                            '\U0001F7E1 - WS im Messbereich', # legend yellow
                                            html.Br(),
                                            html.Br(),
                                            '\U0001F534 - schlechte Windbedingunen', # legend red
                                            html.Br(),
                                            html.Br(),
                                            ]
                                            ),                                        
                                            dcc.RadioItems(get_daily_weather(load_weather())[1],
                                                           value=get_daily_weather(load_weather())[1][1],
                                                           id='day-radio',
                                                           className='Radio-days',
                                                           labelClassName='Radio-days-label'),
                                            html.Br(),
                                            dcc.Input( # filter for lower WS 
                                                className='WS-input',
                                                id='min-ws-input',
                                                type='number',
                                                placeholder='Min WS',
                                                min=0,
                                                max=100,
                                                debounce=True,
                                                ),
                                            dcc.Input( # filter for upper WS
                                                className='WS-input',
                                                id='max-ws-input',
                                                type='number',
                                                placeholder='Max WS',
                                                min=0,
                                                max=100,
                                                debounce=True,
                                                ),
                                            ]
                                        ),
                               html.Div(className='four columns blue-border',
                                        # style={'height': '%spx' % map_height },
                                        children=[
                                            html.P(children=[], id='param-title'),
                                            dcc.Graph(id='weather-plot',
                                                # figure = weather_fig,
                                                ),
                                            dcc.Dropdown(options=[], value=None,
                                                         id='day-selector', className='Selector-days', clearable=False),
                                            html.Div(className='six columns',
                                                     children = [
                                                         dcc.Graph(id='windrose',
                                                                   className='Windrose',
                                                                   # figure = windrose_fig,
                                                                   )
                                                         ]  
                                                ),
                                            # six hours weather description
                                            html.Div(className='six columns',
                                                     children = [
                                                         html.Div(className='twelve columns',
                                                             children = [
                                                                 html.Div(className='four columns',
                                                                          children = [
                                                                              html.H6('0:00')
                                                                              ]
                                                                     ),
                                                                 html.Div(className='eight columns Weather-text',
                                                                          id='0h',
                                                                          children = []
                                                                     )
                                                                 ]
                                                             ),
                                                         html.Div(className='twelve columns',
                                                             children = [
                                                                 html.Div(className='four columns',
                                                                          children = [
                                                                              html.H6('6:00')
                                                                              ]
                                                                     ),
                                                                 html.Div(className='eight columns Weather-text',
                                                                          id='6h',
                                                                          children = []
                                                                     )
                                                                 ]
                                                             ),
                                                         html.Div(className='twelve columns',
                                                             children = [
                                                                 html.Div(className='four columns',
                                                                          children = [
                                                                              html.H6('12:00')
                                                                              ]
                                                                     ),
                                                                 html.Div(className='eight columns Weather-text',
                                                                          id='12h',
                                                                          children = []
                                                                     )
                                                                 ]
                                                             ),
                                                         html.Div(className='twelve columns',
                                                             children = [
                                                                 html.Div(className='four columns',
                                                                          children = [
                                                                              html.H6('18:00')
                                                                              ]
                                                                     ),
                                                                 html.Div(className='eight columns Weather-text',
                                                                          id='18h',
                                                                          children = []
                                                                     )
                                                                 ]
                                                             ),
                                                         ]
                                                )
                                            ]
                                        )
                                   ]
           ),
     # Table
     html.Div(className='row',
                           children=[
                               html.Div(className='twelve columns blue-border table-container',
                                        children=[
                                            html.Div(className='ten columns',
                                                     children=[html.P(children=[], id='table-title'),
                                                               html.Div(children=[], id='table-test'),]
                                                ),
                                            html.Div(className='two columns switch-table',
                                                     children=[
                                                         daq.BooleanSwitch(id='switch-whole-table', on=False,
                                                                           label='Alle Standorte',
                                                                           labelPosition='top')
                                                         ]),
                                            html.Div(className='twelve columns nomargin table-rawdata',
                                                    id='data-table',
                                                    children=[
                                                        build_datatable(load_df())
                                                       ]
                                                    ),
                                            html.Button('+ Zeile', id='add-rows-button', n_clicks=0),
                                            html.Button('Speichern App', id='save-dfapp-button', n_clicks=0),
                                            html.Button('Export Excel', id='save-dfexcl-button', n_clicks=0),
                                            html.Button('Import Excel', id='load-excl-button', n_clicks=0),
                                            ]
                                        ),
                                   ]
           ),
     html.Div(className='twelve columns',
              style={'height': '50px'}, # add some space to the bottom of the app
              id='dummy', # dummy for callbacks
               children=[
                   ]
              )
      ]        
    )

@app.callback(
    Output('location-selector', 'options'),
    Output('location-selector', 'value'),
    Input('pm-selector', 'value'),
    State('location-selector', 'value')
    )
def update_pm(pm, loc):
    '''
    Update location selector based on choosen project manager.
    '''
    loc = str(loc)
    df = load_df()
    locations = get_locations(pm,df)
    # check for deleted location:
    if loc in locations:
        location = loc
    else:
        location = locations[0]
    return locations, location

@app.callback(
    Output('table-title','children'),
    Output('param-title', 'children'),
    Output('data-table','children'),
    Output('weather-plot', 'figure'),
    Output('day-selector', 'options'),
    Output('day-selector', 'value'),
    Output('add-rows-button', 'n_clicks'),
    Input('location-selector','value'),
    Input('switch-whole-table', 'on'),
    Input('add-rows-button', 'n_clicks'),
    )
def update_location(location, whole_table, n_clicks):
    '''
    Update table and weather forecast plots that show single location
    '''
    df = load_df()
    all_weather_dict = load_weather()
    df['Index'] = df.index
    df['Index'] = df['Index'].astype(str)
    data=deepcopy(df.loc[df['Messort']==location]) # data contains data for single location
    data['Alle_Index']=['-'.join(data['Index'].to_list()) for ix in data['Index']] # define all index in table to pass information to table editing
    df['Alle_Index']=['-'.join(df['Index'].to_list()) for ix in df['Index']]
    
    # check if empty row already exist to not append unlimited new rows to table
    if n_clicks > 0 and not df.iloc[-1].isna().all():
        df = pd.concat([df,pd.DataFrame([[np.nan for col in df.columns]],columns=df.columns)])
        data = pd.concat([data,pd.DataFrame([[np.nan for col in data.columns]],columns=data.columns)])
    elif n_clicks == 0 and df.iloc[-1].isna().all():
        df.drop(df.index[-1])
        data.drop(data.index[-1])
    
    # wether table shows one location or everything
    if whole_table == True:
        # choose between those tables
        data_table = build_datatable(df) # editable table
        # data_table = dbc.Table.from_dataframe(df) # just table
    else:
        # choose between those tables
        data_table = build_datatable(data) # editable table
        # data_table = dbc.Table.from_dataframe(data) # just table 
    
    # create weather forecast figure
    weather_fig = build_weather_figure(location, all_weather_dict)
    
    # create options for dropdown of selected site
    if location in all_weather_dict:
        days = all_weather_dict[location]['day'].unique()
        days_loc = []
        for d in days:
            days_loc.append(location + ' ' + str(d))
        days_val = days_loc[1]
    else:
        days_loc = []
        days_val = None
        
    n_clicks = 0 # set clicks to zero back to avoid circular dependencies on button click
    return location, location, data_table, weather_fig, days_loc, days_val, n_clicks

@app.callback(
    Output('windrose', 'figure'),
    Output('0h', 'children'),
    Output('6h', 'children'),
    Output('12h', 'children'),
    Output('18h', 'children'),
    Input('day-selector', 'value'),
    )
def update_day(day):
    '''
    Update windrose and six hours description based on selected day and location
    '''
    all_weather_dict = load_weather()
    windrose = build_windrose(day,all_weather_dict)
    zeroh, sixh, twelveh, eighteenh = sixhourssummary(day,all_weather_dict)
    return windrose, zeroh, sixh, twelveh, eighteenh

@app.callback(
    Output('map', 'figure'),
    Input('day-radio', 'value'),
    Input('pm-selector', 'value'),
    Input('min-ws-input', 'value'),
    Input('max-ws-input', 'value'),
    )
def update_map(map_day, pm, min_ws, max_ws):
    '''
    Update map figure based on project manager, day filter and WS filter.
    '''
    if min_ws == None:
        min_ws = 0 # when no min WS is given
    if max_ws == None:
        max_ws = 100 # when no max WS is given
    if min_ws >= max_ws: # when min WS is higher than max WS --> everything will be filtered
        min_ws = 0
        max_ws = 0
    df = load_df()
    all_weather_dict = load_weather()
    new_map = build_map_figure(map_day,pm,df,all_weather_dict,min_ws,max_ws) # build map
    return new_map

@app.callback(
    Output('save-dfapp-button', 'n_clicks'),
    Output('load-excl-button', 'n_clicks'),
    Output('pm-selector','options'),
    Output('pm-selector', 'value'),
    Output('update-weather-button', 'n_clicks'),
    Output('day-radio', 'options'),
    Output('day-radio', 'value'),
    Input('update-weather-button', 'n_clicks'),
    Input('save-dfapp-button', 'n_clicks'),
    Input('load-excl-button', 'n_clicks'),
    State('table', 'data'),
    State('pm-selector', 'value'),
    State('day-radio', 'options'),
    State('day-radio', 'value'),
    State('location-selector','value'),
    )
def table_edit(n_clicks_uw,n_clicks_save,n_clicks_load,data,pm,opt_day_radio,val_day_radio,location):
    '''
    Reacts on buttons below the table, edits table and triggers basic project manager dropdown callbacks to reload app.
    '''
    # if the save button is clicked
    if n_clicks_save > 0:
        df = load_df()
        df['Index'] = df.index
        df['Index'] = df['Index'].astype(int)
        df['Alle_Index'] = df.index
        data = pd.DataFrame(data)
        
        if data.empty == True:
            # drop all rows from location
            df.drop(df[df['Messort']==str(location)].index, inplace=True)
        else:
            # check for single deleted rows
            data = data.fillna(np.nan)
            data['Index'] = pd.to_numeric(data['Index'], errors='coerce')
            idx_list = str(data['Alle_Index'][0]).split('-') # use all idx to distinguish between deleted and edited rows
            for i in idx_list:
                if int(i) not in data['Index'].values: 
                    df.drop(df[df['Index']==int(i)].index, inplace=True)
            
            # replace rows in case something changed
            for i in range(0,data.shape[0]):
                idx = data.iloc[i]['Index']
                if pd.isnull(idx)==True:
                    df = pd.concat([df,pd.DataFrame(data.iloc[i]).T])
                else:
                    df.loc[df['Index']==idx] = data.iloc[i].to_list()
        
        # save new df
        df.reset_index(drop=True,inplace=True)
        dump_df(df)
        
        # define remaining outputs
        n_clicks_save=0
        pm_opt = get_project_managers(df)
        if str(pm) not in pm_opt:
            pm = pm_opt[0]
        return n_clicks_save, n_clicks_load, pm_opt, pm, n_clicks_uw, opt_day_radio, val_day_radio
    
    # if the load excel button is clicked
    elif n_clicks_load > 0:
        # load df
        df = pd.read_excel(r"Projectdata_rev3.xlsx")
        df_original_cols = deepcopy(df.columns)
        cols=[]
        for col in df.columns:
            # process column names
            cols.append(str(col).replace('\n',' '))
        df.columns = cols
        # save df in cache
        dump_df(df)
        dump_org_cols(df_original_cols)
        
        # define remaining outputs
        n_clicks_load=0
        pm_opt = get_project_managers(df)
        if str(pm) not in pm_opt:
            pm = pm_opt[0]
        return n_clicks_save, n_clicks_load, pm_opt, pm, n_clicks_uw, opt_day_radio, val_day_radio
    
    # if the update weather button is clicked
    elif n_clicks_uw > 0:
        df = load_df()
        
        # load weather data from DWD with Brightsky API
        all_weather_dict = get_weatherdata(df)
        
        # integrate code here to get alpha or z0 from df
        # put function here to extrapolate from 10m to 100m WS
        for loc in all_weather_dict:
            all_weather_dict[loc]['wind_speed_100m'] = all_weather_dict[loc]['wind_speed'].multiply(1.5)
        opt_day_radio = get_daily_weather(all_weather_dict)[1]
        val_day_radio = get_daily_weather(all_weather_dict)[1][1]
        # save weather data to cache
        dump_weather(all_weather_dict)
        
        # define remaining outputs
        n_clicks_uw=0
        pm_opt = get_project_managers(df)
        if str(pm) not in pm_opt:
            pm = pm_opt[0]
        return n_clicks_save, n_clicks_load, pm_opt, pm, n_clicks_uw, opt_day_radio, val_day_radio
    
    else:
        raise PreventUpdate

@app.callback(
    Output('save-dfexcl-button', 'n_clicks'),
    Input('save-dfexcl-button', 'n_clicks'),
    )
def update_excel(n_clicks):
    '''
    Export excel. Possible to overwrite excel.
    '''
    if n_clicks > 0:
        df = load_df()
        # delete helper columns
        if 'Alle_Index' in df.columns:
            df.drop(['Alle_Index'],axis=1, inplace=True)
        if 'Index' in df.columns:
            df.drop(['Index'],axis=1, inplace=True)
        df.columns = load_org_cols()
        df.to_excel('test.xlsx', index=False) # change this path later
        n_clicks=0
        return n_clicks
    else:
        raise PreventUpdate
            
if __name__ == "__main__":
    # ------ load data initialy
    df = pd.read_excel(r"Projectdata_rev3.xlsx")
    df_original_cols = deepcopy(df.columns)
    cols=[]
    for col in df.columns:
        cols.append(str(col).replace('\n',' '))
    df.columns = cols
    dump_org_cols(df_original_cols)
    dump_df(df)

    all_weather_dict = get_weatherdata(df)
    # with open('weather_data.pickle', 'rb') as handle:
    #     all_weather_dict = pickle.load(handle)
    for loc in all_weather_dict:
        all_weather_dict[loc]['wind_speed_100m'] = all_weather_dict[loc]['wind_speed'].multiply(1.5)
    dump_weather(all_weather_dict)
    # -----------------------
    app.run_server(debug=True)
    