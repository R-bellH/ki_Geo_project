import React, { useState } from "react";
import MapComponent from "./components/Map";
import Sidebar from "./components/Sidebar";
import "bootstrap/dist/css/bootstrap.min.css";

const App = () => {
  const [markerPosition, setMarkerPosition] = useState([41.9028, 12.4964]); // Default coordinates for Rome
  const [confidence, setConfidence] = useState(null);
  const [errorMessage, setErrorMessage] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);

  const handleCoordinateSubmit = async (lat, lng) => {
    try {
      const response = await fetch("http://localhost:5000/coordinates", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ lat, lng }),
      });

      const responseData = await response.json(); // should be in the form { 'latitude': , 'longitude':, 'confidence': }

      if (response.status === 404) {
        setErrorMessage(`Data found for ${lat}, ${lng} is insufficient for a reliable risk prediction`);
        setConfidence(null);
        setSuccessMessage(null);
        return;
      }

      if (!response.ok) {
        throw new Error(responseData.message);
      }

      // if response is 404, pass this as a prop to the sidebar and display that error message
      // it will be a json {"error": "Not enough data to make a prediction."}

      const { latitude, longitude, confidence} = responseData;

      setMarkerPosition([latitude, longitude]);
      setConfidence(confidence);
      setErrorMessage(null);
      setSuccessMessage(`Prediction for ${lat}, ${lng} successful`);
    } catch (error) {
      console.error("Error fetching new coordinates:", error);
      setSuccessMessage(null);
    }
  };

  const resetErrorMessage = () => {
    setErrorMessage(null);
    setSuccessMessage(null);
  };

  return (
    <div style={{ display: "flex" }}>
      <Sidebar onCoordinateSubmit={handleCoordinateSubmit} errorMessage={errorMessage} resetErrorMessage={resetErrorMessage} successMessage={successMessage} />
      <MapComponent markerPosition={markerPosition} confidenceLevel={confidence} />
    </div>
  );
};

export default App;
