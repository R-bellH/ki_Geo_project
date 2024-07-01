from __future__ import annotations
import os
from datetime import datetime, timedelta
from tifffile import imwrite
import pandas as pd
import requests
from sentinelhub import SHConfig, MimeType, CRS, BBox, SentinelHubRequest, DataCollection, bbox_to_dimensions, \
    MosaickingOrder
from typing import Any
import matplotlib.pyplot as plt
import numpy as np


def get_token(client_id, client_secret):
    """
    This function retrieves the access token from Sentinel Hub.
    :param client_id: The client ID for Sentinel Hub.
    :param client_secret: The client secret for Sentinel Hub.
    :return: access token.
    """
    url = 'https://services.sentinel-hub.com/auth/realms/main/protocol/openid-connect/token'
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    }
    response = requests.post(url, headers=headers, data=data)
    access_token = response.json()['access_token']
    return access_token


def get_config(client_id, client_secret):
    """
    This function sets up the configuration for Sentinel Hub.
    :param client_id: The client ID for Sentinel Hub.
    :param client_secret: The client secret for Sentinel Hub.
    :return: configuration for Sentinel Hub.
    """
    config = SHConfig()
    config.instance_id = '880e1fdd-9935-4a80-b200-0c1468b320a8'
    config.sh_client_secret = client_secret
    config.sh_client_id = client_id
    return config


def request_all_bands_sentinel(coordinates, time_interval, config):
    """
    This function requests all bands of light from Sentinel satellite for a given location and time.

    :param coordinates: coordinates of the location.
    :param time_interval: start and end dates of the time interval.
    :param config: configuration for Sentinel Hub.
    :return:
    """
    padding = 0.1
    bbox_coords_wgs = [coordinates['latitude']-0.01,
                       coordinates['longitude']-0.01,
                       coordinates['latitude'] + 2 * padding,
                       coordinates['longitude'] + 2 * padding]
    bbox = BBox(bbox_coords_wgs, crs=CRS.WGS84)
    x_size = 190
    _, y_size = bbox_to_dimensions(bbox, resolution=x_size)

    eval_script = """
                //VERSION=3
                    function setup() {
                        return {
                            input: [{
                                bands: ["B01","B02","B03","B04","B05","B06","B07","B08","B8A","B09","B10","B11","B12"],
                                units: "DN"
                            }],
                            output: {
                                bands: 13,
                                sampleType: "INT16"
                            }
                        };
                    }
                    function evaluatePixel(sample) {
                        return [sample.B01,
                                sample.B02,
                                sample.B03,
                                sample.B04,
                                sample.B05,
                                sample.B06,
                                sample.B07,
                                sample.B08,
                                sample.B8A,
                                sample.B09,
                                sample.B10,
                                sample.B11,
                                sample.B12];
                    }
                """
    input_data = SentinelHubRequest.input_data(
        data_collection=DataCollection.SENTINEL2_L1C,
        time_interval=(f'{time_interval[0]}T00:00:00Z', f'{time_interval[1]}T23:59:59Z'),
        mosaicking_order=MosaickingOrder.LEAST_CC
    )
    request = SentinelHubRequest(
        evalscript=eval_script,
        input_data=[input_data],
        responses=[SentinelHubRequest.output_response('default', MimeType.TIFF)],
        bbox=bbox,
        size=(x_size, y_size),
        config=config
    )
    image = request.get_data()[0]
    return image

