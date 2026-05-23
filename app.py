"""
Smart Travel Packing & Clothing Advisor
Mobile-first Streamlit app — optimised for iPhone Safari
=========================================================
Free dependencies only:
    pip install streamlit requests

APIs used (no key required):
    • Open-Meteo Geocoding  → https://geocoding-api.open-meteo.com
    • Open-Meteo Forecast   → https://api.open-meteo.com
    • Open-Meteo Archive    → https://archive-api.open-meteo.com
    • ip-api.com            → free IP geolocation fallback
"""

import streamlit as st
import requests
from datetime import date, timedelta
from math import ceil

# ─────────────────────────────────────────────
#  PAGE CONFIG  (must be first Streamlit call)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="✈️ Packing Advisor",
    page_icon="🧳",
    layout="centered",          # keeps it narrow = phone-friendly
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
#  MOBILE-FIRST CSS
#  Uses CSS variables so dark-mode works too.
# ─────────────────────────────────────────────
st.markdown("""
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<style>
/* ── Global ─────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}
.stApp { background: #f2f4f8; }

/* Hide Streamlit chrome on mobile */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1rem 1rem 4rem 1rem !important; max-width: 480px !important; margin: auto; }

/* ── Hero banner ─────────────────────────────── */
.hero {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 20px;
    padding: 1.5rem 1.2rem 1.2rem;
    color: white;
    margin-bottom: 1rem;
    text-align: center;
    box-shadow: 0 8px 24px rgba(102,126,234,0.35);
}
.hero h1 { font-size: 1.6rem; font-weight: 800; margin: 0 0 0.2rem; color:white; }
.hero p  { font-size: 0.88rem; opacity: 0.88; margin: 0; }

/* ── Cards ───────────────────────────────────── */
.card {
    background: white;
    border-radius: 18px;
    padding: 1.1rem 1.2rem;
    margin-bottom: 0.9rem;
    box-shadow: 0 2px 14px rgba(0,0,0,0.07);
}
.card-title {
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #8b9ab1;
    margin-bottom: 0.6rem;
}

/* ── Weather stat row ────────────────────────── */
.stat-row { display:flex; gap:0.6rem; margin-bottom:0.9rem; }
.stat-box {
    flex:1; background:white; border-radius:16px;
    padding:0.8rem 0.5rem; text-align:center;
    box-shadow: 0 2px 10px rgba(0,0,0,0.07);
}
.stat-val { font-size:1.4rem; font-weight:800; color:#1a1f36; line-height:1; }
.stat-lbl { font-size:0.68rem; color:#8b9ab1; font-weight:600; margin-top:3px; letter-spacing:0.04em; text-transform:uppercase; }

/* ── Condition pill ──────────────────────────── */
.condition-pill {
    display:inline-flex; align-items:center; gap:6px;
    background:#eef2ff; color:#4f46e5;
    border-radius:20px; padding:5px 14px;
    font-size:0.85rem; font-weight:600;
    margin-bottom:0.6rem;
}

/* ── Wear items ──────────────────────────────── */
.wear-item {
    display:flex; align-items:flex-start; gap:10px;
    padding: 0.65rem 0;
    border-bottom: 1px solid #f1f3f7;
    font-size:0.9rem; color:#2d3748;
}
.wear-item:last-child { border-bottom:none; }
.wear-icon { font-size:1.3rem; width:28px; text-align:center; flex-shrink:0; }
.wear-text strong { display:block; font-size:0.78rem; color:#8b9ab1; font-weight:600;
                    text-transform:uppercase; letter-spacing:0.05em; margin-bottom:1px; }

/* ── Packing category ────────────────────────── */
.pack-cat {
    border-radius:14px; padding:0.9rem 1rem;
    margin-bottom:0.7rem;
}
.pack-cat-title {
    font-size:0.8rem; font-weight:700; letter-spacing:0.06em;
    text-transform:uppercase; margin-bottom:0.5rem;
}
.pack-item {
    display:flex; align-items:center; gap:8px;
    font-size:0.88rem; padding:4px 0; color:#374151;
}
.pack-dot { width:6px; height:6px; border-radius:50%; flex-shrink:0; }

/* Category colours */
.tops      { background:#eff6ff; } .tops .pack-cat-title      { color:#1d4ed8; } .tops .pack-dot      { background:#3b82f6; }
.bottoms   { background:#f0fdf4; } .bottoms .pack-cat-title   { color:#166534; } .bottoms .pack-dot   { background:#22c55e; }
.outerwear { background:#fff7ed; } .outerwear .pack-cat-title { color:#9a3412; } .outerwear .pack-dot { background:#f97316; }
.footwear  { background:#faf5ff; } .footwear .pack-cat-title  { color:#6b21a8; } .footwear .pack-dot  { background:#a855f7; }
.access    { background:#fefce8; } .access .pack-cat-title    { color:#854d0e; } .access .pack-dot    { background:#eab308; }
.misc      { background:#f8fafc; } .misc .pack-cat-title      { color:#475569; } .misc .pack-dot      { background:#94a3b8; }

/* ── Alert strip ─────────────────────────────── */
.alert {
    background:#fff7ed; border-left:4px solid #f97316;
    border-radius:10px; padding:0.7rem 0.9rem;
    font-size:0.84rem; color:#7c2d12; margin-bottom:0.5rem;
}

/* ── Pro tips ────────────────────────────────── */
.tip-box {
    background:linear-gradient(135deg,#ecfdf5,#d1fae5);
    border-radius:14px; padding:0.9rem 1rem; margin-top:0.5rem;
}
.tip-box ul { margin:0.4rem 0 0 1rem; padding:0; }
.tip-box li { font-size:0.84rem; color:#065f46; margin-bottom:4px; }

/* ── Estimate notice ─────────────────────────── */
.est-notice {
    background:#f0f9ff; border-radius:10px;
    padding:0.6rem 0.9rem; font-size:0.8rem;
    color:#0369a1; margin-bottom:0.7rem;
}

/* ── Input section ───────────────────────────── */
.input-card {
    background:white; border-radius:18px;
    padding:1rem 1.1rem; margin-bottom:0.9rem;
    box-shadow:0 2px 14px rgba(0,0,0,0.07);
}

/* Make Streamlit inputs fill width nicely */
[data-testid="stTextInput"] input,
[data-testid="stDateInput"]  input {
    border-radius:10px !important;
    font-size:1rem !important;
}
.stButton>button {
    width:100%; border-radius:14px !important;
    background:linear-gradient(135deg,#667eea,#764ba2) !important;
    color:white !important; font-weight:700 !important;
    font-size:1rem !important; padding:0.75rem !important;
    border:none !important; margin-top:0.3rem;
    box-shadow:0 4px 15px rgba(102,126,234,0.4) !important;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  IP-BASED LOCATION FALLBACK
# ─────────────────────────────────────────────
@st.cache_data(ttl=3600)
def ip_location() -> str:
    """Return a best-guess city from the server's IP via ip-api.com."""
    try:
        r = requests.get("http://ip-api.com/json/?fields=city", timeout=4)
        city = r.json().get("city", "London")
        return city if city else "London"
    except Exception:
        return "London"


# ─────────────────────────────────────────────
#  GEOCODING
# ─────────────────────────────────────────────
@st.cache_data(ttl=3600)
def geocode(city: str) -> dict | None:
    try:
        r = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 1, "language": "en", "format": "json"},
            timeout=8,
        )
        results = r.json().get("results")
        if not results:
            return None
        loc = results[0]
        return {
            "name":    loc.get("name", city),
            "country": loc.get("country", ""),
            "lat":     loc["latitude"],
            "lon":     loc["longitude"],
        }
    except Exception:
        return None


