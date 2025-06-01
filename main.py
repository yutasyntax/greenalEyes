import streamlit as st
from streamlit_folium import st_folium
import folium
from folium.plugins import Draw
import math
import requests
from PIL import Image
from io import BytesIO
import numpy as np

st.set_page_config(layout="wide")
st.sidebar.title("GreenalEyes")

# Sidebar: Jump to City + Analysis Display
st.sidebar.title("Jump to Region")
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

# Zoom level calculator from bbox
def calculate_zoom_level(lon_min, lat_min, lon_max, lat_max, image_width=640):
    bbox_width_deg = abs(lon_max - lon_min)
    TILE_SIZE = 256
    zoom = math.log2((360 * image_width) / (bbox_width_deg * TILE_SIZE))
    return max(0, min(int(zoom), 20))

# Display the map with drawing tool
m = folium.Map(location=center, zoom_start=12)

Draw(
    export=False,
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

st_data = st_folium(m, width=1200, height=800, key="map_final", returned_objects=["all_drawings"])

if st_data and st_data.get("all_drawings"):
    drawing = st_data["all_drawings"][-1]
    coords = drawing["geometry"]["coordinates"][0]
    lons = [point[0] for point in coords]
    lats = [point[1] for point in coords]
    bbox = [min(lons), min(lats), max(lons), max(lats)]

    st.sidebar.write("Selected Area:")
    st.sidebar.write(bbox)

    MAPBOX_TOKEN = "pk.eyJ1Ijoia3VrdXN5bnRheCIsImEiOiJjbWFkNHVpdHgwN3k4MmlzaWtpeHc5dmh4In0.xhrRYZR3tfl3d_mJoSqnbg"
    lon_min, lat_min, lon_max, lat_max = bbox
    center_lon = (lon_min + lon_max) / 2
    center_lat = (lat_min + lat_max) / 2
    zoom = calculate_zoom_level(lon_min, lat_min, lon_max, lat_max)
    mapbox_url = f"https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static/{center_lon},{center_lat},{zoom}/640x640?access_token={MAPBOX_TOKEN}"

    response = requests.get(mapbox_url)
    if response.status_code == 200:
        try:
            image = Image.open(BytesIO(response.content)).convert("RGB")
            st.sidebar.image(image, caption=f"Satellite Image (Zoom: {zoom})")

            image_np = np.array(image)
            green_mask = (
                (image_np[:, :, 1] > 100) &
                (image_np[:, :, 1] > image_np[:, :, 0]) &
                (image_np[:, :, 1] > image_np[:, :, 2])
            )

            green_pixels = np.count_nonzero(green_mask)
            total_pixels = green_mask.size
            green_ratio = green_pixels / total_pixels * 100

            st.sidebar.metric("🌿 Green Coverage", f"{green_ratio:.2f} %")
            st.sidebar.image(green_mask.astype(np.uint8) * 255, caption="Detected Green Areas (White)", clamp=True)

        except Exception as e:
            st.error(f"Image decoding error: {e}")
    else:
        st.error("Failed to fetch satellite image from Mapbox.")
