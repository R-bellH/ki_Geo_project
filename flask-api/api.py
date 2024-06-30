'''
Provides an endpoint for clients to send coordinates for wildfire detection to an AI model.
Upon receiving the coordinates, the API processes them to determine the wildfire risk level at the specified location.
The endpoint then returns the coordinates along with the corresponding wildfire risk level.
'''

from os import wait
from time import time
from datetime import date
from flask import Flask, jsonify, request
from flask_cors import CORS
from main import main

app = Flask(__name__)

cors = CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})


def validate_coordinates(lat, lon):
    try:
        lat = float(lat)
        lon = float(lon)
    except ValueError:
        return False, "Latitude/Longitude must be numbers."

    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        return False, "Latitude/Longitude values invalid."

    return True, (lat, lon)


def get_fire_coordinates(lat, lon):
    new_lat = lat
    new_lon = lon

    today = date.today()
    today_str = today.strftime("%Y-%m-%d")

    location = {"latitude": lat, "longitude": lon, "date": today_str}
    print("before prediction")
    prediction_result = main(location) #main(location) returns a list of lists
    if prediction_result is None:
        return None

    prediction = prediction_result[0][0] * 100 if prediction_result[0] else None

    if prediction is None:
        return None




    new_coordinates = {
        'latitude': new_lat,
        'longitude': new_lon,
        'confidence': round(prediction,2)
    }
    return new_coordinates


@app.route('/coordinates', methods=['POST'])
def receive_coordinates():

    data = request.get_json()
    lat = data.get('lat')
    lon = data.get('lng')

    if not validate_coordinates(lat, lon):
        return jsonify({"error": "Invalid coordinates. Latitude must be between -90 and 90, and longitude must be between -180 and 180."}), 400

    lat = float(lat)
    lon = float(lon)
    print(lat)
    print(lon)

    new_coordinates = get_fire_coordinates(lat, lon)
    if new_coordinates is None:
        return jsonify({"error": "Not enough data to make a prediction."}), 404

    return jsonify(new_coordinates), 200


if __name__ == '__main__':
    app.run(debug=True)
