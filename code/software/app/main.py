import streamlit as st

from webserver import ESP32CAM

st.set_page_config(
    page_title="SuperScanner8000",  # Window title
    page_icon="🧊",              # Favicon (optional)
    layout="centered"            # Layout ("centered" or "wide")
)

current_mode = "SETUP"

# esp32cam = ESP32CAM("http://172.20.10.8:80/stream")
# frame = esp32cam.get_frame()

#if frame is None or frame.size == 0:
#    print("Failed to receive initial frame.")

# Create three rows for th  e cross shape

if current_mode == "SETUP":
    wsAroundBut = 4

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
