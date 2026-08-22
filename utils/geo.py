import math
from typing import List, Tuple, Dict, Any, Optional
from shapely.geometry import Point, LineString, Polygon, shape
from shapely import wkt


# Earth radius in meters
EARTH_RADIUS_METERS = 6371000.0


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two points on the Earth in meters.
    """
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    return EARTH_RADIUS_METERS * c


def get_bounding_box(lat: float, lon: float, radius_meters: float) -> Tuple[float, float, float, float]:
    """
    Return (min_lat, max_lat, min_lon, max_lon) for an approximate bounding box given radius in meters.
    """
    # 1 deg latitude is approx 111,320 meters
    lat_delta = radius_meters / 111320.0
    # 1 deg longitude varies with latitude
    lon_delta = radius_meters / (111320.0 * math.cos(math.radians(lat)))

    return (lat - lat_delta, lat + lat_delta, lon - lon_delta, lon + lon_delta)


def point_to_wkt(lat: float, lon: float) -> str:
    """Create WKT representation for a Point."""
    return f"POINT({lon} {lat})"


def is_point_near_polyline(lat: float, lon: float, polyline_coords: List[Tuple[float, float]], buffer_meters: float = 500.0) -> bool:
    """
    Check if a (lat, lon) point is within buffer_meters of a polyline given as [(lat, lon), ...].
    """
    if not polyline_coords or len(polyline_coords) < 2:
        if polyline_coords and len(polyline_coords) == 1:
            p_lat, p_lon = polyline_coords[0]
            return haversine_distance(lat, lon, p_lat, p_lon) <= buffer_meters
        return False

    # Convert lat/lon coords to shapely LineString in (lon, lat) order
    # Convert meters to degrees approx
    buffer_deg = buffer_meters / 111320.0
    line = LineString([(p[1], p[0]) for p in polyline_coords])
    point = Point(lon, lat)
    
    return line.distance(point) <= buffer_deg


def decode_polyline(encoded_polyline: str) -> List[Tuple[float, float]]:
    """
    Decodes a Google encoded polyline string into a list of (latitude, longitude) tuples.
    """
    points = []
    index = 0
    length = len(encoded_polyline)
    lat = 0
    lng = 0

    while index < length:
        # Decode Latitude
        shift = 0
        result = 0
        while True:
            byte = ord(encoded_polyline[index]) - 63
            index += 1
            result |= (byte & 0x1F) << shift
            shift += 5
            if byte < 0x20:
                break
        dlat = ~(result >> 1) if (result & 1) else (result >> 1)
        lat += dlat

        # Decode Longitude
        shift = 0
        result = 0
        while True:
            if index >= length:
                break
            byte = ord(encoded_polyline[index]) - 63
            index += 1
            result |= (byte & 0x1F) << shift
            shift += 5
            if byte < 0x20:
                break
        dlng = ~(result >> 1) if (result & 1) else (result >> 1)
        lng += dlng

        points.append((lat * 1e-5, lng * 1e-5))

    return points
