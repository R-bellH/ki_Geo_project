import pandas as pd
import numpy as np
from datetime import datetime

def get_new_locations(df_fire_conf, df_fire_news):
    # Convert dates to datetime objects to ensure proper comparison
    df_fire_conf['date'] = pd.to_datetime(df_fire_conf['date'])
    df_fire_news['date'] = pd.to_datetime(df_fire_news['date'])

    # Group data by date in both dataframes
    grouped_conf = df_fire_conf.groupby('date')
    grouped_news = df_fire_news.groupby('date')

    new_locations  = []
    #Iterate over each group in df_fire_news
    for date, group_news in grouped_news:
        print(date)
        # Check if the date exists in df_fire_conf
        if date in grouped_conf.groups:
            print("Matching fires from confidence dataset:")
            group_conf = grouped_conf.get_group(date)
            # print(group_conf)
            # print(group_news)
            # Iterate over each row in group_news and compare with group_conf
            for index_news, row_news in group_news.iterrows():
                # Compare with all rows in group_conf
                match_found = False
                for index_conf, row_conf in group_conf.iterrows():
                    # Calculate absolute differences
                    lat_diff = abs(row_news['latitude'] - row_conf['latitude'])
                    lon_diff = abs(row_news['longitude'] - row_conf['longitude'])

                    # Check if differences between points exceed 0.1 degree
                    if lat_diff <= 0.1 and lon_diff <= 0.1:
                        match_found = True
                        break

                # If no match found, consider it a new location
                if not match_found:
                    new_locations.append({
                        'latitude': row_news['latitude'],
                        'longitude': row_news['longitude'],
                        'date': date,
                        'time': row_news['time']
                    })
        else:
            print("No matching fires found in confidence dataset.")
            # print(group_news)

        print("-------------------------------------")

    df_new_locations = pd.DataFrame(new_locations)
    df_new_locations.to_csv('./fire_labels/new_locations_from_firenews.csv', index=False)

def clean_and_merge():
    df_fire_conf = pd.read_csv('./fire_confidence/fire_confidence_clean.csv')
    df_new_locations_from_firenews = pd.read_csv('./fire_labels/new_locations_from_firenews.csv', dtype={'time': str})

    columns_to_append = ['latitude_clean', 'longitude_clean', 'date', 'time']
    df_to_append = df_fire_conf[columns_to_append]

    # Rename columns in df_to_append to match df_new_locations_from_firenews
    df_to_append.columns = ['latitude', 'longitude', 'date', 'time']

    df_combined = pd.concat([df_new_locations_from_firenews, df_to_append], ignore_index=True)

    #confirm merge
    if len(df_combined) == len(df_new_locations_from_firenews) + len(df_fire_conf):
        print("merge successful")
    else:
        print("merge failed")

    # save to CSV
    df_combined.to_csv('./fire_labels/fire_labels_final.csv', index=False)

def run():
    df_fire_conf = pd.read_csv('./fire_confidence/fire_confidence_clean.csv')
    df_fire_news = pd.read_csv('./fire_news/fire_news_clean.csv', dtype={'time': str})
    get_new_locations(df_fire_conf, df_fire_news)
    clean_and_merge()
if __name__ == "__main__":
    df_fire_conf = pd.read_csv('./fire_confidence/fire_confidence_clean.csv')
    df_fire_news = pd.read_csv('./fire_news/fire_news_clean.csv', dtype={'time': str})
    get_new_locations(df_fire_conf, df_fire_news)
    clean_and_merge()