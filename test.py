import pandas as pd
import pickle
import json
import os
import sys
from weather import get_weatherdata, daily_mean, get_locs_lats_lons # import weather data funtions

''''
with open('cache/weather_data.pickle', 'rb') as handle:
    df = pickle.load(handle)

#df.to_csv('df_data.csv')

json_obj = json.loads(json.dumps(df))

# write the json file
with open('weather_data.json', 'w', encoding='utf-8') as outfile:
    json.dump(json_obj, outfile, ensure_ascii=False, indent=4)

'''
'''
def load_weather():
    f = open('weather_data.json')

    df = json.load(f)
    return df

all_weather_dict = load_weather()

daily_weather = {}

for key, weather_df in all_weather_dict.items():
        print(weather_df)
        #daily_weather[key] = daily_mean(weather_df, 'wind_speed', 'wind_speed_100m', 'wind_direction')
'''
'''
def load_weather():
    #Loads weather-dict from cache
    
    with open('cache/weather_data.pickle', 'rb') as handle:
        all_weather_dict = pickle.load(handle)
    return all_weather_dict

all_weather_dict = load_weather()

daily_weather = {}

for key, weather_df in all_weather_dict.items():
        print(type(weather_df))
        #daily_weather[key] = daily_mean(weather_df, 'wind_speed', 'wind_speed_100m', 'wind_direction')
'''

df = pd.read_csv("df_data.csv")

df.info()