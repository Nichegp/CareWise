
import streamlit as st

import Heart_disease_predictor
import FindHospital
import parkinsons
import Breastcancer
import diabetes_predictor
import Bloodtest

# --------------------------------------------------
# Page Configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Care Wise",
    page_icon="🏥",
    layout="wide",
)

# --------------------------------------------------
# Global CSS – Remove Wasted Space
# --------------------------------------------------

st.markdown("""
<style>
.block-container {
    padding-top: 0.5rem;
    padding-bottom: 0rem;
}

button[data-baseweb="tab"] > div {
    font-size: 20px;
    font-weight: 200;
}

h1 {
    margin-bottom: 0.1rem;
}

h3 {
    margin-top: 0rem;
    margin-bottom: 0.2rem;
}

[data-baseweb="tab-list"] {
    margin-top: 0rem;
    font-size: 40px;
}

img {
    max-height: 300px;
    object-fit: cover;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# Banner
# --------------------------------------------------

st.image("./data/Banner.png", width="stretch")

# --------------------------------------------------
# Main Tabs
# --------------------------------------------------

blood_tab, illness_tab = st.tabs(
    [
        "🧪 Analyse Blood Report",
        "🩺 Critical Illness Report",
    ]
)

# --------------------------------------------------
# Blood Test Report
# --------------------------------------------------

with blood_tab:
    Bloodtest.render()

# --------------------------------------------------
# Critical Illness Report
# --------------------------------------------------

with illness_tab:

    cardiologist_tab, parkinsons_tab, breast_cancer_tab, diabetes_tab = st.tabs(
        [
            "❤️ Cardiologist",
            "🧠 Parkinson's",
            "🎗️ Breast Cancer",
            "🩸 Diabetes",
        ]
    )

    # ----------------------------------------------
    # Cardiologist
    # ----------------------------------------------

    with cardiologist_tab:
        Heart_disease_predictor.render()

    # ----------------------------------------------
    # Parkinson's
    # ----------------------------------------------

    with parkinsons_tab:
        parkinsons.render()

    # ----------------------------------------------
    # Breast Cancer
    # ----------------------------------------------

    with breast_cancer_tab:
        Breastcancer.render()

    # ----------------------------------------------
    # Diabetes
    # ----------------------------------------------

    with diabetes_tab:
        diabetes_predictor.render()

# --------------------------------------------------
# Nearby Hospitals
# --------------------------------------------------

FindHospital.render()

# --------------------------------------------------
# Footer
# --------------------------------------------------

st.markdown("""
<div style='text-align: center; padding: 0rem; color: green; font-size: 1.2rem;'>
Care Wise is not designed to replace doctors. It is to ensure patients reach out to doctors at the right time and well informed.
</div>
""", unsafe_allow_html=True)