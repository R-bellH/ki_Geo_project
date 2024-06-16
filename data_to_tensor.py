# import tensorflow as tf
# import keras
import tifffile
from tifffile import imread
import numpy as np
import pandas as pd
from datetime import datetime, timedelta


def data2tensor(location, date):
    """
    take location (latitude, longitude) and a date "yy-mm-dd" and return a tensor vector representations
    :returns: bands tensor (hXwXbands) (117X190X13), weather tensor (hourX(temp, 10m_speed,100m_speed) (24X3)
    """
    tensor_bands = read_sentinel_tiff(location, date)
    tensor_weather = read_weather_data(location, date)
    stacked_word_tensor=tf.stack(tensor_bands, tensor_weather)
    return stacked_word_tensor


def read_sentinel_tiff(location, date):
    path2sentinel = f"data_mining/sentinel_images/{location['latitude'], location['longitude']}"
    bands = imread(path2sentinel + f"{date}.tiff")
    return tf.convert_to_tensor(bands)


def read_weather_data(location, date):
    path2weather = f"data_mining/weather_data/{location['latitude'], location['longitude']}.csv"
    weather = pd.read_csv(path2weather, index_col=0)
    weather["day"] = weather["date"].map(lambda x: x.split(" ")[0])
    weather_date = weather[weather["day"] == date]
    weather_date.drop(columns=['date', 'day'], inplace=True)
    return tf.convert_to_tensor(weather_date)


def location2sentence(fires, location):
    fire = fires[fires['latitude'] == location['latitude']]
    fire = fire[fire['longitude'] == location['longitude']]

    dates = []
    for day in fire.iterrows():
        day = day[1]["acq_date"].split("T")[0]
        # generate area around the date
        day_date = datetime.strptime(day, "%Y-%m-%d")
        # dates = [(day_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(-15, 16)] # get 30 days around that date
        _dates = [(day_date + timedelta(weeks=i)).strftime("%Y-%m-%d") for i in
                  range(-2, 2)]  # sample every week for a month around that date
        dates = dates + _dates

    tensor_list=[]
    for date in dates:
        tensor_list.append(data2tensor(location,date))
    sentence = tf.stack(tensor_list)
    return sentence


if __name__ == "__main__":
    fires = pd.read_csv("data_mining/fire_news.csv")
    location = {"latitude": 8.635563034028015, "longitude": 39.95169788042532}
    location2sentence(fires, location)
    # # test
    # path2sentinel=f"data_mining/sentinel_images/40.50196,17.21493/"
    # path2weather = f"data_mining/weather_data/40.50196,17.21493.csv"
    # weather = pd.read_csv(path2weather,index_col=0)
    # weather["day"]=weather["date"].map(lambda x: x.split(" ")[0])
    # weather_date = weather[weather["day"] == "2024-05-06"]
    # weather_date.drop(columns=['date', 'day'], inplace=True)
    # # tensor_weather=tf.convert_to_tensor(weather_date)
    # # print(tensor_weather)
    # # print(tensor_weather.shape)
    # # print(type(tensor_weather))
