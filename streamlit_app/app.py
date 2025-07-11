import streamlit as st
import folium
from streamlit_folium import folium_static
from math import radians, sin, cos, sqrt, atan2

stations = [
    {"id": "CH001", "name": "Chennai Central", "lat": 13.08, "lon": 80.27, "available_slots": 3, "status": "active", "power_level": "fast"},
    {"id": "CH002", "name": "Velachery", "lat": 12.98, "lon": 80.22, "available_slots": 0, "status": "active", "power_level": "slow"},
]

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c

def filter_and_score(user_lat, user_lon, battery):
    max_km = (battery / 100) * 200
    results = []
    for s in stations:
        dist = haversine(user_lat, user_lon, s["lat"], s["lon"])
        if dist <= max_km:
            score = 0
            if s["status"] == "active" and s["available_slots"] > 0:
                score += 50
            if s["power_level"] == "fast":
                score += 20
            if s["available_slots"] >= 2:
                score += 10
            results.append({**s, "distance": round(dist, 2), "score": score})
    return sorted(results, key=lambda x: -x["score"])

st.title("🔋 ChargeSmart - EV Charging Recommendation")
user_lat = st.number_input("Your Latitude", value=13.05)
user_lon = st.number_input("Your Longitude", value=80.25)
battery = st.slider("Battery Percentage", 0, 100, 60)

if st.button("Find Nearby Chargers"):
    results = filter_and_score(user_lat, user_lon, battery)
    st.subheader(f"Top {len(results)} Recommendations:")
    for s in results:
        st.write(f"📍 **{s['name']}** - {s['distance']} km | Slots: {s['available_slots']} | Score: {s['score']}")

    m = folium.Map(location=[user_lat, user_lon], zoom_start=12)
    folium.Marker([user_lat, user_lon], tooltip="You", icon=folium.Icon(color='blue')).add_to(m)
    for s in results:
        folium.Marker(
            [s["lat"], s["lon"]],
            tooltip=f"{s['name']} - {s['available_slots']} slots",
            icon=folium.Icon(color='green' if s["available_slots"] > 0 else 'red')
        ).add_to(m)
    folium_static(m)
