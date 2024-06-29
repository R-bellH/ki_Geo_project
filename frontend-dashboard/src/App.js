import React, { useState } from "react";
import MapComponent from "./components/Map";
import Sidebar from "./components/Sidebar";
import "bootstrap/dist/css/bootstrap.min.css";

const App = () => {
  const [markerPosition, setMarkerPosition] = useState([41.9028, 12.4964]); // Default coordinates for Rome

  const handleCoordinateSubmit = async (lat, lng) => {
    try {
      const response = await fetch("http://localhost:5000/coordinates", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ lat, lng }),
      });

      // TODO: add probability
      const responseData = await response.json(); // should be in the form { 'latitude': , 'longitude': }

      if (!response.ok) {
        throw new Error(responseData.message);
      }

      const { latitude, longitude } = responseData;

      setMarkerPosition([latitude, longitude]);
    } catch (error) {
      console.error("Error fetching new coordinates:", error);
    }
  };

  return (
    <div style={{ display: "flex" }}>
      <Sidebar onCoordinateSubmit={handleCoordinateSubmit} />
      <MapComponent markerPosition={markerPosition} />
    </div>
  );
};

export default App;
