import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
from datetime import datetime
import streamlit.components.v1 as components
import math

# ----------------------------
# Helpers: parse GPGGA log
# ----------------------------

def s(x):
    """Convert any value to a JSON-safe string."""
    if x is None:
        return ""
    if isinstance(x, float) and np.isnan(x):
        return ""
    return str(x)


def set_query_params(**kwargs):
    st.query_params.clear()
    for k, v in kwargs.items():
        st.query_params[k] = str(v)

def get_query_param(key: str, default=""):
    try:
        v = st.query_params.get(key)
        if v is None:
            return default
        # streamlit may return list in some versions
        if isinstance(v, list):
            return v[0] if v else default
        return v
    except Exception:
        return default



def nmea_to_decimal(coord_str: str, hemi: str) -> float:
    """
    coord_str like: lat=4916.45 (ddmm.mmmm), lon=12311.12 (dddmm.mmmm)
    hemi: N/S/E/W
    """
    if not coord_str or coord_str == "":
        return np.nan

    val = float(coord_str)
    deg = int(val // 100)
    minutes = val - (deg * 100)
    dec = deg + minutes / 60.0

    if hemi in ["S", "W"]:
        dec *= -1
    return dec

def parse_gpgga_line(line: str):
    # Typical: $GPGGA,hhmmss.ss,lat,NS,lon,EW,fix,sats,hdop,alt,M,...
    if not line.startswith("$") or "GPGGA" not in line:
        return None
    parts = line.strip().split(",")
    if len(parts) < 6:
        return None

    t = parts[1]
    lat_str, lat_hemi = parts[2], parts[3]
    lon_str, lon_hemi = parts[4], parts[5]

    lat = nmea_to_decimal(lat_str, lat_hemi)
    lon = nmea_to_decimal(lon_str, lon_hemi)

    # Keep time as string (hhmmss) — you can later merge with UTC timestamps if needed
    return {"gpgga_time": t, "latitude": lat, "longitude": lon}

def load_flight_path(gpgga_path: str) -> pd.DataFrame:
    rows = []
    with open(gpgga_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            rec = parse_gpgga_line(line)
            if rec:
                rows.append(rec)
    df = pd.DataFrame(rows).dropna()
    return df

# ----------------------------
# Helpers: risk scoring
# ----------------------------
def risk_score(authmode: str, pairwise: str, group: str, wps: int | bool) -> tuple[int, list[str]]:
    """
    Safe, high-level risk scoring (no hacking guidance).
    """
    reasons = []
    score = 0

    a = (authmode or "").upper()
    p = (pairwise or "").upper()
    g = (group or "").upper()

    # OPEN / WEP are highest risk
    if "OPEN" in a or "NONE" in a:
        score += 60
        reasons.append("Open authentication")
    if "WEP" in a or "WEP" in p or "WEP" in g:
        score += 70
        reasons.append("WEP encryption")

    # WPS increases risk
    if bool(wps):
        score += 25
        reasons.append("WPS enabled")

    # TKIP often considered weaker than CCMP/GCMP
    if "TKIP" in p or "TKIP" in g:
        score += 25
        reasons.append("TKIP cipher")

    # Mixed modes add some risk
    if "WPA_WPA2" in a or ("WPA" in a and "WPA2" in a):
        score += 15
        reasons.append("Mixed WPA/WPA2 mode")

    return score, reasons

def risk_level(score: int) -> str:
    if score >= 70:
        return "Critical"
    if score >= 40:
        return "High"
    if score >= 20:
        return "Medium"
    return "Low"

def risk_color(level: str) -> str:
    # Folium supports color names
    return {
        "Low": "green",
        "Medium": "orange",
        "High": "red",
        "Critical": "darkred"
    }.get(level, "blue")

# ----------------------------
# Load data
# ----------------------------
st.set_page_config(page_title="Drone Wi-Fi Security Dashboard", layout="wide")
st.title("Drone Wi-Fi Security Dashboard")

WIFI_CSV = "sample_wifi_with_gps_200rows.csv"
GPGGA_LOG = "sample_gpgga_200lines.log"

@st.cache_data
def load_wifi(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    # normalize column names if needed
    df.columns = [c.strip().lower() for c in df.columns]
    # try to sort by timestamp if exists
    if "timestamp_utc" in df.columns:
        df = df.sort_values("timestamp_utc")
    return df

wifi_df = load_wifi(WIFI_CSV)

# Flight path
flight_df = load_flight_path(GPGGA_LOG)

# ----------------------------
# Build AP summary (group by BSSID if available, else SSID)
# ----------------------------
group_key = "bssid" if "bssid" in wifi_df.columns else "ssid"

# strongest detection row per AP
idx = wifi_df.groupby(group_key)["rssi_dbm"].idxmax()
strong_df = wifi_df.loc[idx].copy()

# first detection row per AP (time order)
if "timestamp_utc" in wifi_df.columns:
    first_df = wifi_df.sort_values("timestamp_utc").groupby(group_key).first().reset_index()
else:
    first_df = wifi_df.groupby(group_key).first().reset_index()

# merge strongest + first coords to allow radius estimate if you want later
use_cols_first = [group_key]
for c in ["latitude", "longitude"]:
    if c in first_df.columns:
        use_cols_first.append(c)

ap = strong_df.merge(
    first_df[use_cols_first],
    on=group_key,
    suffixes=("_strong", "_first"),
    how="left"
)

# Risk scoring (only if auth/cipher columns exist)
for col in ["authmode", "pairwise_cipher", "group_cipher", "wps"]:
    if col not in ap.columns:
        ap[col] = ""

scores = []
levels = []
reasons_all = []
for _, r in ap.iterrows():
    sc, reasons = risk_score(r.get("authmode", ""), r.get("pairwise_cipher", ""), r.get("group_cipher", ""), r.get("wps", 0))
    scores.append(sc)
    levels.append(risk_level(sc))
    reasons_all.append(", ".join(reasons) if reasons else "No major flags")

ap["risk_score"] = scores
ap["risk_level"] = levels
ap["risk_reasons"] = reasons_all

# ----------------------------
# Navigation
# ----------------------------
default_page = get_query_param("page", "Map")
page = st.sidebar.radio("Pages", ["Map", "Access Points Table", "AP Details"], index=["Map","Access Points Table","AP Details"].index(default_page) if default_page in ["Map","Access Points Table","AP Details"] else 0)

if page == "Map":
    st.subheader("Maps")
    colA, colB = st.columns([2, 1])

    with colB:
        st.markdown("### Layers")
        show_ap = st.checkbox("Access Points", value=True)
        show_risk = st.checkbox("Security Risk View (color by risk)", value=True)
        show_path = st.checkbox("Drone Flight Path", value=True)

        st.markdown("### Filters")
        min_rssi = st.slider("Minimum RSSI (dBm)", -100, 0, -85)
        allowed_levels = st.multiselect(
            "Risk Levels",
            ["Low", "Medium", "High", "Critical"],
            default=["Low", "Medium", "High", "Critical"]
        )

    # Filter APs
    ap_f = ap.copy()
    if "rssi_dbm" in ap_f.columns:
        ap_f = ap_f[ap_f["rssi_dbm"] >= min_rssi]
    ap_f = ap_f[ap_f["risk_level"].isin(allowed_levels)]

    # Choose map center
    if "latitude" in wifi_df.columns and "longitude" in wifi_df.columns:
        center = [wifi_df["latitude"].mean(), wifi_df["longitude"].mean()]
    elif len(flight_df) > 0:
        center = [flight_df["latitude"].mean(), flight_df["longitude"].mean()]
    else:
        center = [49.2827, -123.1207]  # fallback (Vancouver)

    m = folium.Map(location=center, zoom_start=16)

    # Flight path layer
    if show_path and len(flight_df) > 1:
        coords = flight_df[["latitude", "longitude"]].values.tolist()
        folium.PolyLine(coords, weight=4, opacity=0.8, tooltip="Drone Flight Path").add_to(m)
        folium.Marker(coords[0], tooltip="Start").add_to(m)
        folium.Marker(coords[-1], tooltip="End").add_to(m)

    # AP markers
    if show_ap and "latitude_strong" in ap_f.columns and "longitude_strong" in ap_f.columns:
        for _, r in ap_f.iterrows():
            ssid = s(r.get("ssid", "(hidden)"))
            bssid = s(r.get("bssid", ""))
            rssi = s(r.get("rssi_dbm", ""))
            ch = s(r.get("primary", ""))
            auth = s(r.get("authmode", ""))
            lvl = s(r.get("risk_level", "Low"))

            details_url = f"/?page=AP Details&bssid={bssid}"

            popup_text = (
                f"<b>SSID:</b> {ssid}<br>"
                f"<b>BSSID:</b> {bssid}<br>"
                f"<b>RSSI:</b> {rssi} dBm<br>"
                f"<b>Channel:</b> {ch}<br>"
                f"<b>Auth:</b> {auth}<br>"
                f"<b>Risk:</b> {lvl}<br><br>"
                f"<a href='{details_url}' target='_self'>View AP Details</a>"
            )

            marker_color = "blue"
            if show_risk:
                marker_color = risk_color(lvl)
            
            lat = float(r["latitude_strong"])
            lon = float(r["longitude_strong"])

            folium.CircleMarker(
                location=[lat, lon],
                radius=6,
                color=marker_color,
                fill=True,
                fill_opacity=0.9,
                popup=folium.Popup(popup_text, max_width=300),
                tooltip=f"{ssid} ({lvl})"
            ).add_to(m)

    with colA:
        st.markdown("### Interactive Map")
        map_html = m.get_root().render()
        components.html(map_html, height=650, width=1200)

elif page == "Access Points Table":
    st.subheader("Access Points (Detailed Table)")
    st.caption("This table contains more fields than the map popup.")

    c1, c2, c3 = st.columns(3)

    with c1:
        level_filter = st.multiselect(
            "Risk Level",
            ["Low","Medium","High","Critical"],
            default=["Low","Medium","High","Critical"]
        )

    with c2:
        ssid_query = st.text_input("Search SSID contains", "")

    with c3:
        bssid_query = st.text_input("Search BSSID contains", "")

    ap_t = ap.copy()
    ap_t = ap_t[ap_t["risk_level"].isin(level_filter)]

    if ssid_query:
        ap_t = ap_t[ap_t["ssid"].astype(str).str.contains(ssid_query, case=False)]

    if bssid_query:
        ap_t = ap_t[ap_t["bssid"].astype(str).str.contains(bssid_query, case=False)]

    preferred = [
        c for c in [
            "ssid","bssid","rssi_dbm","primary","second",
            "authmode","pairwise_cipher","group_cipher","wps",
            "bandwidth","risk_score","risk_level","risk_reasons",
            "latitude_strong","longitude_strong"
        ] if c in ap_t.columns
    ]

    st.markdown("### Click an AP to open details")

    display_cols = preferred.copy()

    ap_show = ap_t[display_cols].copy()
    ap_show.insert(0,"Select",False)

    edited = st.data_editor(
        ap_show,
        use_container_width=True,
        hide_index=True,
        disabled=[c for c in ap_show.columns if c!="Select"]
    )

    if edited["Select"].sum() > 1:
        st.warning("Select only one AP")

    selected_rows = edited[edited["Select"] == True]

    if len(selected_rows) > 0:
        selected_bssid = str(selected_rows.iloc[0]["bssid"])

        set_query_params(page="AP Details", bssid=selected_bssid)
        st.rerun()

elif page == "AP Details":
    st.subheader("Access Point Details")

    st.markdown("""
    <style>
    /* Hide sidebar only on this page */
    [data-testid="stSidebar"] {display: none;}
    /* Remove extra left padding when sidebar is hidden */
    section.main {padding-left: 2rem;}
    </style>
    """, unsafe_allow_html=True)


    c1, c2 = st.columns(2)
    with c1:
        if st.button("⬅ Back to Map"):
            set_query_params(page="Map")
            st.rerun()
    with c2:
        if st.button("⬅ Back to Table"):
            set_query_params(page="Access Points Table")
            st.rerun()



    # Prefer BSSID as key
    ap_id = get_query_param("bssid", "")
    if not ap_id:
        st.info("No AP selected. Go to Map or Table and click View Details.")
        st.stop()

    # Filter all detections for this AP
    if "bssid" in wifi_df.columns:
        det = wifi_df[wifi_df["bssid"].astype(str) == ap_id].copy()
    else:
        # fallback if bssid doesn't exist
        det = wifi_df[wifi_df["ssid"].astype(str) == ap_id].copy()

    if det.empty:
        st.warning("No detections found for this AP.")
        st.stop()

    # Compute summary
    det = det.dropna(subset=["latitude", "longitude"])
    det["rssi_dbm"] = pd.to_numeric(det["rssi_dbm"], errors="coerce")

    strongest = det.loc[det["rssi_dbm"].idxmax()]
    ssid_val = s(strongest.get("ssid", ""))

    first_seen = det["timestamp_utc"].min() if "timestamp_utc" in det.columns else ""
    last_seen  = det["timestamp_utc"].max() if "timestamp_utc" in det.columns else ""
    count_det  = len(det)

    # Risk scoring using strongest row fields
    sc, reasons = risk_score(
        strongest.get("authmode", ""),
        strongest.get("pairwise_cipher", ""),
        strongest.get("group_cipher", ""),
        strongest.get("wps", 0)
    )
    lvl = risk_level(sc)

    # Coverage estimate: radius = max distance from strongest point to all detection points
    def haversine_m(lat1, lon1, lat2, lon2):
        R = 6371000
        p1, p2 = math.radians(lat1), math.radians(lat2)
        dp = math.radians(lat2 - lat1)
        dl = math.radians(lon2 - lon1)
        a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
        return 2 * R * math.asin(math.sqrt(a))

    s_lat = float(strongest["latitude"])
    s_lon = float(strongest["longitude"])

    det["_dist_m"] = det.apply(lambda r: haversine_m(s_lat, s_lon, float(r["latitude"]), float(r["longitude"])), axis=1)
    radius_m = float(det["_dist_m"].max()) if len(det) > 1 else 10.0

    # Layout
    left, right = st.columns([2, 1])

    with right:
        st.markdown("### Summary")
        st.write(f"**SSID:** {ssid_val}")
        st.write(f"**BSSID:** {ap_id}")
        st.write(f"**Risk:** {lvl} (score: {sc})")
        st.write(f"**Detections:** {count_det}")
        st.write(f"**First seen:** {first_seen}")
        st.write(f"**Last seen:** {last_seen}")
        st.write(f"**Estimated coverage radius:** {radius_m:.1f} m")
        st.write(f"**Risk reasons:** {', '.join(reasons) if reasons else 'No major flags'}")

        st.markdown("### Actions")
        if st.button("Back to Map"):
            set_query_params(page="Map")
            st.rerun()
        if st.button("Back to Table"):
            set_query_params(page="Access Points Table")
            st.rerun()

    with left:
        st.markdown("### Coverage Map (this AP only)")

        # Map centered on strongest point
        m2 = folium.Map(location=[s_lat, s_lon], zoom_start=18)

        # Optional: add flight path context
        show_path2 = st.checkbox("Show Flight Path (context)", value=False)
        if show_path2 and len(flight_df) > 1:
            coords = flight_df[["latitude", "longitude"]].values.tolist()
            folium.PolyLine(coords, weight=3, opacity=0.6, tooltip="Drone Flight Path").add_to(m2)

        # plot detection points
        for _, r in det.iterrows():
            lat = float(r["latitude"])
            lon = float(r["longitude"])
            rssi = s(r.get("rssi_dbm", ""))
            folium.CircleMarker(
                location=[lat, lon],
                radius=3,
                fill=True,
                fill_opacity=0.7,
                popup=folium.Popup(f"RSSI: {rssi} dBm", max_width=200)
            ).add_to(m2)

        # strongest marker
        folium.Marker(
            [s_lat, s_lon],
            popup=folium.Popup(f"<b>Strongest</b><br>SSID: {ssid_val}<br>BSSID: {ap_id}<br>RSSI: {int(strongest['rssi_dbm'])} dBm", max_width=300),
            tooltip="Strongest detection"
        ).add_to(m2)

        # coverage circle
        folium.Circle(
            location=[s_lat, s_lon],
            radius=radius_m,
            color=risk_color(lvl),
            fill=True,
            fill_opacity=0.12,
            weight=2
        ).add_to(m2)

        # Render map using HTML (stable)
        map_html = m2.get_root().render()
        components.html(map_html, height=650, width=1200)

    st.markdown("### All Fields (from strongest detection row)")
    # Show the strongest row fields (all columns)
    st.dataframe(pd.DataFrame([strongest]), use_container_width=True)

    st.markdown("### All Detections for this AP")
    # Show detections table (optional)
    show_cols = [c for c in det.columns if c not in ["_dist_m"]]
    st.dataframe(det[show_cols], use_container_width=True)