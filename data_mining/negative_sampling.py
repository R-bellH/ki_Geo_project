import random
from datetime import datetime, timedelta
from shapely.geometry import Point, Polygon
import pandas as pd
from data_mining.get_sat2_images import call_sentinel
from tifffile import imwrite, imread
import numpy as np
import os
import time
from openmeteo_requests.Client import OpenMeteoRequestsError
import data_mining.read_weather as weather

# Define the polygons using the provided coordinates
north = Polygon([
    (44.45, 8.80),
    (45.41, 8.74),
    (45.34, 12.11),
    (44.24, 12.19)
])

south = Polygon([
    (41.329022, 13.12),
    (42.08, 12.67),
    (42.01, 14.82),
    (41.22, 15.04)
])

def generate_random_point_in_polygon(polygon):
    minx, miny, maxx, maxy = polygon.bounds
    while True:
        p = Point(random.uniform(minx, maxx), random.uniform(miny, maxy))
        if polygon.contains(p):
            return p

def generate_random_date(start_date, end_date):
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    delta = end - start
    random_days = random.randint(0, delta.days)
    random_date = start + timedelta(days=random_days)
    return random_date.strftime("%Y-%m-%d")

def generate_random_data(num_samples, start_date, end_date, polygons):
    data = []
    for _ in range(num_samples):
        date = generate_random_date(start_date, end_date)
        area = random.choice(polygons)
        point = generate_random_point_in_polygon(area)
        coordinate = (point.x, point.y)
        data.append([round(coordinate[0], 2), round(coordinate[1], 2), date])
    return pd.DataFrame(data, columns=["latitude", "longitude", "date"])

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

def collect_images(df, main_folder, client_id, client_secret):
    print("collecting images")
    for index, row in df.iterrows():
        day = row["date"]
        day_date = datetime.strptime(day, "%Y-%m-%d")
        yesterday = (day_date - timedelta(days=1)).strftime("%Y-%m-%d")
        time_interval = (yesterday, day)
        success = call_sentinel(client_id, client_secret, row, time_interval, save=True)
        print(f"success {success} on {day} in {row['latitude'], row['longitude']}")
        if success:
            dates = [(day_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(-9, 0)]
            for date in dates:
                day_date = datetime.strptime(date, "%Y-%m-%d")
                yesterday = (day_date - timedelta(days=1)).strftime("%Y-%m-%d")
                time_interval = (yesterday, date)
                call_sentinel(client_id, client_secret, row, time_interval, save=True, folder=main_folder)
                print(f"success {success} on {date} in {row['latitude'], row['longitude']}")

def try_get_weather(openmeteo_session, row, time_interval, folder, verbose=False):
    try:
        weather.get_weather(openmeteo_session, row, time_interval, verbose, save=True, folder=folder)
    except OpenMeteoRequestsError as e:
        print(e)
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

def main(n=500):
    start_date = "2022-02-01"
    end_date = "2024-06-25"
    num_samples = n
    main_folder = "sentinel_images_no_fire"
    with open('../config') as f:
        contents = f.readlines()[0].split(" ")
        client_id = contents[0]
        client_secret = contents[1]

    polygons = [north, south]
    df = generate_random_data(num_samples, start_date, end_date, polygons)
    df.to_csv("no_fire_probably.csv", index=False)

    df=pd.read_csv("no_fire_probably.csv")
    collect_images(df, main_folder, client_id, client_secret)

    entries = os.listdir(main_folder)
    rows = process_images(main_folder, entries,process=True)

    no_fire_weather = pd.DataFrame(rows, columns=["latitude", "longitude", "date"])
    gather_weather(no_fire_weather, "no_fire_weather")

if __name__ == "__main__":
    main()