# ─────────────────────────────────────────────
#  WEATHER FETCH  (forecast + archive fallback)
# ─────────────────────────────────────────────
DAILY_VARS = ("temperature_2m_max,temperature_2m_min,precipitation_sum,"
              "precipitation_probability_max,windspeed_10m_max,weathercode")
ARCHIVE_VARS = ("temperature_2m_max,temperature_2m_min,precipitation_sum,"
                "windspeed_10m_max,weathercode")

@st.cache_data(ttl=1800)
def fetch_weather(lat: float, lon: float, start: date, end: date) -> list[dict]:
    today          = date.today()
    forecast_limit = today + timedelta(days=16)
    rows: list[dict] = []

    def _pull(url, params, is_estimate=False):
        try:
            r = requests.get(url, params=params, timeout=12)
            daily = r.json().get("daily", {})
            times = daily.get("time", [])
            for i, t in enumerate(times):
                d = date.fromisoformat(t)
                rows.append({
                    "date":        d,
                    "temp_max":    daily["temperature_2m_max"][i],
                    "temp_min":    daily["temperature_2m_min"][i],
                    "precip_mm":   daily["precipitation_sum"][i] or 0,
                    "precip_prob": daily.get("precipitation_probability_max",
                                             [None]*len(times))[i],
                    "wind_kph":    daily["windspeed_10m_max"][i] or 0,
                    "wcode":       int(daily["weathercode"][i] or 0),
                    "estimate":    is_estimate,
                })
        except Exception:
            pass

    base = {"latitude": lat, "longitude": lon, "timezone": "auto"}

    # ── Forecast segment ──────────────────────
    if start <= forecast_limit and end >= today:
        s = max(start, today)
        e = min(end, forecast_limit)
        _pull("https://api.open-meteo.com/v1/forecast",
              {**base, "daily": DAILY_VARS,
               "start_date": s.isoformat(), "end_date": e.isoformat()})

    # ── Archive segment (past dates) ──────────
    if start < today:
        s = start
        e = min(end, today - timedelta(days=1))
        _pull("https://archive-api.open-meteo.com/v1/archive",
              {**base, "daily": ARCHIVE_VARS,
               "start_date": s.isoformat(), "end_date": e.isoformat()})

    # ── Climate proxy (far-future dates) ──────
    if end > forecast_limit:
        s = max(start, forecast_limit + timedelta(days=1))
        e = end
        ps = s.replace(year=s.year - 1)
        pe = e.replace(year=e.year - 1)
        _pull("https://archive-api.open-meteo.com/v1/archive",
              {**base, "daily": ARCHIVE_VARS,
               "start_date": ps.isoformat(), "end_date": pe.isoformat()},
              is_estimate=True)
        # Relabel dates to the real trip year
        for row in rows:
            if row["estimate"] and row["date"].year == ps.year:
                try:
                    row["date"] = row["date"].replace(year=s.year)
                except ValueError:
                    pass

    # Deduplicate, filter, sort
    seen: set[date] = set()
    clean = []
    for row in sorted(rows, key=lambda r: r["date"]):
        if row["date"] in seen or not (start <= row["date"] <= end):
            continue
        seen.add(row["date"])
        clean.append(row)
    return clean


