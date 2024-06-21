import streamlit as st
import folium
from streamlit_folium import st_folium
from folium import Marker

# placeholder for backend function
def process_coordinates(lat, lon):
    # Replace this logic with your actual backend processing
    new_lat = lat + 10.002
    new_lon = lon + 10.002
    return new_lat, new_lon
if 'init' not in st.session_state:
    st.session_state['init'] = True

# initial session state variables, default map view italy
if 'lat' not in st.session_state:
    st.session_state['lat'] = 41.48
if 'lon' not in st.session_state:
    st.session_state['lon'] = 14.47
if 'zoom' not in st.session_state:
    st.session_state['zoom'] = 6

st.title("Wildfire Early Warning System")
st.header("the best wildfire warning system everrr")

# Sidebar
st.sidebar.header("Enter Coordinates")
st.sidebar.caption("for the area to make a prediction for")
lat = st.sidebar.number_input("Enter latitude", value=0.0, format="%.6f")
lon = st.sidebar.number_input("Enter longitude", value=0.0, format="%.6f")

if 'lat' in st.session_state and not st.session_state['init']:
    print("entered rounds")
    marker = Marker([st.session_state['lat'], st.session_state['lon']], tooltip="Wildfire predicted")

with st.sidebar.expander("How to Use"):
    st.write("""
    1. Enter latitude and longitude coordinates in the sidebar.
    2. Click on the "Submit" button to update the map with the new coordinates.
    3. IF MARKERS APPEAR, FIRE IS PREDICTEDdd oh noooo!
    """)

# Submit button
if st.sidebar.button("Submit"):
    st.session_state['init'] = False
    # get new coordinates
    new_lat, new_lon = process_coordinates(lat, lon)
    # update session state with new coordinates
    st.session_state['lat'] = new_lat
    st.session_state['lon'] = new_lon
    marker = Marker([st.session_state['lat'], st.session_state['lon']], tooltip="Wildfire predicted")
    print(marker)

# create Folium map centered at the session state coordinates
m = folium.Map(location=[st.session_state['lat'], st.session_state['lon']], zoom_start=st.session_state['zoom'])

print(st.session_state['init'])
if st.session_state.init == False:
    print("adding")
    marker.add_to(m)

# display
st_folium(m, width=700, height=500)
