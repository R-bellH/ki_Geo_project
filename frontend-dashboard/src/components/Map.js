import React from "react";
import {
  MapContainer,
  TileLayer,
  Marker,
  useMap,
  Tooltip,
} from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";

// Fix for known leaflet marker icon issue
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl:
    "https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon-2x.png",
  iconUrl: "https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png",
});

const MapComponent = ({ markerPosition, confidenceLevel }) => {
  if (
    !markerPosition ||
    !Array.isArray(markerPosition) ||
    markerPosition.length !== 2
  ) {
    console.error("map: invalid marker position");
    return null;
  }

  return (
    <MapContainer
      center={[markerPosition[0], markerPosition[1]]}
      zoom={7}
      style={{ height: "100vh", width: "100%" }}
    >
      <ChangeView center={[markerPosition[0], markerPosition[1]]} />
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      />
      <Marker position={[markerPosition[0], markerPosition[1]]}>
        <Tooltip permanent>Wildfire risk: {confidenceLevel} %</Tooltip>
      </Marker>
    </MapContainer>
  );
};

// Dynamically re-center map on new coordinates
function ChangeView({ center }) {
  const map = useMap();
  map.setView(center);
  return null;
}

export default MapComponent;
