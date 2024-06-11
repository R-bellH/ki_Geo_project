import requests
import json
import pandas as pd

def _fetch_fire_news(startDate, endDate):
    url = "https://api2.effis.emergency.copernicus.eu/firenews/rest/firenews/firenews" #firenews api
    params = {
        "notify": 1, #FIXED VALUE
        #"place__icontains": <country/region/city/...>
        "startdate__gte": startDate+"T00:00:00.000Z",
        "enddate__lte": endDate+"T23:59:59.999Z",
        "simpleplace__icontains": "IT",  #2 letters ISO country code
        "ordering": "-enddate,  -startdate",
        #"limit": 20, #result limit
        "offset": 0
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Check the response status code, if it is not 200, throw an exception
        data = response.json()  # Parse the response content into JSON format
        return data
    except requests.exceptions.RequestException as e:
        print("Error fetching fire news:", e)
        return None
def fetch_fire_news(startDat, endDate, verbose=False, save=False):
    fire_news = _fetch_fire_news(startDate, endDate)
    if fire_news:
        number_of_reported_fires_italy = len(fire_news['results'])
        print("Fetched fire news successfully:")
        print(f"reported fires in italy between {startDate} and {endDate} : {number_of_reported_fires_italy}")
        latitudes = []
        longitudes = []
        dates = []

        for ans in fire_news['results']:
            coordinate = ans['geom']['coordinates']
            updated_time = ans['updated']
            latitudes.append(coordinate[0])
            longitudes.append(coordinate[1])
            dates.append(updated_time)
            if verbose:
                print("coordinates：", coordinate)
                print("updated_time：", updated_time)
                print("--------------------------------------")
        fires = pd.DataFrame(columns=["latitude", "longitude", "acq_date"])
        fires["latitude"] = latitudes
        fires["longitude"] = longitudes
        fires["acq_date"] = dates
        if save:
            fires.to_csv("fire_news.csv",index=False)
        return fires
    else:
        if verbose:
            print("Failed to fetch fire news.")


if __name__=="__main__":
    startDate = "2022-05-01"
    endDate = "2025-06-10"
    fire_news = fetch_fire_news(startDate, endDate,True,True)
    print(fire_news)
