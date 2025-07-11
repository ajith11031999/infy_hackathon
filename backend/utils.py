
import math

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = math.sin(d_lat / 2) ** 2 +         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *         math.sin(d_lon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    return R * c

def filter_by_range(user_lat, user_lon, stations, max_km):
    return [
        s for s in stations
        if haversine(user_lat, user_lon, s["lat"], s["lon"]) <= max_km
    ]
