
from flask import Flask, request, jsonify
from data import stations
from utils import filter_by_range, haversine
from scorer import score_station

app = Flask(__name__)

@app.route("/recommend", methods=["GET"])
def recommend():
    user_lat = float(request.args.get("lat"))
    user_lon = float(request.args.get("lon"))
    battery_pct = float(request.args.get("battery", 50))
    vehicle_range_km = 200
    max_reach = (battery_pct / 100) * vehicle_range_km

    nearby = filter_by_range(user_lat, user_lon, stations, max_reach)
    results = []
    for s in nearby:
        s_copy = s.copy()
        s_copy["distance"] = haversine(user_lat, user_lon, s["lat"], s["lon"])
        s_copy["score"] = score_station(s, user_lat, user_lon)
        results.append(s_copy)

    sorted_stations = sorted(results, key=lambda x: -x["score"])
    return jsonify(sorted_stations)

if __name__ == "__main__":
    app.run(debug=True)
