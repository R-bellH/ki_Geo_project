import os

import openmeteo_requests

import requests_cache
import pandas as pd
from retry_requests import retry


# Setup the Open-Meteo API client with cache and retry on error
def start_openmeteo_session():
    cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)
    return openmeteo


# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
def get_weather(openmeteo_session, coordinates, time_interval, verbose=False, save=False):
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": coordinates['latitude'],
        "longitude": coordinates['longitude'],
        "start_date": f"{time_interval[0]}",
        "end_date": f"{time_interval[1]}",
        "hourly": ["temperature_2m", "wind_speed_10m", "wind_speed_100m"]
    }
    responses = openmeteo_session.weather_api(url, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]
    if verbose:
        print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
        print(f"Elevation {response.Elevation()} m asl")
        print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
        print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

    # Process hourly data. The order of variables needs to be the same as requested.
    hourly = response.Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
    hourly_wind_speed_10m = hourly.Variables(1).ValuesAsNumpy()
    hourly_wind_speed_100m = hourly.Variables(2).ValuesAsNumpy()

    hourly_data = {"date": pd.date_range(
        start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
        end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=hourly.Interval()),
        inclusive="left"
    )}
    hourly_data["temperature_2m"] = hourly_temperature_2m
    hourly_data["wind_speed_10m"] = hourly_wind_speed_10m
    hourly_data["wind_speed_100m"] = hourly_wind_speed_100m

    hourly_dataframe = pd.DataFrame(data=hourly_data)
    if verbose:
        print(hourly_dataframe)
    if save:
        folder = f"weather_data"
        os.makedirs(folder, exist_ok=True)
        hourly_dataframe.to_csv(folder+f"/{coordinates['latitude']},{coordinates['longitude']}.csv")
    return hourly_dataframe

if __name__=="__main__":
    coordinates = {
        "latitude": 40.50196,
        "longitude": 17.21493,
    }
    time_interval=("1960-05-12","1960-05-13")
    session=start_openmeteo_session()
    print(get_weather(session,coordinates, time_interval,verbose=True))
