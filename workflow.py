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

# test function to simulate retrieving coordinates from the frontend
def get_data_from_web():
    """
    This function simulates retrieving coordinates from the frontend for testing.
    returns a hardcoded location and date.
    """
    latitude = 37
    longitude = 14.5
    date = "2024-06-30"

    location = {"latitude": latitude, "longitude": longitude, "date": date}
    return location


def get_images(location, folder):
    """
    This function retrieves satellite images for a given location and a date.
    The images are saved in the specified folder.
    """
    with open('./config') as f:
        contents = f.readlines()[0].split(" ")
        client_id = contents[0]
        client_secret = contents[1]
    day_date = datetime.strptime(location['date'], "%Y-%m-%d")
    dates = [(day_date + timedelta(days=i)).strftime("%Y-%m-%d")
             for i in range(-9, 0)]
    success = 0
    for date in dates:
        day_date = datetime.strptime(date, "%Y-%m-%d")
        yesterday = (day_date - timedelta(days=1)).strftime("%Y-%m-%d")
        time_interval = (yesterday, date)
        success += call_sentinel(client_id, client_secret,
                                 location, time_interval, save=True, folder=folder)
    return True if success >= 5 else False


def resize_image(input_data, target_size):
    """
    This function resizes an image to a target size.
    """
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
    """
    This function processes images in a given folder.
    If the process flag is True, it resizes the images to 190x190.
    It returns a list of rows, where each row is a list of latitude, longitude, and date.
    """
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
    """
    This function get weather data for a given location and time interval.
    """
    try:
        weather.get_weather(openmeteo_session, row,
                            time_interval, verbose, save=True, folder=folder)
    except OpenMeteoRequestsError as e:
        print(e)
        print("waiting")
        time.sleep(61)
        print("continued")
        try_get_weather(openmeteo_session, row, time_interval, folder, verbose)


def gather_weather(no_fire_weather, folder):
    """
    A wrapper function to gather weather data for a given location.
    initializes an openmeteo session and calls try_get_weather for each row in the dataframe.
    """
    openmeteo_session = weather.start_openmeteo_session()
    print("gathering weather")
    for index, row in no_fire_weather.iterrows():
        day = row["date"]
        day_date = datetime.strptime(day, "%Y-%m-%d")
        week_old = (day_date - timedelta(days=9)).strftime("%Y-%m-%d")
        time_interval = (week_old, day)
        try_get_weather(openmeteo_session, row, time_interval, folder)


def run_workflow(location):
    """
    This function runs the entire workflow for a given location (including date).
    It gets images, processes them, gathers weather data, loads a model, and makes a prediction.
    """
    images_folder = "new_data_images"
    weather_folder = "new_data_weather"
    enough_images = get_images(location, images_folder)
    if not enough_images:
        print("not enough images for analysis for the required location, please try again with another location")
        return
    location["latitude"] = str(location["latitude"])
    location["longitude"] = str(location["longitude"])

    entries = os.listdir(images_folder)
    data = process_images(images_folder, entries, process=True)
    data = pd.DataFrame(data, columns=["latitude", "longitude", "date"])
    gather_weather(data, weather_folder)

    # load the model
    path = os.path.abspath(os.getcwd()) + r"/./model.h5"
    model = tf.keras.models.load_model(path)

    location_tensor = location2sentence("_", location, images_folder, weather_folder)
    location_tensor = [tf.expand_dims(tensor, axis=0) for tensor in location_tensor]

    # predict
    prediction = model.predict(location_tensor)
    return prediction

def run_workflow_from_dataframe(locations):
    """
    This function runs the entire workflow for a list of locations.
    It gets images, processes them, gathers weather data, loads a model, and makes predictions for all locations.
    """
    images_folder = "new_data_images"
    weather_folder = "new_data_weather"
    for location in locations:
        enough_images = get_images(location, images_folder)
        if not enough_images:
            print("not enough images for analysis for the required location, please try again with another location")
        location["latitude"] = str(location["latitude"])
        location["longitude"] = str(location["longitude"])

    entries = os.listdir(images_folder)
    data = process_images(images_folder, entries, process=True)
    data = pd.DataFrame(data, columns=["latitude", "longitude", "date"])
    gather_weather(data, weather_folder)

    # load the model
    path = os.path.abspath(os.getcwd()) + r"/../model.h5"
    model = tf.keras.models.load_model(path)

    images_list,weather_list = [], []
    for location in locations:
        location_tensor = location2sentence("_", location)
        images_list.append(location_tensor[0])
        weather_list.append(location_tensor[1])

    tensor= [images_list, weather_list]

    # predict
    predictions = model.predict(tensor)
    return predictions

def run_workflow_from_path(path):
    """
    A wrapper function to run the workflow for a given a path to csv file with locations and dates.
    """
    locations = pd.read_csv(path)
    run_workflow_from_dataframe(locations)

if __name__ == '__main__':
    run_workflow(get_data_from_web())

