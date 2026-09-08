import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  ScrollView,
} from 'react-native';
import MapView, { Marker } from 'react-native-maps';
import { useDispatch, useSelector } from 'react-redux';
import { setMapCenter, setMarkers } from '../store/slices/mapSlice';
import mapService from '../services/mapService';

const MapScreen = () => {
  const dispatch = useDispatch();
  const { center, markers } = useSelector(state => state.map);
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedService, setSelectedService] = useState(null);

  useEffect(() => {
    const mockServices = mapService.getMockServices();
    dispatch(setMarkers(mockServices));
  }, []);

  const handleSearch = async () => {
    setIsLoading(true);
    try {
      const results = await mapService.searchServices(searchQuery);
      dispatch(setMarkers(results));
    } catch (error) {
      console.log('خطا:', error);
    }
    setIsLoading(false);
  };

  return (
    <View style={styles.container}>
      <View style={styles.searchContainer}>
        <TextInput
          style={styles.searchInput}
          placeholder="جستجو..."
          placeholderTextColor="#a0aec0"
          value={searchQuery}
          onChangeText={setSearchQuery}
        />
        <TouchableOpacity style={styles.searchButton} onPress={handleSearch} disabled={isLoading}>
          {isLoading ? <ActivityIndicator color="white" /> : <Text style={styles.searchButtonText}>🔍</Text>}
        </TouchableOpacity>
      </View>

      <MapView
        style={styles.map}
        initialRegion={{
          latitude: center.lat,
          longitude: center.lng,
          latitudeDelta: 0.05,
          longitudeDelta: 0.05,
        }}
      >
        {markers.map(marker => (
          <Marker
            key={marker.id}
            coordinate={{ latitude: marker.lat, longitude: marker.lng }}
            onPress={() => setSelectedService(marker)}
          >
            <View style={styles.markerIcon}>
              <Text style={styles.markerText}>📍</Text>
            </View>
          </Marker>
        ))}
      </MapView>

      {selectedService && (
        <View style={styles.detailsPanel}>
          <Text style={styles.detailsTitle}>{selectedService.name}</Text>
          <Text style={styles.detailsText}>📍 {selectedService.address}</Text>
          <Text style={styles.detailsText}>📞 {selectedService.phone}</Text>
          <Text style={styles.detailsText}>⭐ {selectedService.rating}</Text>
          <TouchableOpacity style={styles.directionsButton}>
            <Text style={styles.directionsButtonText}>🧭 مسیریابی</Text>
          </TouchableOpacity>
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: 'white' },
  searchContainer: { flexDirection: 'row-reverse', padding: 12, backgroundColor: '#667eea', gap: 8 },
  searchInput: { flex: 1, padding: 10, backgroundColor: 'white', borderRadius: 8, textAlign: 'right' },
  searchButton: { width: 44, height: 44, borderRadius: 8, backgroundColor: '#764ba2', justifyContent: 'center', alignItems: 'center' },
  searchButtonText: { fontSize: 18 },
  map: { flex: 1 },
  markerIcon: { width: 40, height: 40, borderRadius: 20, backgroundColor: '#667eea', justifyContent: 'center', alignItems: 'center', borderWidth: 2, borderColor: 'white' },
  markerText: { fontSize: 20 },
  detailsPanel: { position: 'absolute', bottom: 20, left: 20, right: 20, backgroundColor: 'white', padding: 16, borderRadius: 12, shadowColor: '#000', shadowOpacity: 0.1, shadowRadius: 4, elevation: 5 },
  detailsTitle: { fontSize: 18, fontWeight: 'bold', color: '#2d3748', marginBottom: 8, textAlign: 'right' },
  detailsText: { fontSize: 14, color: '#718096', marginBottom: 4, textAlign: 'right' },
  directionsButton: { marginTop: 12, paddingVertical: 10, backgroundColor: '#667eea', borderRadius: 8, alignItems: 'center' },
  directionsButtonText: { color: 'white', fontWeight: 'bold' },
});

export default MapScreen;
