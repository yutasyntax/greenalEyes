import streamlit as st
from streamlit_folium import st_folium
import folium
from folium.plugins import Draw, HeatMap
import math
import requests
from PIL import Image
from io import BytesIO
import cv2
import numpy as np

st.set_page_config(layout="wide")
st.sidebar.title("GreenalEyes")

# Sidebar: Jump to City + Analysis Display
st.sidebar.title("🗺️ Jump to Region")
jump_locations = {
    "Tokyo": [35.681236, 139.767125],
    "London": [51.5074, -0.1278],
    "New York": [40.7128, -74.0060],
    "Madrid": [40.4168, -3.7038],
    "Sydney": [-33.8688, 151.2093],
    "Paris": [48.8566, 2.3522],
    "Seoul": [37.5665, 126.9780],
    "Bangkok": [13.7563, 100.5018],
    "São Paulo": [-23.5505, -46.6333],
    "Johannesburg": [-26.2041, 28.0473],
    "Toronto": [43.6532, -79.3832],
    "Beijing": [39.9042, 116.4074]
}
selected_city = st.sidebar.selectbox("Select a City:", list(jump_locations.keys()))
center = jump_locations[selected_city]

# Map setup (default: selected city)
m = folium.Map(location=center, zoom_start=12)

# Add Draw tool (rectangle only, limit to single shape)
Draw(
    export=True,
    draw_options={
        "rectangle": {
            "shapeOptions": {"color": "#ff0000"},
            "repeatMode": False
        },
        "polygon": False,
        "circle": False,
        "polyline": False,
        "marker": False,
        "circlemarker": False
    },
    edit_options={"edit": False, "remove": True}
).add_to(m)

# Display the map
st_data = st_folium(m, width=1200, height=800, key="map")

# Zoom level calculator from bbox
def calculate_zoom_level(lon_min, lat_min, lon_max, lat_max, image_width=640):
    bbox_width_deg = abs(lon_max - lon_min)
    TILE_SIZE = 256
    zoom = math.log2((360 * image_width) / (bbox_width_deg * TILE_SIZE))
    return max(0, min(int(zoom), 20))

# Show green area analysis
if st_data and st_data.get("all_drawings"):
    drawing = st_data["all_drawings"][0]
    coords = drawing["geometry"]["coordinates"][0]
    lons = [point[0] for point in coords]
    lats = [point[1] for point in coords]
    bbox = [min(lons), min(lats), max(lons), max(lats)]

    st.sidebar.write("🗺️ Selected Area:")
    st.sidebar.write(bbox)

    MAPBOX_TOKEN = "YOUR_MAPBOX_TOKEN_HERE"  # Replace with your actual token
    lon_min, lat_min, lon_max, lat_max = bbox
    center_lon = (lon_min + lon_max) / 2
    center_lat = (lat_min + lat_max) / 2
    zoom = calculate_zoom_level(lon_min, lat_min, lon_max, lat_max)
    mapbox_url = f"https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static/{center_lon},{center_lat},{zoom}/640x640?access_token={MAPBOX_TOKEN}"

    response = requests.get(mapbox_url)
    image = Image.open(BytesIO(response.content))
    st.sidebar.image(image, caption=f"Satellite Image (Zoom: {zoom})")

    image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    hsv = cv2.cvtColor(image_cv, cv2.COLOR_BGR2HSV)

    lower_green = np.array([35, 40, 40])
    upper_green = np.array([85, 255, 255])
    mask = cv2.inRange(hsv, lower_green, upper_green)
    green_pixels = np.count_nonzero(mask)
    total_pixels = mask.shape[0] * mask.shape[1]
    green_ratio = green_pixels / total_pixels * 100

    st.sidebar.metric("🌿 Green Coverage", f"{green_ratio:.2f} %")
    st.sidebar.image(mask, caption="Detected Green Areas (White)", clamp=True)

    # Heatmap points sampling
    heat_data = []
    for y in range(0, mask.shape[0], 10):
        for x in range(0, mask.shape[1], 10):
            if mask[y, x] > 0:
                lat = lat_max - (y / mask.shape[0]) * (lat_max - lat_min)
                lon = lon_min + (x / mask.shape[1]) * (lon_max - lon_min)
                heat_data.append([lat, lon])

    # Add heatmap to map
    if heat_data:
        HeatMap(heat_data, radius=8).add_to(m)
        st_folium(m, width=1200, height=800, key="map_final")
