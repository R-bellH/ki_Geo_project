import os
import time
from datetime import datetime, timedelta

import tensorflow as tf

import numpy as np
import pandas as pd
from tifffile import imread, imwrite

from data_mining.get_sat2_images import call_sentinel
from openmeteo_requests.Client import OpenMeteoRequestsError
import data_mining.read_weather as weather
from training.data_to_tensor import location2sentence


def get_data_from_web():
    # get coordinates and date
    # TODO: write code to take the info from the website and get it into these paramters

    # right now its just an example
    latitude = 36.68
    longitude = 14.96
    date = "2024-06-23"


    location = {"latitude": latitude, "longitude": longitude, "date": date}
    return location

def get_images(location, folder):
    client_id = '4d093505-d867-4ae4-90b0-468eb78dd9af'
    client_secret = 'UHSroMy3xUHqh0SakSXrPvCejglb2eyH'
    day_date = datetime.strptime(location['date'], "%Y-%m-%d")
    dates = [(day_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(-9, 0)]
    success=0
    for date in dates:
        day_date = datetime.strptime(date, "%Y-%m-%d")
        yesterday = (day_date - timedelta(days=1)).strftime("%Y-%m-%d")
        time_interval = (yesterday, date)
        success += call_sentinel(client_id, client_secret, location, time_interval, save=True, folder="new_data")
    return True if success >=5 else False

def resize_image(input_data, target_size):
    height, width, channels = input_data.shape
    resized_data = np.zeros((*target_size, channels), dtype=input_data.dtype)
    scale_height = target_size[0] / height
    scale_width = target_size[1] / width
    for h in range(target_size[0]):
        for w in range(target_size[1]):
            h_orig = int(h / scale_height)
            w_orig = int(w / scale_width)
            resized_data[h, w, :] = input_data[h_orig, w_orig, :]
    return resized_data

def process_images(main_folder, entries, process=False):

    if process:
        print("resizing images")
    rows = []
    for entry in entries:
        lat, long = entry.split(",")
        full_path = os.path.join(main_folder, entry)
        if os.path.isdir(full_path):
            dates = os.listdir(full_path)
            for date in dates:
                rows.append([lat, long, date.split(".")[0]])
                if process:
                    file = f"{main_folder}/{entry}/{date}"
                    image = imread(file)
                    resized_image = resize_image(image, (190, 190))
                    imwrite(file, resized_image)
    return rows
def try_get_weather(openmeteo_session, row, time_interval, folder, verbose=False):
    try:
        weather.get_weather(openmeteo_session, row, time_interval, verbose, save=True, folder=folder)
    except OpenMeteoRequestsError as e:
        print(e)
        print("waiting")
        time.sleep(61)
        print("continued")
        try_get_weather(openmeteo_session, row, time_interval, folder, verbose)

def gather_weather(no_fire_weather, folder):
    openmeteo_session = weather.start_openmeteo_session()
    print("gathering weather")
    for index, row in no_fire_weather.iterrows():
        day = row["date"]
        day_date = datetime.strptime(day, "%Y-%m-%d")
        week_old = (day_date - timedelta(days=9)).strftime("%Y-%m-%d")
        time_interval = (week_old, day)
        try_get_weather(openmeteo_session, row, time_interval, folder)
def main():
    images_folder="new_data_images"
    weather_folder="new_data_weather"
    location=get_data_from_web()
    enough_images=get_images(location,images_folder)
    if not enough_images:
        print("not enough images for analysis for the required location, please try again with another location")
        return
    location["latitude"] = str(location["latitude"])
    location["longitude"] = str(location["longitude"])

    entries = os.listdir(images_folder)
    data = process_images(images_folder, entries,process=True)
    data = pd.DataFrame(data, columns=["latitude", "longitude", "date"])
    gather_weather(data, weather_folder)

    # load the model
    path = os.path.abspath(os.getcwd()) + r"\model.h5"
    model = tf.keras.models.load_model(path)

    location_tensor=location2sentence("_",location)
    # predict
    prediction = model.predict(location_tensor)

    return prediction
