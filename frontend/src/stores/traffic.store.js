import { create } from "zustand";

export const useTrafficStore = create((set, get) => ({
  // Data
  trafficData: [],
  incidents: [],
  cameras: [],
  hotspots: [],
  stats: null,

  // Filters
  selectedRoad: null,
  filterSeverity: "all",
  filterType: "all",

  // Loading
  loading: false,
  error: null,

  // Actions
  setTrafficData: (trafficData) => set({ trafficData }),
  setIncidents: (incidents) => set({ incidents }),
  setCameras: (cameras) => set({ cameras }),
  setHotspots: (hotspots) => set({ hotspots }),
  setStats: (stats) => set({ stats }),

  setSelectedRoad: (selectedRoad) => set({ selectedRoad }),
  setFilterSeverity: (filterSeverity) => set({ filterSeverity }),
  setFilterType: (filterType) => set({ filterType }),

  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),

  getFilteredIncidents: () => {
    const { incidents, filterSeverity, filterType } = get();
    return incidents.filter((incident) => {
      const severityMatch =
        filterSeverity === "all" || incident.severity === filterSeverity;
      const typeMatch =
        filterType === "all" || incident.type === filterType;
      return severityMatch && typeMatch;
    });
  },
}));
