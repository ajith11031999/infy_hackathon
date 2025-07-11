
import streamlit as st
import folium
from streamlit_folium import folium_static
from math import radians, sin, cos, sqrt, atan2

# Constants
EV_BATTERY_CAPACITY = 40  # kWh
MAX_RANGE = 200  # km
GREEN_ZONE = 80
YELLOW_ZONE = 100
WAIT_TIME_LIMIT = 30  # minutes

# Sample station data with swap battery info
stations = [
    {
        "id": "ST001", "name": "Chennai Central", "lat": 13.08, "lon": 80.27,
        "available_slots": 1, "status": "active", "power_level": "fast",
        "connector_types": ["CCS2", "Type2"], "current_vehicle_battery": 40,
        "target_battery": 80, "charger_kw": 22, "battery_type": "Li-ion 48V",
        "available_batteries": 2
    },
    {
        "id": "ST002", "name": "Velachery", "lat": 12.98, "lon": 80.22,
        "available_slots": 0, "status": "active", "power_level": "slow",
        "connector_types": ["CHAdeMO"], "current_vehicle_battery": 30,
        "target_battery": 80, "charger_kw": 7, "battery_type": "Li-ion 48V",
        "available_batteries": 0
    },
    {
        "id": "ST003", "name": "Tambaram", "lat": 12.92, "lon": 80.12,
        "available_slots": 2, "status": "maintenance", "power_level": "fast",
        "connector_types": ["CCS2"], "current_vehicle_battery": 20,
        "target_battery": 80, "charger_kw": 22, "battery_type": "Li-ion 60V",
        "available_batteries": 1
    }
]

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c

def estimate_wait_time(station):
    battery_needed = station["target_battery"] - station["current_vehicle_battery"]
    energy_needed = (battery_needed / 100) * EV_BATTERY_CAPACITY
    wait_time_hr = energy_needed / station["charger_kw"]
    return round(wait_time_hr * 60)

def classify_zone(distance, station, user_battery_type):
    wait_time = estimate_wait_time(station)
    if distance <= GREEN_ZONE:
        zone = "green"
    elif distance <= YELLOW_ZONE:
        zone = "yellow"
    else:
        zone = "red"

    if (station["status"] != "active" or
        station["available_slots"] == 0 or
        station["available_batteries"] == 0 or
        station["battery_type"] != user_battery_type or
        wait_time > WAIT_TIME_LIMIT or
        len(station["connector_types"]) == 0):
        zone = "red"

    return zone, wait_time

def filter_and_score(user_lat, user_lon, battery, plug_type, user_battery_type):
    max_km = (battery / 100) * MAX_RANGE
    results = []
    for s in stations:
        dist = haversine(user_lat, user_lon, s["lat"], s["lon"])
        if dist > max_km:
            continue
        if plug_type not in s["connector_types"]:
            continue
        zone, wait_time = classify_zone(dist, s, user_battery_type)
        score = 100 if zone == "green" else 50 if zone == "yellow" else 10
        results.append({**s, "distance": round(dist, 2), "zone": zone, "wait_time_min": wait_time, "score": score})
    return sorted(results, key=lambda x: -x["score"])

st.title("🔋 ChargeSmart - EV Charging & Battery Swap Recommendation")
user_lat = st.number_input("Your Latitude", value=13.05)
user_lon = st.number_input("Your Longitude", value=80.25)
battery = st.slider("Battery Percentage", 0, 100, 60)
charger_type = st.selectbox("Select your car's plug type", ["CCS2", "CHAdeMO", "Type2"])
battery_type = st.selectbox("Select your car's battery type", ["Li-ion 48V", "Li-ion 60V"])

if st.button("Find Stations"):
    results = filter_and_score(user_lat, user_lon, battery, charger_type, battery_type)
    st.subheader("Station Recommendations:")
    for s in results:
        emoji = "🟢" if s["zone"] == "green" else "🟡" if s["zone"] == "yellow" else "🔴"
        st.write(f"{emoji} **{s['name']}** - {s['distance']} km | Slots: {s['available_slots']} | Batteries: {s['available_batteries']} | Wait: {s['wait_time_min']} min")

    m = folium.Map(location=[user_lat, user_lon], zoom_start=12)
    folium.Marker([user_lat, user_lon], tooltip="You", icon=folium.Icon(color='blue')).add_to(m)
    for s in results:
        color = "green" if s["zone"] == "green" else "orange" if s["zone"] == "yellow" else "red"
        tooltip = f"{s['name']} ({s['zone'].capitalize()}) | {s['distance']} km | Wait: {s['wait_time_min']} min"
        folium.Marker([s["lat"], s["lon"]], tooltip=tooltip, icon=folium.Icon(color=color)).add_to(m)
    folium_static(m)
