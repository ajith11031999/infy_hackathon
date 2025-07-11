
def score_station(station, user_lat, user_lon):
    score = 0
    if station["status"] == "active" and station["available_slots"] > 0:
        score += 50
    if station["power_level"] == "fast":
        score += 20
    if station["available_slots"] >= 2:
        score += 10
    return score
