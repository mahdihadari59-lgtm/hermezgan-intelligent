import { useEffect, useCallback } from "react";
import { useQuery } from "@tanstack/react-query";
import { trafficApi } from "@api/traffic.api";
import { camerasApi } from "@api/cameras.api";
import { hotspotsApi } from "@api/hotspots.api";
import { useTrafficStore } from "@stores/traffic.store";

export function useTraffic() {
  const store = useTrafficStore();

  const { data: trafficData, isLoading: trafficLoading } = useQuery({
    queryKey: ["traffic"],
    queryFn: () => trafficApi.current(),
    refetchInterval: 30000,
  });

  const { data: incidentsData } = useQuery({
    queryKey: ["incidents"],
    queryFn: () => trafficApi.incidents(),
    refetchInterval: 60000,
  });

  const { data: statsData } = useQuery({
    queryKey: ["trafficStats"],
    queryFn: () => trafficApi.stats(),
    refetchInterval: 60000,
  });

  const { data: camerasData } = useQuery({
    queryKey: ["cameras"],
    queryFn: () => camerasApi.list(),
    refetchInterval: 60000,
  });

  const { data: hotspotsData } = useQuery({
    queryKey: ["hotspots"],
    queryFn: () => hotspotsApi.list(),
    refetchInterval: 120000,
  });

  useEffect(() => {
    if (trafficData) store.setTrafficData(trafficData);
  }, [trafficData, store]);

  useEffect(() => {
    if (incidentsData) store.setIncidents(incidentsData);
  }, [incidentsData, store]);

  useEffect(() => {
    if (statsData) store.setStats(statsData);
  }, [statsData, store]);

  useEffect(() => {
    if (camerasData) store.setCameras(camerasData);
  }, [camerasData, store]);

  useEffect(() => {
    if (hotspotsData) store.setHotspots(hotspotsData);
  }, [hotspotsData, store]);

  const reportIncident = useCallback(async (data) => {
    try {
      await trafficApi.report(data);
      return true;
    } catch (error) {
      console.error("Report incident error:", error);
      return false;
    }
  }, []);

  return {
    ...store,
    trafficLoading,
    reportIncident,
  };
}
