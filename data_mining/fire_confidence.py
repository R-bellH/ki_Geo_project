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


def fetch_csv_data(url):
    response = requests.get(url, timeout=10)
    if response.status_code == 200:
        return response.text
    else:
        print("Failed to fetch CSV. Error code:", response.status_code)
        print("Response: ", response.text)
        return None


def write_csv(csv_data):
    with open("./data_mining/fire_confidence.csv", "w", newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["latitude", "longitude", "acq_date", "acq_time", "confidence"])  # write header
        for row in csv_data.splitlines():
            csv_row = row.split(',')
            if csv_row[10] == 'h': # if confidence is 'h'
                writer.writerow([csv_row[i] for i in [1, 2, 6, 7, 10]])  # write relevant elements
    print("CSV data written to 'fire_confidence.csv'.")


def append_csv(csv_data):
    with open("./data_mining/fire_confidence.csv", "a", newline='') as file:
        writer = csv.writer(file)
        for row in csv_data.splitlines():
            csv_row = row.split(',')
            if csv_row[10] == 'h':  # if confidence is 'h'
                writer.writerow([csv_row[i] for i in [1, 2, 6, 7, 10]])  # append relevant elements
    print("CSV data appended to 'fire_confidence.csv'.")


# fetch all data from data_range_start_date until today, querying in 10-day intervals starting from the current date

data_range_start_date = datetime(2022, 12, 10).date() # start date of available data
current_date = datetime(2022, 12, 10).date()

today = datetime.today().date()
data_range_end_date = today - timedelta(days=10) # define the end date as today minus 10 days

# api map key
map_key = "0808db13cedb45abe0ab70d1603c4a74"

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
        print(f"error writing csv data for {date_str}.")

    # increment the date by 10 days
    current_date += timedelta(days=10)