# ─────────────────────────────────────────────
#  WMO CODE → EMOJI + LABEL
# ─────────────────────────────────────────────
def wmo(code: int) -> tuple[str, str]:
    table = {
        0: ("☀️","Clear sky"), 1: ("🌤️","Mainly clear"), 2: ("⛅","Partly cloudy"),
        3: ("☁️","Overcast"),  45: ("🌫️","Foggy"),       51: ("🌦️","Light drizzle"),
        61: ("🌧️","Rain"),     63: ("🌧️","Heavy rain"),  71: ("🌨️","Light snow"),
        73: ("❄️","Snow"),     75: ("❄️","Heavy snow"),   80: ("🌦️","Showers"),
        95: ("⛈️","Thunderstorm"),
    }
    for k in sorted(table.keys(), reverse=True):
        if code >= k:
            return table[k]
    return ("🌡️","Unknown")


# ─────────────────────────────────────────────
#  RECOMMENDATION ENGINE
# ─────────────────────────────────────────────
def recommend(rows: list[dict], trip_days: int) -> dict:
    avg_max = sum(r["temp_max"] for r in rows) / len(rows)
    avg_min = sum(r["temp_min"] for r in rows) / len(rows)
    avg_wind= sum(r["wind_kph"] for r in rows) / len(rows)
    total_rain = sum(r["precip_mm"] for r in rows)
    rainy_days = sum(1 for r in rows if r["precip_mm"] > 1)
    snowy_days = sum(1 for r in rows if r["wcode"] >= 71)
    hot_days   = sum(1 for r in rows if r["temp_max"] > 28)
    windy_days = sum(1 for r in rows if r["wind_kph"] > 40)
    storm_days = sum(1 for r in rows if r["wcode"] >= 95)
    dominant_code = max(set(r["wcode"] for r in rows),
                        key=lambda c: sum(1 for r in rows if r["wcode"] == c))

    # Temperature band
    if avg_max >= 30:   band = "hot"
    elif avg_max >= 22: band = "warm"
    elif avg_max >= 14: band = "mild"
    elif avg_max >= 5:  band = "cool"
    else:               band = "cold"

    # Alerts
    alerts = []
    if rainy_days > trip_days * 0.35:
        alerts.append(f"🌧️ Rain expected on ~{rainy_days} day(s) — waterproofs essential.")
    if snowy_days:
        alerts.append(f"❄️ Snow likely on ~{snowy_days} day(s) — warm waterproof layers a must.")
    if storm_days:
        alerts.append(f"⛈️ Storms possible on ~{storm_days} day(s) — check local forecasts.")
    if windy_days:
        alerts.append(f"💨 Strong winds (>40 kph) on ~{windy_days} day(s) — windproof layer recommended.")
    if hot_days > trip_days * 0.5:
        alerts.append("☀️ High UV likely — sunscreen SPF50+, hat & sunglasses are a must.")

    # Daily wear
    wear: list[tuple[str,str,str]] = []  # (icon, category, description)
    if band == "hot":
        wear = [
            ("👕","Top","Lightweight tee, linen or moisture-wicking shirt"),
            ("🩳","Bottom","Shorts, linen trousers or a light sundress"),
            ("🧥","Outerwear","Light cardigan for air-conditioned spaces"),
            ("👡","Footwear","Sandals or breathable trainers"),
        ]
    elif band == "warm":
        wear = [
            ("👕","Top","Short-sleeve shirt or breathable polo"),
            ("👖","Bottom","Chinos, light jeans or a casual dress"),
            ("🧥","Outerwear","Light zip-up or denim jacket for evenings"),
            ("👟","Footwear","Trainers or loafers"),
        ]
    elif band == "mild":
        wear = [
            ("👕","Top","Long-sleeve top or lightweight merino tee"),
            ("👖","Bottom","Jeans or chinos"),
            ("🧥","Outerwear","Medium jacket or trench coat — layers for evening"),
            ("👟","Footwear","Waterproof trainers or ankle boots"),
        ]
    elif band == "cool":
        wear = [
            ("🧣","Top","Thermal long-sleeve + knit sweater"),
            ("👖","Bottom","Thick jeans or fleece-lined trousers"),
            ("🧥","Outerwear","Wool coat or insulated jacket; scarf & gloves for evenings"),
            ("🥾","Footwear","Waterproof ankle boots with warm socks"),
        ]
    else:
        wear = [
            ("🧣","Top","Thermal base layer + merino wool sweater"),
            ("👖","Bottom","Thermal leggings under fleece-lined trousers"),
            ("🧥","Outerwear","Heavy down coat + fleece mid-layer + hat & gloves — mandatory"),
            ("🥾","Footwear","Insulated waterproof winter boots + thick wool socks"),
        ]
    if rainy_days:
        wear.append(("☂️","Rain Gear","Compact umbrella + waterproof rain jacket"))
    if snowy_days:
        wear.append(("🧤","Snow Gear","Waterproof gloves + neck gaiter"))

    # Packing list (scaled to trip length)
    lc = max(1, ceil(trip_days / 5))   # laundry cycles
    def q(n): return min(n * lc, n + 4)

    tops, bottoms, outer, foot, acc = [], [], [], [], []

    if band in ("hot","warm"):
        tops = [f"{q(3)} lightweight tees/shirts",
                f"{q(2)} breathable cotton/linen tops",
                "1 smart top for dinner"]
        bottoms = [f"{q(2)} pairs shorts",
                   "1 pair light trousers/chinos",
                   f"{q(4)} pairs underwear",f"{q(4)} pairs socks"]
        outer = ["1 light cardigan","1 packable windbreaker"]
        foot  = ["1 pair sandals","1 pair breathable trainers"]
        acc   = ["Sunglasses (UV400)","Wide-brim hat or cap",
                 "Sunscreen SPF 50+","Reusable water bottle"]
    elif band == "mild":
        tops = [f"{q(2)} long-sleeve tops",f"{q(2)} regular tees (layering)",
                "1 knit sweater"]
        bottoms = [f"{q(2)} pairs jeans/chinos",
                   f"{q(4)} pairs underwear",f"{q(4)} pairs socks"]
        outer = ["1 medium-weight waterproof jacket","1 mid-layer fleece or cardigan"]
        foot  = ["1 pair waterproof trainers","1 pair casual shoes or ankle boots"]
        acc   = ["Compact umbrella","Reusable water bottle","Light scarf"]
    elif band == "cool":
        tops = [f"{q(2)} long-sleeve merino tops",
                f"{q(1)} thermal base-layer top","1 chunky knit sweater"]
        bottoms = [f"{q(2)} pairs thick jeans/trousers",
                   "1 thermal legging",
                   f"{q(4)} pairs underwear",f"{q(4)} pairs warm socks"]
        outer = ["1 insulated winter coat","1 fleece mid-layer",
                 "1 waterproof shell jacket"]
        foot  = ["1 pair waterproof ankle boots","1 pair warm indoor shoes"]
        acc   = ["Warm beanie","Scarf","Gloves","Compact umbrella",
                 "Reusable water bottle"]
    else:  # cold
        tops = [f"{q(2)} thermal base-layer tops",
                f"{q(2)} merino wool sweaters","1 extra insulating mid-layer"]
        bottoms = [f"{q(2)} thermal base-layer bottoms",
                   f"{q(2)} fleece-lined trousers",
                   f"{q(4)} pairs underwear",f"{q(4)} pairs thick wool socks"]
        outer = ["1 heavy-duty down/puffer coat",
                 "1 waterproof outer shell","1 fleece mid-layer"]
        foot  = ["1 pair insulated waterproof winter boots",
                 "1 pair warm indoor shoes/slippers"]
        acc   = ["Warm beanie","Neck gaiter","Insulated gloves",
                 "Disposable hand warmers","Reusable water bottle",
                 "Heavy-duty lip balm & hand cream"]

    if rainy_days:
        outer.append("1 compact travel umbrella")
        outer.append("Waterproof bag cover / dry-bag")

    misc = ["Passport/ID + photocopies stored separately",
            "Travel adapter (check local voltage)",
            "Portable charger / power bank",
            "Basic first-aid kit + any medications",
            "Packing cubes or compression bags",
            "Travel insurance documents",
            "Local currency + backup card"]

    return dict(
        avg_max=avg_max, avg_min=avg_min, avg_wind=avg_wind,
        total_rain=total_rain, rainy_days=rainy_days,
        band=band, dominant_code=dominant_code,
        alerts=alerts, wear=wear,
        tops=tops, bottoms=bottoms, outer=outer, foot=foot,
        acc=acc, misc=misc,
        has_estimates=any(r["estimate"] for r in rows),
    )


