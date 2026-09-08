import { create } from "zustand";

export const useMapStore = create((set, get) => ({
  // Map state
  center: { lat: 27.1832, lng: 56.2666 },
  zoom: 13,
  userLocation: null,
  destination: null,
  route: null,

  // Layers visibility
  layers: {
    traffic: true,
    cameras: true,
    pois: true,
    tourism: true,
    accidents: false,
    hotspots: false,
    route: false,
  },

  // Selection
  selectedPoi: null,
  selectedCamera: null,
  selectedHotspot: null,

  // Navigation
  navigation: {
    active: false,
    distance: 0,
    duration: 0,
  },

  // Actions
  setCenter: (center) => set({ center }),
  setZoom: (zoom) => set({ zoom }),
  setUserLocation: (userLocation) => set({ userLocation }),
  setDestination: (destination) => set({ destination }),
  setRoute: (route) => set({ route }),

  toggleLayer: (layer) =>
    set((state) => ({
      layers: { ...state.layers, [layer]: !state.layers[layer] },
    })),

  setLayer: (layer, value) =>
    set((state) => ({
      layers: { ...state.layers, [layer]: value },
    })),

  setSelectedPoi: (selectedPoi) => set({ selectedPoi }),
  setSelectedCamera: (selectedCamera) => set({ selectedCamera }),
  setSelectedHotspot: (selectedHotspot) => set({ selectedHotspot }),

  startNavigation: (distance, duration) =>
    set({
      navigation: { active: true, distance, duration },
    }),

  stopNavigation: () =>
    set({
      navigation: { active: false, distance: 0, duration: 0 },
      route: null,
      destination: null,
    }),

  reset: () =>
    set({
      destination: null,
      route: null,
      selectedPoi: null,
      selectedCamera: null,
      selectedHotspot: null,
      navigation: { active: false, distance: 0, duration: 0 },
    }),
}));
