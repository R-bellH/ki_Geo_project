import os

import openmeteo_requests

import requests_cache
import pandas as pd
from retry_requests import retry
from datetime import datetime

# Setup the Open-Meteo API client with cache and retry on error
def start_openmeteo_session():
    """
    This function sets up the Open-Meteo API client with cache and retry on error.
    :return: Open-Meteo API client.
    """
    cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)
    return openmeteo


# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
def get_weather(openmeteo_session, coordinates, time_interval, verbose=False, save=False,folder="weather_data"):
    """
    This function gets weather data for a given location and time interval.

    :param openmeteo_session: The Open-Meteo API client.
    :param coordinates: The coordinates of the location.
    :param time_interval: The start and end dates of the time interval.
    :param verbose: Whether to print verbose output. Defaults to False.
    :param save: Whether to save the weather data. Defaults to False.
    :param folder: The folder to save the weather data. Defaults to "weather_data".
    :return: The weather data as a pandas DataFrame.
    """
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": coordinates['latitude'],
        "longitude": coordinates['longitude'],
        "start_date": time_interval[0],
        "end_date": time_interval[1],
        "hourly": ["temperature_2m", "relative_humidity_2m", "apparent_temperature", "precipitation", "rain",
                   "wind_speed_10m", "soil_temperature_0_to_7cm", "soil_temperature_7_to_28cm",
                   "soil_temperature_28_to_100cm", "soil_temperature_100_to_255cm", "soil_moisture_0_to_7cm",
                   "soil_moisture_7_to_28cm", "soil_moisture_28_to_100cm", "soil_moisture_100_to_255cm"]
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
    hourly_relative_humidity_2m = hourly.Variables(1).ValuesAsNumpy()
    hourly_apparent_temperature = hourly.Variables(2).ValuesAsNumpy()
    hourly_precipitation = hourly.Variables(3).ValuesAsNumpy()
    hourly_rain = hourly.Variables(4).ValuesAsNumpy()
    hourly_wind_speed_10m = hourly.Variables(5).ValuesAsNumpy()
    hourly_soil_temperature_0_to_7cm = hourly.Variables(6).ValuesAsNumpy()
    hourly_soil_temperature_7_to_28cm = hourly.Variables(7).ValuesAsNumpy()
    hourly_soil_temperature_28_to_100cm = hourly.Variables(8).ValuesAsNumpy()
    hourly_soil_temperature_100_to_255cm = hourly.Variables(9).ValuesAsNumpy()
    hourly_soil_moisture_0_to_7cm = hourly.Variables(10).ValuesAsNumpy()
    hourly_soil_moisture_7_to_28cm = hourly.Variables(11).ValuesAsNumpy()
    hourly_soil_moisture_28_to_100cm = hourly.Variables(12).ValuesAsNumpy()
    hourly_soil_moisture_100_to_255cm = hourly.Variables(13).ValuesAsNumpy()
    day_of_year = datetime.strptime(time_interval[1], "%Y-%m-%d").timetuple().tm_yday

    hourly_data = {"date": pd.date_range(
        start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
        end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=hourly.Interval()),
        inclusive="left"
    )}
    hourly_data["temperature_2m"] = hourly_temperature_2m
    hourly_data["relative_humidity_2m"] = hourly_relative_humidity_2m
    hourly_data["apparent_temperature"] = hourly_apparent_temperature
    hourly_data["precipitation"] = hourly_precipitation
    hourly_data["rain"] = hourly_rain
    hourly_data["wind_speed_10m"] = hourly_wind_speed_10m
    hourly_data["soil_temperature_0_to_7cm"] = hourly_soil_temperature_0_to_7cm
    hourly_data["soil_temperature_7_to_28cm"] = hourly_soil_temperature_7_to_28cm
    hourly_data["soil_temperature_28_to_100cm"] = hourly_soil_temperature_28_to_100cm
    hourly_data["soil_temperature_100_to_255cm"] = hourly_soil_temperature_100_to_255cm
    hourly_data["soil_moisture_0_to_7cm"] = hourly_soil_moisture_0_to_7cm
    hourly_data["soil_moisture_7_to_28cm"] = hourly_soil_moisture_7_to_28cm
    hourly_data["soil_moisture_28_to_100cm"] = hourly_soil_moisture_28_to_100cm
    hourly_data["soil_moisture_100_to_255cm"] = hourly_soil_moisture_100_to_255cm
    hourly_data["day_of_year"] = day_of_year

    hourly_dataframe = pd.DataFrame(data=hourly_data)
    if verbose:
        print(hourly_dataframe)
    if save:
        os.makedirs(folder, exist_ok=True)
        hourly_dataframe.to_csv(folder+f"/{coordinates['latitude']},{coordinates['longitude']}.csv",mode='a')
    return hourly_dataframe


if __name__=="__main__":
    coordinates = {
        "latitude": 40.50,
        "longitude": 17.21,
    }
    time_interval=("1960-05-12","1960-05-13")
    session=start_openmeteo_session()
    print(get_weather(session,coordinates, time_interval,verbose=True))
