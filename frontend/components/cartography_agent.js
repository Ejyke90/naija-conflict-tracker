import React from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

const ConflictMap = ({ positions }) => {
  return (
    <MapContainer center={[9.0820, 8.6753]} zoom={6} style={{ height: '400px', width: '100%' }}>
      <TileLayer url='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png' />
      {positions.map((pos, index) => (
        <Marker key={index} position={[pos.lat, pos.lon]}>
          <Popup>{pos.location}</Popup>
        </Marker>
      ))}
    </MapContainer>
  );
};

export default ConflictMap;
