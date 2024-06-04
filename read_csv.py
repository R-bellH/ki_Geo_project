#read the fire_data.csv file and extract the [latitude, longitude acq_time, daynight] columns
# example for a line in the file
# ITA,40.50196,17.21493,303.05,0.54,0.42,2024-05-07,107,N,VIIRS,n,2.0NRT,286.83,1.26,N
from datetime import datetime

fire_data = pd.read_csv("fire_data.csv")
fire_data = fire_data[["latitude", "longitude", "acq_time", "daynight"]]


def to_date(date_str):
    date_obj= datetime.strptime(date_str, "%Y-%m-%d")
    return date_obj