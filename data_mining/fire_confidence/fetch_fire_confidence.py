'''
fetches fire confidence data from the FIRMS api. returns coordinates, date, time
commented out sections with "WARNING!" must only be used when fetching data for the very first time,
or to override the existing fire_confidence.csv and start over
due to the api map key transaction limit, stop the script the moment a 403 : Exceeding allowed transaction limit
error is returned.
Adjust data_range_start_date and current_date to the date of FIRST failed attempt seen in
output, and try again after some time
this workaround will continue to append new data chronologically to the existing csv

adjusting data_range_start_date and current_date to the date after the last saved date will also allow
continual updating of the csv without having to start over again
'''

#import os
from pathlib import Path
from datetime import datetime, timedelta
import csv
import requests
import pandas as pd
import numpy as np


def fetch_csv_data(url):
    response = requests.get(url, timeout=10)
    if response.status_code == 200:
        return response.text
    else:
        print("Failed to fetch CSV. Error code:", response.status_code)
        print("Response: ", response.text)
        return None


def write_csv(csv_data):
    with open("./fire_confidence/fire_confidence.csv", "w", newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["latitude", "longitude", "acq_date", "acq_time", "confidence"])  # write header
        for row in csv_data.splitlines():
            csv_row = row.split(',')
            if csv_row[10] == 'h': # if confidence is 'h'
                writer.writerow([csv_row[i] for i in [1, 2, 6, 7, 10]])  # write relevant elements
    print("CSV data written to 'fire_confidence.csv'.")


def append_csv(csv_data):
    with open("/fire_confidence/fire_confidence.csv", "a", newline='') as file:
        writer = csv.writer(file)
        for row in csv_data.splitlines():
            csv_row = row.split(',')
            if csv_row[10] == 'h':  # if confidence is 'h'
                writer.writerow([csv_row[i] for i in [1, 2, 6, 7, 10]])  # append relevant elements
    print("CSV data appended to 'fire_confidence.csv'.")

def fetch():
    # fetch all data from data_range_start_date until today, querying in 10-day intervals starting from the current date

    data_range_start_date = datetime(2024, 6, 16).date() # start date
    current_date = datetime(2024, 6, 16).date()

    today = datetime.today().date()
    data_range_end_date = today - timedelta(days=10) # define the end date as today minus 10 days

    # api map key
    map_key = "2249b64ce48507ad117e1d491272c5e6"

    base_url = f"https://firms.modaps.eosdis.nasa.gov/api/country/csv/{map_key}/VIIRS_SNPP_NRT/ITA/10/"

    '''(WARNING! only use if wanting to fetch data all over again)'''
    # remove file if already exists before fetching data
    # data_dir = Path("./data_mining")
    # file_path = data_dir / "fire_confidence.csv"

    # if file_path.exists():
    #     file_path.unlink()


    while current_date <= data_range_end_date:

        # construct the api URL
        date_str = current_date.strftime('%Y-%m-%d')
        url = f"{base_url}{date_str}"
        print(url)

        csv_data = fetch_csv_data(url)

        if csv_data is not None:
            '''(WARNING! only use if wanting to write a new csv or completely rewrite existing csv)'''
            # if current_date == data_range_start_date:  # First iteration
            #     write_csv(csv_data)
            # else:
            #     append_csv(csv_data)
            append_csv(csv_data)
        else:
            print(f"no csv data for {date_str}.")
            break

        # increment the date by 10 days
        current_date += timedelta(days=10)

def run_clean():
    df = pd.read_csv('/fire_confidence/fire_confidence.csv')

    # round latitude and longitude to 2 decimal points
    df['latitude'] = df['latitude'].round(2)
    df['longitude'] = df['longitude'].round(2)

    # create new columns latitude_clean and longitude_clean
    df['latitude_clean'] = df['latitude']
    df['longitude_clean'] = df['longitude']
    df.rename(columns={'acq_date': 'date', 'acq_time': 'time'}, inplace=True)

    # determine if coordinates are within the same 0.2x0.2 degree tile
    def coordinates_part_of_same_tile(lat1, lon1, lat2, lon2, delta=0.2):
        return abs(lat1 - lat2) <= delta and abs(lon1 - lon2) <= delta

    # iterate over each row in the DataFrame to group coordinates
    for index, row in df.iterrows():
        lat = row['latitude']
        lon = row['longitude']

        # find all rows that are within the same 0.2x0.2 degree tile
        in_same_tile = df.apply(lambda x: coordinates_part_of_same_tile(lat, lon, x['latitude'], x['longitude']),
                                axis=1)

        # get the subset of the DataFrame that falls within the same tile
        tile_group = df[in_same_tile]

        # find the lowest left coordinate in this tile group
        lowest_lat = tile_group['latitude'].min()
        lowest_lon = tile_group['longitude'].min()

        # assign the lowest left coordinate to the latitude_clean and longitude_clean columns for the rows in this tile group
        print(f"uniting {lowest_lat} {lowest_lon} and {lat} {lon}")
        df.loc[in_same_tile, 'latitude_clean'] = lowest_lat
        df.loc[in_same_tile, 'longitude_clean'] = lowest_lon

    df.to_csv('/fire_confidence/fire_confidence_clean.csv', index=False)


def run():
    fetch()
    run_clean()


if __name__ == "__main__":
    run()

