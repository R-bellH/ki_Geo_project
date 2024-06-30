import React, { useState, useEffect } from "react";
import italyGeoJSON from "./../italy-polygon.json";
import * as turf from "@turf/turf";

const Sidebar = ({ onCoordinateSubmit, error }) => {
  const [lat, setLat] = useState("");
  const [lng, setLng] = useState("");
  const [latError, setLatError] = useState(false);
  const [lngError, setLngError] = useState(false);
  const [geoJSONError, setGeoJSONError] = useState(false);

  useEffect(() => {
    if (!italyGeoJSON || !italyGeoJSON.features) {
      setGeoJSONError(true);
      console.error("Failed to load Italy GeoJSON file.");
    }
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();

    const latValue = parseFloat(lat);
    const lngValue = parseFloat(lng);

    // input validation: coordinates must be numerical
    const latIsNumber = !isNaN(latValue);
    const lngIsNumber = !isNaN(lngValue);

    if (!latIsNumber || !lngIsNumber) {
      setLatError(!latIsNumber ? "Latitude must be a number." : "");
      setLngError(!lngIsNumber ? "Longitude must be a number." : "");
      console.error("Invalid input. Coordinates must be numerical");
      return;
    }

    // input validation: coordinates must be within Italy
    const isWithinItaly = coordinatesWithinItaly([latValue, lngValue]);

    setLatError(!isWithinItaly ? "Coordinates must be within Italy" : "");
    setLngError(!isWithinItaly ? "Coordinates must be within Italy" : "");

    if (latIsNumber && lngIsNumber && isWithinItaly) {
      onCoordinateSubmit(lat, lng);
      setLat("");
      setLng("");
    }
  };

  // Function to check if coordinates are within Italy
  function coordinatesWithinItaly([lat, lng]) {
    if (geoJSONError) {
      console.error("GeoJSON file error. Cannot validate coordinates.");
      return false;
    }

    const point = turf.point([lng, lat]);

    const isWithinItaly = italyGeoJSON.features.some((feature) => {
      const polygon = turf.polygon(feature.geometry.coordinates);
      return turf.booleanPointInPolygon(point, polygon);
    });

    if (isWithinItaly) {
      console.log("Coordinates are within Italy");
      return true;
    } else {
      console.log("Coordinates are outside Italy");
      return false;
    }
  }

  // Conditionally set bootstrap class based on errors
  return (
    <div style={{ width: "25%", padding: "20px" }}>
      <h2 className="mb-4">Wildfire Early Warning System for the region of Italy</h2>

      <p>
        <b>Enter Coordinates</b> of area to monitor for wildfire risk
      </p>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>
            Latitude:
            <input
              type="text"
              className={`form-control ${latError ? "is-invalid" : ""}`}
              value={lat}
              onChange={(e) => setLat(e.target.value)}
            />
            {latError && <div className="invalid-feedback">{latError}</div>}
          </label>
        </div>
        <div className="form-group">
          <label>
            Longitude:
            <input
              type="text"
              className={`form-control ${lngError ? "is-invalid" : ""}`}
              value={lng}
              onChange={(e) => setLng(e.target.value)}
            />
            {lngError && <div className="invalid-feedback">{lngError}</div>}
          </label>
        </div>
        <button type="submit" className="btn btn-primary btn-lg btn-block mt-3">
          Submit
        </button>
      </form>
    </div>
  );
};

export default Sidebar;
