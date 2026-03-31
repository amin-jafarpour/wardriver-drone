import math

def estimate_transmitter(records, A=-45.0, n=2.7, max_iter=200, lr=0.1):
    """
    Estimate transmitter location from RSSI + lat/lon samples.

    Args:
        records: list of dicts with keys:
                 { "lat": float, "lon": float, "rssi": float }
        A: RSSI at 1 meter (calibration constant)
        n: path-loss exponent
        max_iter: iterations for optimizer
        lr: learning rate for gradient descent

    Returns:
        {
            "latitude": float,
            "longitude": float,
            "mean_rssi": float,
            "num_points": int
        }
    """

    if len(records) < 2:
        raise ValueError("Need at least 2 measurements.")

    EARTH_R = 6371000.0

    # --- Mean RSSI ---
    mean_rssi = sum(r.rssi for r in records) / len(records)

    # --- Reference origin (centroid) ---
    lat0 = sum(r.latitude for r in records) / len(records)
    lon0 = sum(r.longitude for r in records) / len(records)

    lat0_rad = math.radians(lat0)

    # --- Helpers ---
    def latlon_to_xy(lat, lon):
        lat_r = math.radians(lat)
        lon_r = math.radians(lon)
        x = (lon_r - math.radians(lon0)) * math.cos(lat0_rad) * EARTH_R
        y = (lat_r - math.radians(lat0)) * EARTH_R
        return x, y

    def xy_to_latlon(x, y):
        lat = lat0 + math.degrees(y / EARTH_R)
        lon = lon0 + math.degrees(x / (EARTH_R * math.cos(lat0_rad)))
        return lat, lon

    def rssi_to_distance(rssi):
        return 10 ** ((A - rssi) / (10 * n))

    # --- Build dataset ---
    points = []
    for r in records:
        x, y = latlon_to_xy(r.latitude, r.longitude)
        d = rssi_to_distance(r.rssi)
        points.append((x, y, d, r.rssi))

    # ------------------------------------------------------------
    # CASE 1: ONLY 2 POINTS → weighted midpoint approximation
    # ------------------------------------------------------------
    if len(points) == 2:
        (x1, y1, d1, rssi1), (x2, y2, d2, rssi2) = points

        # stronger signal → closer → more weight
        w1 = 1 / (d1 + 1e-6)
        w2 = 1 / (d2 + 1e-6)

        tx = (w1 * x1 + w2 * x2) / (w1 + w2)
        ty = (w1 * y1 + w2 * y2) / (w1 + w2)

        lat, lon = xy_to_latlon(tx, ty)

        return {
            "latitude": lat, 
            "longitude": lon,
            "rssi": mean_rssi,
            "num_points": len(records),
        }
    # ------------------------------------------------------------
    # CASE 2: N ≥ 3 → gradient descent trilateration
    # ------------------------------------------------------------

    # initial guess: centroid
    tx = sum(p[0] for p in points) / len(points)
    ty = sum(p[1] for p in points) / len(points)

    for _ in range(max_iter):
        grad_x = 0.0
        grad_y = 0.0

        for x, y, d, rssi in points:
            dx = tx - x
            dy = ty - y
            dist = math.sqrt(dx*dx + dy*dy) + 1e-6

            error = dist - d

            # weight stronger RSSI higher
            w = 1 / (d + 1e-6)

            grad_x += w * error * (dx / dist)
            grad_y += w * error * (dy / dist)

        tx -= lr * grad_x
        ty -= lr * grad_y

    lat, lon = xy_to_latlon(tx, ty)

    return {
        "latitude": lat, 
        "longitude": lon,
        "rssi": mean_rssi,
        "num_points": len(records),
    }