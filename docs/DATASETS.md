# SMARTINFRA AI - Datasets & Normalization Guide

SmartInfra AI ingests, validates, and normalizes municipal open data from OpenCity, Pune Municipal Corporation (PMC), PMRDA, and IoT telemetry streams.

---

## Ingested Datasets

| Dataset Name | Source | Target Model | Normalization Logic |
|---|---|---|---|
| **Pune Footpaths & Roads** | [OpenCity](https://data.opencity.in/dataset/pune-footpaths-and-roads) | `InfrastructureAsset` (`ROAD`, `FOOTPATH`) | Normalizes road names, asphalt/concrete materials, coordinate geometry, assigns baseline health from road condition. |
| **Pune Sewage Network** | [OpenCity](https://data.opencity.in/dataset/pune-sewage-network) | `InfrastructureAsset` (`SEWAGE`, `DRAINAGE`) | Normalizes trunk sewer dimensions (RCC), storm drainage lines, flood retention basins. |
| **Pune Sewage Treatment Plants** | [OpenCity](https://data.opencity.in/dataset/pune-sewage-treatment-plants) | `InfrastructureAsset` (`STP`) | Normalizes plant capacity (MLD), mechanical treatment age, and location. |
| **Pune Fire Stations** | [OpenCity](https://data.opencity.in/dataset/pune-fire-stations) | `InfrastructureAsset` (`FIRE_STATION`) | Normalizes fire station locations, emergency headquarters, zonal divisions. |
| **Pune Metro DPR** | [OpenCity](https://data.opencity.in/dataset/pune-metro-detailed-project-report) | `GovernmentProject` + `InfrastructureAsset` (`METRO`) | Extracts alignment corridor, progress percentage, station nodes. |
| **Water Supply & Leaks** | PMC Water Supply Division | `InfrastructureAsset` (`PIPELINE`, `WATER_NETWORK`) | Normalizes pipe material (DI, MS, CI, HDPE), nominal diameters, attaches pressure & flow sensors. |
| **Ongoing Government Projects** | PMC & PMRDA Project Monitoring Cell | `GovernmentProject` + `Officer` | Attaches verified executive engineers, designated department, start/end dates, and official public contact numbers. |
| **IoT Sensor Registry** | Pune Smart City Telemetry Network | `Sensor` + `SensorReading` | Maps physical sensor IDs (`WP-001`, `FL-001`, `VIB-001`) to assets with engineering measurement units (`psi`, `L/min`, `mm/s`, `°C`). |

---

## Canonical Internal Schema & Provenance

Every normalized database record strictly maintains:
- `source`: Dataset or institution name (e.g., `"OpenCity Pune Footpaths and Roads"`).
- `source_url`: Public source reference link.
- `source_record_id`: Upstream source identifier if provided.
- `last_updated`: Timestamp of the latest verified synchronization.
- **Anti-Fabrication Rule:** Missing values are recorded as `null` or `"Unknown"` and are never hallucinated or artificially fabricated.
