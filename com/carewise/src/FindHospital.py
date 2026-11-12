import streamlit as st
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score
import googlemaps

API_KEY = "AIzaSyBhksGknvLc61HhxmoLTKw9DKxDE9Y__gE"
gmaps = googlemaps.Client(key=API_KEY)


def get_nearby_hospitals(lat, lng, radius=3000):
    try:
        places = gmaps.places_nearby(
            location=(lat, lng),
            radius=radius,
            type="hospital"
        )
        return places.get("results", [])
    except Exception as e:
        print(f"Error fetching hospitals: {e}")
        return []

 
def render():
   
   

# Sidebar
    st.sidebar.image("./data/Logo.png")
    st.sidebar.write(
        "Care Wise is an AI-powered health assistant that provides "
        "preliminary disease predictions based on user-described symptoms."
        "It does not replace a doctor.")

    st.sidebar.title("🏥 Find Nearby Hospitals")
        
    address = st.sidebar.text_input("📍 Enter your address (e.g., 'Bangalore, India')", 
                           placeholder="City, Country or full address",
                           key="address_input")
    lat = None
    lng = None
   
    if address:
        try:
            # Geocode the address
            geocode_result = gmaps.geocode(address)
            if geocode_result:
                location = geocode_result[0]['geometry']['location']
                lat = location['lat']
                lng = location['lng']
                st.sidebar.success(f"📍 Location found: {lat:.6f}, {lng:.6f}")
            else:
                st.sidebar.warning("Could not find location for that address.")
        except Exception as e:
            st.sidebar.error(f"Error geocoding address: {e}")
    
    if st.sidebar.button("🔍 Search Hospitals"):
        if lat and lng:
            hospitals = get_nearby_hospitals(lat, lng)
            if hospitals:
                st.sidebar.write("**Nearby Hospitals:**")
                for h in hospitals:
                    name = h.get("name", "Unknown")
                    rating = h.get("rating", "N/A")
                    address = h.get("vicinity", "Address not available")
                    st.sidebar.write(f"🏥 **{name}** - Rating: {rating}")
                    st.sidebar.caption(f"📍 {address}")
                    st.sidebar.divider()
            else:
                st.sidebar.warning("No hospitals found nearby. Try expanding the search radius or check your location.")
        else:
            st.sidebar.error("Please provide a valid location (address or coordinates).")

  