def call_sentinel(client_id, client_secret, coordinates, time_interval, save=False,folder="sentinel_images"):
    """
    A wrapper function to get sentinel image for a given location and time interval.
    :param client_id: client ID for Sentinel Hub.
    :param client_secret: client secret for Sentinel Hub.
    :param coordinates: coordinates of the location.
    :param time_interval: tart and end dates of the time interval.
    :param save: Whether to save the images. Defaults to False.
    :param folder: folder to save the images. Defaults to "sentinel_images"
    :return: Whether the operation was successful.
    """
    folder = f"{folder}/{coordinates['latitude']},{coordinates['longitude']}"
    os.makedirs(folder, exist_ok=True)
    if os.path.exists(folder + f"/{time_interval[1]}.tiff"):
        print("photo already made")
        return True

    config = get_config(client_id, client_secret)
    image = request_all_bands_sentinel(coordinates, time_interval, config)
    if image.mean() == 0:
        print(
            f"Picture not found for location {coordinates['latitude']}, {coordinates['longitude']} on {time_interval[1]}")
        return False
    elif save:
        os.makedirs(folder, exist_ok=True)
        # save output as TIFF
        imwrite(folder + f"/{time_interval[1]}.tiff", image)
    else:
        plot_image(image[:, :, 12], factor=3.5 / 1e4, vmax=1)
    return True


def request_all_bands_sentinel_no_oatue2(coordinates, time_interval, access_token):
    """
    deprecated,
    can be used instead of get sentinel image
    """
    padding = 0.2
    bbox_coords_wgs = [coordinates[0] - padding, coordinates[1] - padding, coordinates[0] + padding,
                       coordinates[1] + padding]

    # The URL to make the request to
    url = 'https://services.sentinel-hub.com/api/v1/process'

    # The headers for the request
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    # The JSON payload for the request
    payload = {
        "input": {
            "bounds": {
                "properties": {
                    "crs": "http://www.opengis.net/def/crs/OGC/1.3/CRS84"
                },
                "bbox": bbox_coords_wgs
            },
            "data": [
                {
                    "type": "sentinel-2-l1c",
                    "dataFilter": {
                        "timeRange": {
                            "from": f'{time_interval[0]}T00:00:00Z',
                            "to": f'{time_interval[1]}T23:59:59Z'
                        }
                    }
                }
            ]
        },
        "output": {
            "width": 512,
            "height": 512,
            "responses": [
                {
                    "identifier": "default",
                    "format": {
                        "type": "image/tiff"
                    }
                }
            ]
        },
        "evalscript": """
        //VERSION=3
            function setup() {
                return {
                    input: [{
                        bands: ["B01","B02","B03","B04","B05","B06","B07","B08","B8A","B09","B10","B11","B12"],
                        units: "DN"
                    }],
                    output: {
                        bands: 13,
                        sampleType: "INT16"
                    }
                };
            }
            function evaluatePixel(sample) {
                return [sample.B01,
                        sample.B02,
                        sample.B03,
                        sample.B04,
                        sample.B05,
                        sample.B06,
                        sample.B07,
                        sample.B08,
                        sample.B8A,
                        sample.B09,
                        sample.B10,
                        sample.B11,
                        sample.B12];
            }
        """
    }

    # Make the POST request
    response = requests.post(url, headers=headers, json=payload)
    # this is an TIFF image
    return response.content


def plot_image(
        image: np.ndarray, factor: float = 1.0, clip_range: tuple[float, float] | None = None, **kwargs: Any
) -> None:
    """Utility function for plotting RGB images."""
    _, ax = plt.subplots(nrows=1, ncols=1, figsize=(15, 15))
    if clip_range is not None:
        ax.imshow(np.clip(image * factor, *clip_range), **kwargs)
    else:
        ax.imshow(image * factor, **kwargs)
    ax.set_xticks([])
    ax.set_yticks([])


if __name__ == '__main__':
    # example of use
    fire_data = pd.read_csv("fire_data.csv")
    fire_data = fire_data[["latitude", "longitude", "date", "daynight"]]
    with open('./config') as f:
        contents = f.readlines()[0].split(" ")
        client_id = contents[0]
        client_secret = contents[1]
    config = get_config(client_id, client_secret)
    for fire in fire_data.iterrows():
        fire = fire[1]
        # coordinates = {'latitude': fire['latitude'], 'longitude': fire[''], 'date': fire[2]}
        day = fire["date"]
        day_date = datetime.strptime(day, "%Y-%m-%d")
        yesterday = (day_date - timedelta(days=1)).strftime("%Y-%m-%d")
        time_interval = (yesterday, day)
        call_sentinel(client_id, client_secret, fire, time_interval, save=True)