# ─────────────────────────────────────────────
#  HTML HELPERS
# ─────────────────────────────────────────────
def pack_section(title: str, items: list[str], css_class: str) -> str:
    dots = "".join(
        f'<div class="pack-item"><div class="pack-dot"></div>{i}</div>'
        for i in items
    )
    return (f'<div class="pack-cat {css_class}">'
            f'<div class="pack-cat-title">{title}</div>{dots}</div>')

def wear_row(icon: str, cat: str, desc: str) -> str:
    return (f'<div class="wear-item">'
            f'<div class="wear-icon">{icon}</div>'
            f'<div class="wear-text"><strong>{cat}</strong>{desc}</div>'
            f'</div>')


# ─────────────────────────────────────────────
#  SESSION STATE  (persist inputs across reruns)
# ─────────────────────────────────────────────
if "default_city" not in st.session_state:
    st.session_state["default_city"] = ip_location()


# ─────────────────────────────────────────────
#  HERO BANNER
# ─────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <h1>🧳 Packing Advisor</h1>
  <p>Smart clothing & packing for every trip</p>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  INPUT CARD
# ─────────────────────────────────────────────
st.markdown('<div class="input-card">', unsafe_allow_html=True)

city_input = st.text_input(
    "📍 Destination",
    value=st.session_state["default_city"],
    placeholder="e.g. Tokyo, Paris, New York…",
    label_visibility="visible",
)

