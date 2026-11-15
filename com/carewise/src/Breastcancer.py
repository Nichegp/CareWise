
import streamlit as st

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import StandardScaler
from PIL import Image, ImageOps, ImageEnhance, ImageFilter
import pytesseract
import re
import hashlib
from collections import Counter

# ---------------- OCR EXTRACTION ----------------

def extract_value(crop):
    crop = crop.resize(
        (crop.width * 5, crop.height * 5),
        Image.Resampling.LANCZOS
    )

    gray = ImageOps.grayscale(crop)

    variants = [
        gray,
        ImageEnhance.Contrast(gray).enhance(2.5),
        gray.point(lambda p: 255 if p > 155 else 0)
    ]

    candidates = []

    for image in variants:
        for psm in (6, 7, 8, 11, 13):
            text = pytesseract.image_to_string(
                image,
                config=f"--oem 3 --psm {psm} -c tessedit_char_whitelist=0123456789.,"
            )

            match = re.search(
                r'\d[\d,]*(?:\.\d+)?',
                text.replace(" ", "")
            )

            if match:
                try:
                    candidates.append(
                        float(match.group().replace(",", ""))
                    )
                except ValueError:
                    pass

    if candidates:
        return Counter(candidates).most_common(1)[0][0]

    return 0.0


def render():

    # ---------------- LOAD DATA ----------------

    breast_data = pd.read_csv('./data/wdbc.data', header=None)

    columns = [
        "id", "diagnosis",
        "radius_mean", "texture_mean", "perimeter_mean",
        "area_mean", "smoothness_mean", "compactness_mean",
        "concavity_mean", "concave_points_mean", "symmetry_mean",
        "fractal_dimension_mean",
        "radius_se", "texture_se", "perimeter_se", "area_se",
        "smoothness_se", "compactness_se", "concavity_se",
        "concave_points_se", "symmetry_se", "fractal_dimension_se",
        "radius_worst", "texture_worst", "perimeter_worst",
        "area_worst", "smoothness_worst", "compactness_worst",
        "concavity_worst", "concave_points_worst", "symmetry_worst",
        "fractal_dimension_worst"
    ]

    breast_data.columns = columns

    # ---------------- PREPARE DATA ----------------

    patients_data = breast_data.drop(columns=['id', 'diagnosis'], axis=1)

    disease_prediction = breast_data['diagnosis'].map({
        'B': 0,
        'M': 1
    })

    feature_columns = patients_data.columns.tolist()

    patients_data_train, patients_data_test, disease_prediction_train, disease_prediction_test = train_test_split(
        patients_data, disease_prediction, test_size=0.2, stratify=disease_prediction, random_state=2
    )

    # Scale features

    scaler = StandardScaler()

    patients_data_train = scaler.fit_transform(patients_data_train.values)
    patients_data_test = scaler.transform(patients_data_test.values)

    model = LogisticRegression(max_iter=1000)

    model.fit(patients_data_train, disease_prediction_train)

    patients_data_train_prediction = model.predict(patients_data_train)

    accuracy_of_train_data = accuracy_score(
        patients_data_train_prediction,
        disease_prediction_train
    )

    disease_prediction_test_prediction = model.predict(patients_data_test)

    test_data_accuracy = accuracy_score(
        disease_prediction_test_prediction,
        disease_prediction_test
    )

    left_col, right_col = st.columns([2, 1])

    with right_col:

        st.markdown(
            f'<div style="background-color: #e8f5e8; border-left: 3px solid #4caf50; padding: 5px; margin: 6px 0; border-radius: 4px;">'
            f'<p style="color:#2e7d32; margin:0; font-weight:600; font-size:14px;">📊 Model Performance</p>'
            f'<p style="color: #388e3c; margin: 2px 0 0 0; font-weight: 500; font-size: 12px;"> Data Accuracy: {accuracy_of_train_data:.2%}</p></div>',
            unsafe_allow_html=True
        )

        st.caption(f"Test Data Accuracy: {test_data_accuracy:.2%}")

    with left_col:
        input_mode = st.radio(
            "Select how you want to enter patient data:",
            ["📷 Scan My Report", "⌨️ Manually Enter Data"],
            horizontal=True,
            key="breast_cancer_input_mode"
        )

    # ---------------- SCAN MEDICAL REPORT ----------------

    if input_mode == "📷 Scan My Report":

        uploaded_img = st.file_uploader(
            "Upload Medical Reports",
            type=["jpg", "jpeg", "png"],
            key="breast_report_uploader"
        )

        if uploaded_img:

            img = ImageOps.exif_transpose(
                Image.open(uploaded_img)
            ).convert("RGB")

            st.image(
                img,
                caption="Scanned Image Preview",
                width=400
            )

            image_signature = hashlib.md5(
                uploaded_img.getvalue()
            ).hexdigest()

            # Extract values from the uploaded report

            if st.session_state.get("breast_last_image") != image_signature:

                extracted_values = {}

                width, height = img.size

                scale_x = width / 1024
                scale_y = height / 1536

                left_features = [
                    "radius_mean", "texture_mean", "perimeter_mean",
                    "area_mean", "smoothness_mean", "compactness_mean",
                    "concavity_mean", "concave_points_mean", "symmetry_mean",
                    "fractal_dimension_mean", "radius_se", "texture_se",
                    "perimeter_se", "area_se", "smoothness_se",
                    "compactness_se", "concavity_se", "concave_points_se",
                    "symmetry_se", "fractal_dimension_se"
                ]

                right_features = [
                    "radius_worst", "texture_worst", "perimeter_worst",
                    "area_worst", "smoothness_worst", "compactness_worst",
                    "concavity_worst", "concave_points_worst",
                    "symmetry_worst", "fractal_dimension_worst"
                ]

                # Mean Features

                for i, feature in enumerate(left_features[:10]):

                    y1 = 538 + i * 39
                    y2 = y1 + 39

                    crop = img.crop((
                        int(365 * scale_x),
                        int(y1 * scale_y),
                        int(507 * scale_x),
                        int(y2 * scale_y)
                    ))

                    extracted_values[feature] = extract_value(crop)

                # Standard Error Features

                for i, feature in enumerate(left_features[10:]):

                    y1 = 974 + i * 38.5
                    y2 = y1 + 39

                    crop = img.crop((
                        int(365 * scale_x),
                        int(y1 * scale_y),
                        int(507 * scale_x),
                        int(y2 * scale_y)
                    ))

                    extracted_values[feature] = extract_value(crop)

                # Worst Features

                for i, feature in enumerate(right_features):

                    y1 = 538 + i * 39
                    y2 = y1 + 39

                    crop = img.crop((
                        int(846 * scale_x),
                        int(y1 * scale_y),
                        int(990 * scale_x),
                        int(y2 * scale_y)
                    ))

                    extracted_values[feature] = extract_value(crop)

                # Save extracted values

                for feature in feature_columns:

                    st.session_state[
                        f"breast_{feature}"
                    ] = extracted_values.get(feature, 0.0)

                st.session_state["breast_last_image"] = image_signature

            st.subheader("Auto-Filled Form Below (Editable)")

            # Mean Features

            st.markdown("**Mean Features**")

            mean_features = [
                ("radius_mean", "Mean Radius"),
                ("texture_mean", "Mean Texture"),
                ("perimeter_mean", "Mean Perimeter"),
                ("area_mean", "Mean Area"),
                ("smoothness_mean", "Mean Smoothness"),
                ("compactness_mean", "Mean Compactness"),
                ("concavity_mean", "Mean Concavity"),
                ("concave_points_mean", "Mean Concave Points"),
                ("symmetry_mean", "Mean Symmetry"),
                ("fractal_dimension_mean", "Mean Fractal Dimension")
            ]

            values = {}

            for feature, label in mean_features:

                values[feature] = st.number_input(
                    label,
                    format="%.6f",
                    key=f"breast_{feature}"
                )

            # Standard Error Features

            st.markdown("**Standard Error Features**")

            se_features = [
                ("radius_se", "Radius Standard Error"),
                ("texture_se", "Texture Standard Error"),
                ("perimeter_se", "Perimeter Standard Error"),
                ("area_se", "Area Standard Error"),
                ("smoothness_se", "Smoothness Standard Error"),
                ("compactness_se", "Compactness Standard Error"),
                ("concavity_se", "Concavity Standard Error"),
                ("concave_points_se", "Concave Points Standard Error"),
                ("symmetry_se", "Symmetry Standard Error"),
                ("fractal_dimension_se", "Fractal Dimension Standard Error")
            ]

            for feature, label in se_features:

                values[feature] = st.number_input(
                    label,
                    format="%.6f",
                    key=f"breast_{feature}"
                )

            # Worst Features

            st.markdown("**Worst Features**")

            worst_features = [
                ("radius_worst", "Worst Radius"),
                ("texture_worst", "Worst Texture"),
                ("perimeter_worst", "Worst Perimeter"),
                ("area_worst", "Worst Area"),
                ("smoothness_worst", "Worst Smoothness"),
                ("compactness_worst", "Worst Compactness"),
                ("concavity_worst", "Worst Concavity"),
                ("concave_points_worst", "Worst Concave Points"),
                ("symmetry_worst", "Worst Symmetry"),
                ("fractal_dimension_worst", "Worst Fractal Dimension")
            ]

            for feature, label in worst_features:

                values[feature] = st.number_input(
                    label,
                    format="%.6f",
                    key=f"breast_{feature}"
                )

            if st.button("BreastAnalyze", key="breast_scan_analyze"):

                input_data = np.array([
                    values[feature] for feature in feature_columns
                ]).reshape(1, -1)

                if np.any(input_data == 0):

                    st.error("Please verify all 30 medical measurements.")

                else:

                    input_data_scaled = scaler.transform(input_data)

                    prediction = model.predict(input_data_scaled)

                    st.session_state["breast_prediction"] = int(prediction[0])
                    st.session_state["show_breast_info"] = False

    else:

        # ---------------- MANUAL DATA ENTRY FORM ----------------

        with st.form("breast_form"):

            st.subheader("Mean Features")

            radius_mean = st.number_input("Mean Radius:")
            texture_mean = st.number_input("Mean Texture:")
            perimeter_mean = st.number_input("Mean Perimeter:")
            area_mean = st.number_input("Mean Area:")
            smoothness_mean = st.number_input("Mean Smoothness:")
            compactness_mean = st.number_input("Mean Compactness:")
            concavity_mean = st.number_input("Mean Concavity:")
            concave_points_mean = st.number_input("Mean Concave Points:")
            symmetry_mean = st.number_input("Mean Symmetry:")
            fractal_dimension_mean = st.number_input("Mean Fractal Dimension:")

            st.subheader("Standard Error Features")

            radius_se = st.number_input("Radius Standard Error:")
            texture_se = st.number_input("Texture Standard Error:")
            perimeter_se = st.number_input("Perimeter Standard Error:")
            area_se = st.number_input("Area Standard Error:")
            smoothness_se = st.number_input("Smoothness Standard Error:")
            compactness_se = st.number_input("Compactness Standard Error:")
            concavity_se = st.number_input("Concavity Standard Error:")
            concave_points_se = st.number_input("Concave Points Standard Error:")
            symmetry_se = st.number_input("Symmetry Standard Error:")
            fractal_dimension_se = st.number_input("Fractal Dimension Standard Error:")

            st.subheader("Worst Features")

            radius_worst = st.number_input("Worst Radius:")
            texture_worst = st.number_input("Worst Texture:")
            perimeter_worst = st.number_input("Worst Perimeter:")
            area_worst = st.number_input("Worst Area:")
            smoothness_worst = st.number_input("Worst Smoothness:")
            compactness_worst = st.number_input("Worst Compactness:")
            concavity_worst = st.number_input("Worst Concavity:")
            concave_points_worst = st.number_input("Worst Concave Points:")
            symmetry_worst = st.number_input("Worst Symmetry:")
            fractal_dimension_worst = st.number_input("Worst Fractal Dimension:")

            submitBreast = st.form_submit_button("BreastAnalyze")

            if submitBreast:

                input_data = np.array([
                    radius_mean, texture_mean, perimeter_mean,
                    area_mean, smoothness_mean, compactness_mean,
                    concavity_mean, concave_points_mean, symmetry_mean,
                    fractal_dimension_mean,
                    radius_se, texture_se, perimeter_se, area_se,
                    smoothness_se, compactness_se, concavity_se,
                    concave_points_se, symmetry_se, fractal_dimension_se,
                    radius_worst, texture_worst, perimeter_worst,
                    area_worst, smoothness_worst, compactness_worst,
                    concavity_worst, concave_points_worst, symmetry_worst,
                    fractal_dimension_worst
                ]).reshape(1, -1)

                if np.any(input_data == 0):

                    st.error("Please enter all 30 medical measurements.")

                else:

                    input_data_scaled = scaler.transform(input_data)

                    prediction = model.predict(input_data_scaled)

                    st.session_state["breast_prediction"] = int(prediction[0])
                    st.session_state["show_breast_info"] = False

    # ---------------- DISPLAY PREDICTION ----------------

    if "breast_prediction" in st.session_state:

        if st.session_state["breast_prediction"] == 0:

            st.success("✅ Amazing News! Low chance of Malignant Breast Cancer!")

        else:

            st.error("⚠️ High chance of Malignant Breast Cancer! Please consult a doctor using the sidebar on the left.")

            if st.button("Learn More About Malignant Cancer", key="learn_breast_cancer"):

                st.session_state["show_breast_info"] = True

            if st.session_state.get("show_breast_info", False):

                st.info(
                    "Malignant breast cancer is a cancerous tumor that develops when cells in the breast mutate, multiply uncontrollably, and invade surrounding healthy tissue and some symptoms of malignant cancer "
                    "include a lump in the breast, changes in breast shape or size, skin dimpling, nipple discharge, and persistent pain in the breast or nipple area. "
                    "Early detection and treatment are crucial for improving outcomes, so regular screenings and prompt medical attention for any concerning changes are essential."
                )