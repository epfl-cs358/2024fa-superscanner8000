import streamlit as st

from webserver import ESP32CAM
import cv2

 
st.write("""
# Superscanner8000
""")

esp32cam = ESP32CAM("http://172.20.10.8:80/stream")
frame = esp32cam.get_frame()

if frame is None or frame.size == 0:
    print("Failed to receive initial frame.")