today = date.today()
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("🛫 Departure", value=today,
                               min_value=today - timedelta(days=365),
                               max_value=today + timedelta(days=365))
with col2:
    end_date = st.date_input("🛬 Return",
                             value=today + timedelta(days=6),
                             min_value=today - timedelta(days=365),
                             max_value=today + timedelta(days=365))

go = st.button("✨ Get My Packing List")
st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  VALIDATE
# ─────────────────────────────────────────────
if not go:
    st.markdown("""
    <div class="card" style="text-align:center;padding:2.5rem 1rem;">
      <div style="font-size:3rem;">🌍✈️👗</div>
      <p style="color:#8b9ab1;margin-top:0.6rem;font-size:0.95rem;">
        Enter your destination and dates above,<br>then tap <strong>Get My Packing List</strong>.
      </p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

if not city_input.strip():
    st.error("Please enter a destination.")
    st.stop()
if end_date < start_date:
    st.error("Return date must be on or after departure date.")
    st.stop()

trip_days = (end_date - start_date).days + 1


# ─────────────────────────────────────────────
#  GEOCODE
# ─────────────────────────────────────────────
with st.spinner("📍 Finding your destination…"):
    loc = geocode(city_input.strip())

if not loc:
    st.error(f"❌ Can't find **{city_input}**. Try a nearby larger city or check the spelling.")
    st.stop()


# ─────────────────────────────────────────────
#  FETCH WEATHER
# ─────────────────────────────────────────────
with st.spinner("🌦️ Fetching weather data…"):
    rows = fetch_weather(loc["lat"], loc["lon"], start_date, end_date)

if not rows:
    st.error("❌ Couldn't retrieve weather data. Try a different date range.")
    st.stop()


# ─────────────────────────────────────────────
#  BUILD RECOMMENDATIONS
# ─────────────────────────────────────────────
rec = recommend(rows, trip_days)


# ─────────────────────────────────────────────
#  UNIT TOGGLE  (Celsius / Fahrenheit)
# ─────────────────────────────────────────────
unit = st.radio("", ["°C", "°F"], horizontal=True, label_visibility="collapsed")

def fmt(c):
    if unit == "°F":
        return f"{c*9/5+32:.0f}°F"
    return f"{c:.0f}°C"


# ─────────────────────────────────────────────
#  DESTINATION HEADER
# ─────────────────────────────────────────────
st.markdown(f"""
<div style="text-align:center;margin:0.5rem 0 0.8rem;">
  <div style="font-size:1.25rem;font-weight:800;color:#1a1f36;">
    📍 {loc['name']}, {loc['country']}
  </div>
  <div style="font-size:0.82rem;color:#8b9ab1;margin-top:2px;">
    {start_date.strftime('%d %b')} – {end_date.strftime('%d %b %Y')} · {trip_days} day(s)
  </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  STAT CHIPS
# ─────────────────────────────────────────────
emoji, label = wmo(rec["dominant_code"])
st.markdown(f"""
<div style="text-align:center;margin-bottom:0.8rem;">
  <span class="condition-pill">{emoji} {label}</span>
</div>
<div class="stat-row">
  <div class="stat-box">
    <div class="stat-val">{fmt(rec['avg_max'])}</div>
    <div class="stat-lbl">High</div>
  </div>
  <div class="stat-box">
    <div class="stat-val">{fmt(rec['avg_min'])}</div>
    <div class="stat-lbl">Low</div>
  </div>
  <div class="stat-box">
    <div class="stat-val">{rec['rainy_days']}/{trip_days}</div>
    <div class="stat-lbl">Rainy Days</div>
  </div>
  <div class="stat-box">
    <div class="stat-val">{rec['avg_wind']:.0f}</div>
    <div class="stat-lbl">Wind kph</div>
  </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  ESTIMATE NOTICE
# ─────────────────────────────────────────────
if rec["has_estimates"]:
    st.markdown("""
    <div class="est-notice">
      📅 Some dates are beyond the 16-day forecast — those use last year's historical
      data for the same calendar period as a climate estimate.
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  ALERTS
# ─────────────────────────────────────────────
if rec["alerts"]:
    alerts_html = "".join(f'<div class="alert">{a}</div>' for a in rec["alerts"])
    st.markdown(f'<div class="card"><div class="card-title">⚠️ Weather Heads-Up</div>{alerts_html}</div>',
                unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  WHAT TO WEAR DAILY
# ─────────────────────────────────────────────
wear_html = "".join(wear_row(icon, cat, desc) for icon, cat, desc in rec["wear"])
st.markdown(f'<div class="card"><div class="card-title">👗 What to Wear Daily</div>{wear_html}</div>',
            unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  PACKING LIST
# ─────────────────────────────────────────────
st.markdown('<div class="card"><div class="card-title">📦 Essential Packing List</div>', unsafe_allow_html=True)
st.markdown(
    pack_section("👕 Tops",      rec["tops"],    "tops")    +
    pack_section("👖 Bottoms",   rec["bottoms"], "bottoms") +
    pack_section("🧥 Outerwear", rec["outer"],   "outerwear") +
    pack_section("👟 Footwear",  rec["foot"],    "footwear") +
    pack_section("🕶️ Accessories", rec["acc"],   "access")  +
    pack_section("📋 Documents & Misc", rec["misc"], "misc"),
    unsafe_allow_html=True,
)
st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  PRO TIPS
# ─────────────────────────────────────────────
st.markdown("""
<div class="tip-box">
  <strong style="color:#065f46;">💡 Packing Pro Tips</strong>
  <ul>
    <li>Roll clothes — saves space & prevents creases.</li>
    <li>Pack neutral colours that mix & match easily.</li>
    <li>Keep essentials in your carry-on in case bags are delayed.</li>
    <li>Liquids in carry-on must be ≤ 100 ml each (in a clear bag).</li>
    <li>Weigh your bag before heading to the airport!</li>
  </ul>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;margin-top:1.5rem;font-size:0.75rem;color:#8b9ab1;">
  Weather by <a href="https://open-meteo.com" style="color:#667eea;">Open-Meteo</a>
  (CC BY 4.0) · Always check local forecasts before travel 🌍
</div>
""", unsafe_allow_html=True)
