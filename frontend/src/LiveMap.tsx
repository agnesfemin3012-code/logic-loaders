import { useEffect, useRef, useState } from "react";
import type { Map as LeafletMap, LayerGroup } from "leaflet";
import "leaflet/dist/leaflet.css";

import { cityCenters, riskCopy, type Asset, type City, type Risk } from "@/lib/infra-data";

const riskColor: Record<Risk, string> = {
  critical: "#e2483d",
  high: "#e0a325",
  medium: "#7c8aa0",
  low: "#2fae8b",
};

export default function LiveMap({
  city,
  items,
  selectedId,
  onSelect,
}: {
  city: City;
  items: Asset[];
  selectedId?: string | null | undefined;
  onSelect: (a: Asset) => void;
}) {
  const el = useRef<HTMLDivElement | null>(null);
  const map = useRef<LeafletMap | null>(null);
  const layer = useRef<LayerGroup | null>(null);
  const [ready, setReady] = useState(0);
  const select = useRef(onSelect);
  select.current = onSelect;

  useEffect(() => {
    let cancelled = false;
    (async () => {
      const L = (await import("leaflet")).default;
      if (cancelled || !el.current || map.current) return;
      const c = cityCenters[city];
      const m = L.map(el.current, { scrollWheelZoom: false, attributionControl: true }).setView(
        [c.lat, c.lng],
        c.zoom,
      );
      L.tileLayer("https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png", {
        attribution: "&copy; OpenStreetMap &copy; CARTO",
        maxZoom: 19,
      }).addTo(m);
      layer.current = L.layerGroup().addTo(m);
      map.current = m;
      setReady((v) => v + 1);
      // force a resize pass once mounted
      setTimeout(() => m.invalidateSize(), 200);
    })();
    return () => {
      cancelled = true;
      map.current?.remove();
      map.current = null;
      layer.current = null;
    };
  }, [city]);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      const L = (await import("leaflet")).default;
      if (cancelled || !map.current || !layer.current) return;
      layer.current.clearLayers();
      const c = cityCenters[city];
      map.current.setView([c.lat, c.lng], c.zoom, { animate: true });

      items.forEach((a) => {
        const color = riskColor[a.risk];
        const active = a.id === selectedId;
        const pulse = a.risk === "critical" || a.risk === "high";
        const icon = L.divIcon({
          className: "",
          iconSize: [22, 22],
          iconAnchor: [11, 11],
          html: `<span style="display:block;width:22px;height:22px;border-radius:9999px;background:${color};opacity:.28;${
            pulse ? "animation:si-pulse 1.8s ease-out infinite;" : ""
          }">
            <span style="position:absolute;left:5px;top:5px;width:12px;height:12px;border-radius:9999px;background:${color};box-shadow:0 0 0 ${
              active ? "4px" : "2px"
            } rgba(255,255,255,.9)"></span>
          </span>`,
        });
        const marker = L.marker([a.lat, a.lng], { icon, title: a.name }).addTo(layer.current!);
        marker.bindPopup(
          `<div style="font-family:inherit;min-width:190px">
             <strong>${a.name}</strong><br/>
             <span style="color:#64748b;font-size:12px">${a.id} · ${a.type} · ${a.ward}</span><br/>
             <span style="color:${color};font-size:12px;font-weight:600">${riskCopy[a.risk]} · health ${a.health}/100</span>
           </div>`,
        );
        marker.on("click", () => select.current(a));
        if (active) marker.openPopup();
      });
    })();
    return () => {
      cancelled = true;
    };
  }, [items, city, selectedId, ready]);

  return (
    <div className="relative">
      <style>{`@keyframes si-pulse{0%{transform:scale(.6);opacity:.5}70%{transform:scale(1.6);opacity:0}100%{opacity:0}} .leaflet-container{background:var(--color-secondary);font-family:inherit}`}</style>
      <div ref={el} className="h-[380px] w-full rounded-xl" />
    </div>
  );
}
