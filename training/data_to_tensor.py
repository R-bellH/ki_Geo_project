import tensorflow as tf
# import keras
import tifffile
from tifffile import imread
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import os

w_features=15
days=9
hours=days*24
width=190
hight=190
bands=13

global c
global z
c,z=0,0

def data2tensor(location, date):
    """
    take location (latitude, longitude) and a date "yy-mm-dd" and return a tensor vector representations
    :returns: bands tensor (hXwXbands) (190X190X13), weather tensor (hourX(temp, 10m_speed,100m_speed) (9*24X15)
    """
    global z
    global c
    try:
        tensor_bands = read_sentinel_tiff(location, date)
        c+=1
    except Exception as e:
        #print("couldn't find picture")
        tensor_bands = tf.convert_to_tensor(np.zeros((width,hight,bands)), dtype='float32')
        z+=1
    try:
        tensor_weather = read_weather_data(location, date)
        # print("weather shape ", tensor_weather.shape)
    except Exception as e:
        #print("couldn't find weather")
        tensor_weather=tf.convert_to_tensor(np.zeros((hours,w_features)), dtype='float32')

    #print(tensor_bands.shape)
    #print(tensor_weather.shape)
    # tensor_bands = tensor_bands.astype('float32')
    # tensor_weather = tensor_weather.astype('float32')
    return tensor_bands, tensor_weather


def read_sentinel_tiff(location, date):
    path2sentinel = fr"\data_mining\sentinel_images\{location['latitude']},{location['longitude']}"
    path = os.path.abspath(os.getcwd()) + path2sentinel
    bands = imread(path + rf"\{date}.tiff")
    return tf.convert_to_tensor(bands, dtype='float32')


def read_weather_data(location, date):
    day_date = datetime.strptime(date, "%Y-%m-%d")
    dates = [(day_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(-9, 0)]
    path2weather = fr"\data_mining\weather_data\{location['latitude']},{location['longitude']}.csv"
    path = os.path.abspath(os.getcwd()) + path2weather
    weather = pd.read_csv(path, index_col=0)
    weather.drop_duplicates(inplace=True)
    weather["day"] = weather["date"].map(lambda x: x.split(" ")[0])
    weather_date = weather[weather["day"].isin(dates)]
    weather_date=weather_date.tail(9*24)
    weather_date = weather_date.drop(columns=['date', 'day'])
    weather_date = weather_date.astype(float)
    if weather_date.empty:
        raise Exception(f"couldn't find data for {date}, at : {location}")
    rows_to_add = (216 - weather_date.shape[0])
    arr_to_add = np.zeros((rows_to_add, weather_date.shape[1]), dtype=float)
    weather_date = np.vstack([weather_date, arr_to_add])

    return tf.convert_to_tensor(weather_date, dtype='float32')


def location2sentence(fires, location):
    global z
    global c
    #print(f"current location: {location}")
    day_date = datetime.strptime(location['date'], "%Y-%m-%d")
    dates = [(day_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in
             range(-9, 0)]  # sample every day for a week before
    tensor_bands_list, tensor_weather_list, labels=[], [], []
    for date in dates:
        tensor_bands, tensor_weather = data2tensor(location,date)
        tensor_bands_list.append(tensor_bands)
        tensor_weather_list.append(tensor_weather)
    sentence_bands = tf.stack(tensor_bands_list)
    sentence_weather = tf.stack(tensor_weather_list)
    # print("num find", c,"or not", z)

    return sentence_bands, sentence_weather


if __name__ == "__main__":
    # fires = pd.read_csv("data_mining\fire_news.csv")
    # fires["acq_date"] = fires["acq_date"].map(lambda x: x.split("T")[0])
    location = {"latitude": "36.68", "longitude": "14.96", "date": "2023-07-23"}
    location2sentence("_", location)
    # test
    # path2sentinel=f"data_mining\sentinel_images\40.50196,17.21493\"
    # path2weather = f"data_mining\weather_data\40.50196,17.21493.csv"
    # weather = pd.read_csv(path2weather,index_col=0)
    # weather["day"]=weather["date"].map(lambda x: x.split(" ")[0])
    # weather_date = weather[weather["day"] == "2024-05-06"]
    # weather_date.drop(columns=['date', 'day'], inplace=True)
    # location = {"latitude": '36.96', "longitude": '14.53'}
    # data = data2tensor(location,"2023-08-17")
    # tensor_weather=tf.convert_to_tensor(weather_date)
    # print(tensor_weather)
    # print(tensor_weather.shape)
    # print(type(tensor_weather))
