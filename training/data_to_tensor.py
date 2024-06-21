import tensorflow as tf
# import keras
import tifffile
from tifffile import imread
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import os

w_features=14
hours=24
width=190
hight=190
bands=13

global c
global z
c,z=0,0

def data2tensor(location, date):
    """
    take location (latitude, longitude) and a date "yy-mm-dd" and return a tensor vector representations
    :returns: bands tensor (hXwXbands) (190X190X13), weather tensor (hourX(temp, 10m_speed,100m_speed) (24X14)
    """
    global z
    global c
    try:
        tensor_bands = read_sentinel_tiff(location, date)
        c+=1
    except Exception as e:
        print("couldn't find picture")
        tensor_bands = tf.convert_to_tensor(np.zeros((width,hight,bands)), dtype='float32')
        z+=1
    try:
        tensor_weather = read_weather_data(location, date)
    except Exception as e:
        print("couldn't find weather")
        tensor_weather=tf.convert_to_tensor(np.zeros((hours,w_features)), dtype='float32')

    # print(tensor_bands)
    # print(tensor_weather)
    # tensor_bands = tensor_bands.astype('float32')
    # tensor_weather = tensor_weather.astype('float32')
    return tensor_bands, tensor_weather


def read_sentinel_tiff(location, date):
    path2sentinel = fr"\ki_Geo_project\data_mining\sentinel_images\{location['latitude']},{location['longitude']}"
    path = os.path.abspath(os.getcwd()) + path2sentinel
    bands = imread(path + f"\{date}.tiff")
    return tf.convert_to_tensor(bands, dtype='float32')


def read_weather_data(location, date):
    path2weather = fr"\ki_Geo_project\data_mining\weather_data\{location['latitude']},{location['longitude']}.csv"
    path = os.path.abspath(os.getcwd()) + path2weather
    weather = pd.read_csv(path, index_col=0)
    weather.drop_duplicates(inplace=True)
    weather["day"] = weather["date"].map(lambda x: x.split(" ")[0])
    weather_date = weather[weather["day"] == date]
    weather_date.drop(columns=['date', 'day'], inplace=True)
    weather_date = weather_date.astype(float)
    if weather_date.empty:
        raise Exception(f"couldn't find data for {date}, at : {location}")
    return tf.convert_to_tensor(weather_date, dtype='float32')


def location2sentence(fires, location):
    global z
    global c
    print(f"current location: {location}")
    #print(fires['latitude'])
    #print(location['latitude'].values)
    fire = fires[fires['latitude'] == location['latitude']]
    fire = fire[fire['longitude'] == location['longitude']]
    day_date = datetime.strptime(location['date'], "%Y-%m-%d")
    dates = [(day_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in
             range(-7, 2)]  # sample every week for a month around that date
    tensor_bands_list, tensor_weather_list, labels=[], [], []
    for date in dates:
        tensor_bands, tensor_weather = data2tensor(location,date)
        tensor_bands_list.append(tensor_bands)
        tensor_weather_list.append(tensor_weather)
        labels.append(1 if date in fire['date'].values else 0)
    sentence_bands = tf.stack(tensor_bands_list)
    sentence_weather = tf.stack(tensor_weather_list)
    print("num find or not")
    print(c,z)
    return [sentence_bands, sentence_weather], labels


if __name__ == "__main__":
    # fires = pd.read_csv("data_mining\fire_news.csv")
    # fires["acq_date"] = fires["acq_date"].map(lambda x: x.split("T")[0])
    # location = {"latitude": 8.635563034028015, "longitude": 39.95169788042532}
    # location2sentence(fires, location)
    # test
    # path2sentinel=f"data_mining\sentinel_images\40.50196,17.21493\"
    # path2weather = f"data_mining\weather_data\40.50196,17.21493.csv"
    # weather = pd.read_csv(path2weather,index_col=0)
    # weather["day"]=weather["date"].map(lambda x: x.split(" ")[0])
    # weather_date = weather[weather["day"] == "2024-05-06"]
    # weather_date.drop(columns=['date', 'day'], inplace=True)
    location = {"latitude": '36.96', "longitude": '14.53'}
    data = data2tensor(location,"2023-08-17")
    # tensor_weather=tf.convert_to_tensor(weather_date)
    # print(tensor_weather)
    # print(tensor_weather.shape)
    # print(type(tensor_weather))
