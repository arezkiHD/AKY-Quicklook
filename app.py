import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
import requests
import io
from PIL import Image

# Configuration de la page
st.set_page_config(
    page_title="AKY Quicklook ",
    page_icon="",
    layout="wide"
)

# Titre principal centré
st.markdown("<h1 style='text-align: center;'>AKY (Antikythera, Greece) - Quicklook </h1>", unsafe_allow_html=True)

# Espace entre le titre et la navigation
st.markdown("<br><br>", unsafe_allow_html=True)

# Configuration des longueurs d'onde disponibles
WAVELENGTHS = {
    "355_ab": {"name": "355 nm Backscatter", "wavelength": "0355", "product": "ab"},
    "532_ab": {"name": "532 nm Backscatter", "wavelength": "0532", "product": "ab"},
    "1064_ab": {"name": "1064 nm Backscatter", "wavelength": "1064", "product": "ab"},
    "532_vl": {"name": "532 nm Depolarization", "wavelength": "0532", "product": "vl"},
    "cloudmask": {"name": "Cloud Mask", "wavelength": "", "product": "cm"}
}

# Configuration des altitudes disponibles
ALTITUDES = {
    "05km": "5 km",
    "10km": "10 km", 
    "20km": "20 km"
}

# Créneaux horaires fixes
TIME_SLOTS = {
    "00": {"label": "00:00-06:00 UTC", "start": "000000"},
    "06": {"label": "06:00-12:00 UTC", "start": "060000"}, 
    "12": {"label": "12:00-18:00 UTC", "start": "120000"},
    "18": {"label": "18:00-00:00 UTC", "start": "180000"}
}

def generate_aky_quicklook_url(date_str, time_start, wavelength_key, altitude):
    """
    Génère l'URL exacte pour AKY basée sur vos exemples réels avec altitude configurable
    """
    base_url = "https://quicklooks.earlinet.org/quicklooks/"
    
    wavelength_info = WAVELENGTHS[wavelength_key]
    
    if wavelength_key == "cloudmask":
        # Format pour cloudmask: aky_20250601060000_06h_l00146_cm_20km.png
        filename = f"aky_{date_str}{time_start}_06h_l00146_cm_{altitude}.png"
    else:
        # Format pour wavelengths: aky_20250601060000_06h_l00146_w0355_r0_ide_ab_20km.png
        wavelength = wavelength_info["wavelength"]
        product = wavelength_info["product"]
        filename = f"aky_{date_str}{time_start}_06h_l00146_w{wavelength}_r0_ide_{product}_{altitude}.png"
    
    return base_url + filename

def check_image_exists(url):
    """Vérifie si l'image existe avec timeout optimisé"""
    try:
        response = requests.head(url, timeout=3)
        return response.status_code == 200
    except:
        return False

def load_image_from_url(url):
    """Charge une image depuis une URL"""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return Image.open(io.BytesIO(response.content))
    except:
        pass
    return None

# Configuration dans la sidebar
with st.sidebar:
    st.subheader("Configuration")
    
    # Sélection de la date
    selected_date = st.date_input(
        "Date",
        value=date(2025, 6, 1),
        min_value=date(2020, 1, 1),
        max_value=date.today()
    )
    
    # Sélection de la longueur d'onde avec radio buttons
    st.markdown("**Longueur d'onde**")
    selected_wavelength = st.radio(
        "",
        options=list(WAVELENGTHS.keys()),
        format_func=lambda x: WAVELENGTHS[x]['name'],
        index=1,  # 532_ab par défaut
        label_visibility="collapsed"
    )
    
    # Sélection de l'altitude maximale
    st.markdown("**Altitude maximale**")
    selected_altitude = st.radio(
        "",
        options=list(ALTITUDES.keys()),
        format_func=lambda x: ALTITUDES[x],
        index=2,  # 20km par défaut
        label_visibility="collapsed"
    )

# Navigation centrée au milieu de la page
nav_col1, nav_col2, nav_col3, nav_col4, nav_col5 = st.columns([1, 1, 2, 1, 1])

with nav_col2:
    if st.button("← Jour précédent", use_container_width=True):
        new_date = selected_date - timedelta(days=1)
        st.session_state.nav_date = new_date
        st.rerun()

with nav_col3:
    st.markdown(f"<div style='text-align: center; padding: 12px; font-size: 18px; font-weight: bold; background-color: #f0f2f6; border-radius: 10px; margin: 8px;'>{selected_date.strftime('%Y-%m-%d')}</div>", unsafe_allow_html=True)

with nav_col4:
    if st.button("Jour suivant →", use_container_width=True):
        new_date = selected_date + timedelta(days=1)
        if new_date <= date.today():
            st.session_state.nav_date = new_date
            st.rerun()

# Application de la navigation
if 'nav_date' in st.session_state:
    selected_date = st.session_state.nav_date
    del st.session_state.nav_date

# Espace entre la navigation et les quicklooks
st.markdown("<br><br>", unsafe_allow_html=True)

# Affichage des quicklooks
# Génération des URLs et vérification de disponibilité
date_str = selected_date.strftime("%Y%m%d")

# Création d'une grille 2x2 pour les 4 créneaux
row1_col1, row1_col2 = st.columns(2)
row2_col1, row2_col2 = st.columns(2)

columns = [row1_col1, row1_col2, row2_col1, row2_col2]
time_keys = list(TIME_SLOTS.keys())

for i, (time_key, time_info) in enumerate(TIME_SLOTS.items()):
    
    url = generate_aky_quicklook_url(date_str, time_info["start"], selected_wavelength, selected_altitude)
    
    with columns[i]:
        # Vérification et affichage (sans titre en gras)
        if check_image_exists(url):
            image = load_image_from_url(url)
            if image:
                st.image(
                    image, 
                    caption=f"{time_info['label']}",
                    use_container_width=True
                )
            else:
                st.error("Erreur de chargement")
        else:
            # Affichage "Non disponible" stylisé
            st.markdown(
                f"""
                <div style="
                    background-color: #f8f9fa; 
                    border: 2px dashed #dee2e6; 
                    padding: 40px; 
                    text-align: center; 
                    border-radius: 10px;
                    margin: 10px 0;
                ">
                    <p style="color: #6c757d; font-size: 16px; margin: 0;">
                        <strong>Non Disponible</strong><br>
                        <small>{time_info['label']}</small><br>
                        <small style="color: #adb5bd;">Pas de mesures</small>
                    </p>
                </div>
                """, 
                unsafe_allow_html=True
            )