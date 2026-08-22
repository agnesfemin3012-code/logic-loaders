export type Risk = "critical" | "high" | "medium" | "low";

export interface Asset {
  id: string;
  name: string;
  type: "Bridge" | "Road" | "Building" | "Drainage" | "Utility";
  ward: string;
  city: string;
  risk: Risk;
  health: number;
  lastInspected: string;
  insight: string;
  action: string;
  lat: number;
  lng: number;
}

export const cities = ["Pune", "Pimpri-Chinchwad", "Nashik", "Nagpur"] as const;
export type City = (typeof cities)[number];

export const kpis: {
  id: string;
  label: string;
  value: string;
  hint: string;
  tone: "neutral" | "ok" | "warn" | "critical";
  filter: Risk | "all";
}[] = [
  { id: "assets", label: "Total assets", value: "12,482", hint: "+186 onboarded this quarter", tone: "neutral", filter: "all" },
  { id: "healthy", label: "Healthy", value: "11,910", hint: "95.4% of network", tone: "ok", filter: "low" },
  { id: "risk", label: "At risk", value: "486", hint: "+12 since last sync", tone: "warn", filter: "high" },
  { id: "critical", label: "Critical", value: "86", hint: "Action needed in 72h", tone: "critical", filter: "critical" },
];

export const assets: Asset[] = [
  {
    id: "B-104",
    name: "Mula-Mutha River Bridge",
    type: "Bridge",
    ward: "Ward 12 · Yerwada",
    city: "Pune",
    risk: "critical",
    health: 41,
    lastInspected: "18 days ago",
    insight: "Vibration signature on span 3 drifted 22% above baseline after 48 mm rainfall.",
    action: "Restrict heavy vehicles and schedule structural survey within 72 hours.",
    lat: 18.5535,
    lng: 73.8785,
  },
  {
    id: "R-338",
    name: "Nagar Road Corridor",
    type: "Road",
    ward: "Ward 8 · Kharadi",
    city: "Pune",
    risk: "high",
    health: 63,
    lastInspected: "6 days ago",
    insight: "Pothole formation rate tripled across a 2.4 km stretch; subgrade moisture elevated.",
    action: "Queue micro-surfacing before the next rainfall window.",
    lat: 18.551,
    lng: 73.943,
  },
  {
    id: "D-021",
    name: "Eastern Ward Stormwater Line",
    type: "Drainage",
    ward: "Ward 15 · Hadapsar",
    city: "Pune",
    risk: "critical",
    health: 38,
    lastInspected: "2 days ago",
    insight: "Flow pressure anomaly detected at 3 nodes; overflow probability 74% tonight.",
    action: "Deploy desilting crew and pre-position pumps at junction J-7.",
    lat: 18.5089,
    lng: 73.926,
  },
  {
    id: "C-556",
    name: "Civic Hospital Block B",
    type: "Building",
    ward: "Ward 4 · Shivajinagar",
    city: "Pune",
    risk: "medium",
    health: 78,
    lastInspected: "34 days ago",
    insight: "Facade moisture ingress on the north elevation, progressing slowly.",
    action: "Add to next quarter's waterproofing tender.",
    lat: 18.5308,
    lng: 73.847,
  },
  {
    id: "U-112",
    name: "Feeder Substation 11 kV",
    type: "Utility",
    ward: "Ward 21 · Chinchwad",
    city: "Pimpri-Chinchwad",
    risk: "high",
    health: 58,
    lastInspected: "11 days ago",
    insight: "Transformer load peaks exceed rating for 3.2 h daily during monsoon evenings.",
    action: "Rebalance feeder load and plan capacity upgrade.",
    lat: 18.6298,
    lng: 73.7997,
  },
  {
    id: "R-902",
    name: "Ring Road Flyover Approach",
    type: "Road",
    ward: "Ward 3 · Nashik East",
    city: "Nashik",
    risk: "low",
    health: 91,
    lastInspected: "9 days ago",
    insight: "Surface roughness index stable; expansion joints within tolerance.",
    action: "Continue routine 90-day inspection cycle.",
    lat: 20.011,
    lng: 73.857,
  },
  {
    id: "B-217",
    name: "Ambazari Rail Overbridge",
    type: "Bridge",
    ward: "Ward 6 · Nagpur West",
    city: "Nagpur",
    risk: "medium",
    health: 72,
    lastInspected: "27 days ago",
    insight: "Bearing displacement trending upward but inside design allowance.",
    action: "Increase sensor sampling to hourly for 30 days.",
    lat: 21.137,
    lng: 79.049,
  },
  {
    id: "D-407",
    name: "Old City Culvert Network",
    type: "Drainage",
    ward: "Ward 9 · Nashik Central",
    city: "Nashik",
    risk: "high",
    health: 55,
    lastInspected: "21 days ago",
    insight: "Silt accumulation at 61% of section; capacity reduced ahead of peak rainfall.",
    action: "Prioritise desilting in the next works order.",
    lat: 19.9975,
    lng: 73.7898,
  },
];

export const warnings = [
  {
    id: "W-001",
    priority: "P0",
    title: "Structural anomaly · Bridge B-104",
    detail: "Span 3 vibration and tilt sensors exceeded threshold for 4 consecutive readings.",
    window: "Act within 72 hours",
    risk: "critical" as Risk,
  },
  {
    id: "W-002",
    priority: "P0",
    title: "Flood risk · Hadapsar eastern wards",
    detail: "Forecast 40–65 mm rainfall meets a drainage pressure anomaly at three nodes.",
    window: "Tonight, 20:00–02:00",
    risk: "critical" as Risk,
  },
  {
    id: "W-003",
    priority: "P1",
    title: "Load exceedance · Substation U-112",
    detail: "Evening peaks above transformer rating for the eleventh consecutive day.",
    window: "This week",
    risk: "high" as Risk,
  },
  {
    id: "W-004",
    priority: "P2",
    title: "Surface degradation · Nagar Road",
    detail: "Pothole formation rate tripled over a 2.4 km stretch.",
    window: "Next 14 days",
    risk: "high" as Risk,
  },
];

export const projects = [
  { id: "P-01", name: "Riverfront bridge retrofit", progress: 62, status: "On track", budget: "₹34 Cr", ends: "Mar 2027" },
  { id: "P-02", name: "Eastern drainage augmentation", progress: 38, status: "Delayed", budget: "₹18 Cr", ends: "Nov 2026" },
  { id: "P-03", name: "Nagar Road resurfacing", progress: 84, status: "On track", budget: "₹9 Cr", ends: "Oct 2026" },
  { id: "P-04", name: "Smart streetlight rollout", progress: 47, status: "On track", budget: "₹12 Cr", ends: "Jan 2027" },
];

export const riskCopy: Record<Risk, string> = {
  critical: "Critical",
  high: "At risk",
  medium: "Watch",
  low: "Healthy",
};

export const cityCenters: Record<City, { lat: number; lng: number; zoom: number }> = {
  Pune: { lat: 18.5285, lng: 73.8745, zoom: 12 },
  "Pimpri-Chinchwad": { lat: 18.6298, lng: 73.7997, zoom: 12 },
  Nashik: { lat: 20.0045, lng: 73.8235, zoom: 12 },
  Nagpur: { lat: 21.137, lng: 79.049, zoom: 12 },
};
