# An AI-Supported Wildfire Early Warning System for the Region of Italy

![wildfire-header](img.png)

Using free and open remote sensing and weather data in combination with publicly available records of wildfires in Europe, we built an AI early warning system to predict potential fires and support local emergency response teams.

## Technical Overview

* * *

The application currently consists of the following components:

- **React Frontend:** A dashboard and map, allowing the user to submit coordinates for prediction and visualising results
- **Flask API:** Provides endpoints for interaction with the AI Model
- **Recurrent Neural Network:** A TensorFlow model built and trained on datasets from our sources listed below.
- **Data Mining and Training:** scripts for data mining, processing, and model training

![app-diagram](app_diagram.png)

As this prototype was trained with a focus on the region of Italy, the frontend currently performs this validation by cross checking input-coordinates against a geojson [polygon of Italy](https://github.com/georgique/world-geojson). Only coordinates within its borders are sent via the API to the AI model, which in turn returns a wildfire prediction score for the location. This is displayed via a marker on the map.

The satellites used for data collection are not geostationary. This means that it is possible that not enough data will be found on occasion, to make a prediction for specific coordinates. To ensure the model's accuracy and reliability, we have implemented an error message to notify users when this situation arises.

## Data Sources

* * *

All data we use for training and prediction is free and publicly available via the following sources:

### **1\. Sentinel Hub Process API**

This database provides us with full spectrum satellite imagery (Sentinel 2) from the European Space Agency's Copernicus program.

https://docs.sentinel-hub.com/api/latest/api/process/

To connect to the API from within the application, a `client_id` and `client_secret` are required. To get your credentials, create an account at https://www.sentinel-hub.com/

### **2\. Open Meteo Historical Weather API**

Open source weather API offering hourly historical data with a high number of weather variables. No key required.

https://open-meteo.com/en/docs/historical-weather-api

## Labeled Data

The next two sources provide us with historical occurences of wildfires, which have been used as training labels in this prototype.

### **1\. NASA's Fire Information for Resource Management System**

Historical active fire data from NASA's Moderate Resolution Imaging Spectroradiometer (MODIS) and the Visible Infrared Imaging Radiometer Suite (VIIRS) onboard various satellites. Only dates and coordinates with a fire confidence of 'high' are used.

https://firms.modaps.eosdis.nasa.gov/api/country/

request an API key at https://firms.modaps.eosdis.nasa.gov/api/map_key/

### **2\. Firenews API**

Historical geolocated database of European fires reported on the internet

https://api2.effis.emergency.copernicus.eu/firenews/rest/firenews/firenew

## Running the App

* * *

**1\. Clone the repository**
`git clone https://github.com/R-bellH/ki_Geo_project.git`

**2\. Create a config file**
Create a `config` file in root, which contains the Sentinel Hub API keys. Credentials can be obtained by creating a free account here: https://www.sentinel-hub.com/

The keys should be listed in the following order in the file:
&lt;clientID&gt; &lt;clientSecret&gt;

**3\. Install Python and Node dependencies:**
`pip install -r requirements.txt`

from the frontend-dashboard, run `npm install` followed by `npm run start` to start the development server on port 3000
