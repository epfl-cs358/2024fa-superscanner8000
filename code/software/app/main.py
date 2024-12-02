import streamlit as st

from streamlit_image_coordinates  import streamlit_image_coordinates
from webserver import ESP32CAM, WIFI_CONTROLLER

st.set_page_config(
    page_title="SuperScanner8000",  # Window title
    page_icon="🧊",              # Favicon (optional)
    layout="centered"            # Layout ("centered" or "wide")
)

# esp32cam = ESP32CAM("http://172.20.10.8:80/stream")
# frame = esp32cam.get_frame()

#if frame is None or frame.size == 0:
#    print("Failed to receive initial frame.")

# Create three rows for th  e cross shape
if "mode" not in st.session_state:
    st.session_state["mode"] = "CONNECTION"

if(st.session_state["mode"] == "CONNECTION"):
    net_cont = WIFI_CONTROLLER()

    st.title("Connection to the scanner")
    st.write("Welcome to the SuperScanner8000! Please connect to the ESP32-CAM by entering the IP address below.")
    if st.button("Connect"):
        st.session_state["mode"]="SETUP"

elif(st.session_state["mode"] == "SETUP"):
    wsAroundBut = 4

    st.write("Please configure select which object do you want to scan by clicking on the image.")
    value = streamlit_image_coordinates("catglasses.jpg", use_column_width=True, height=200)
    col0, col1, col2, col3, col4 = st.columns([wsAroundBut, 1, 1, 1, wsAroundBut])

    with col1:  
        # Left button
        if st.button("↻"):
            st.write("You pressed the Left button")

    with col2:
        # Top button
        if st.button("↑"):
            st.write("You pressed the Up button")

    with col3:
        # Right button
        if st.button("↺"):
            st.write("You pressed the Right button")

    col0, col1, col2, col3, col4 = st.columns([wsAroundBut, 1, 1, 1, wsAroundBut])

    with col2:
        # Bottom button
        if st.button("↓"):
            st.write("You pressed the Down button")
