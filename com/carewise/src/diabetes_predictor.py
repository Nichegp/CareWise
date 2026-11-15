
import streamlit as st

import numpy as np

import pandas as pd

from sklearn.model_selection import train_test_split

from sklearn.linear_model import LogisticRegression

from sklearn.metrics import accuracy_score

from sklearn.preprocessing import StandardScaler

from PIL import Image

import pytesseract

import re


def render():

    # ---------------- LOAD DATA ----------------

    diabetes_data = pd.read_csv('./data/diabetes_prediction_dataset.csv')

    # ---------------- PREPARE DATA ----------------

    patients_data = diabetes_data.drop(columns=['diabetes'], axis=1)

    disease_prediction = diabetes_data['diabetes']

    # Convert categorical columns into numerical columns

    patients_data = pd.get_dummies(
        patients_data,
        columns=['gender', 'smoking_history'],
        dtype=int
    )

    # Keep the exact feature order for prediction

    feature_columns = patients_data.columns.tolist()

    patients_data_train, patients_data_test, disease_prediction_train, disease_prediction_test = train_test_split(
        patients_data, disease_prediction, test_size=0.2, stratify=disease_prediction, random_state=2
    )

    # Scale features to help Logistic Regression converge reliably

    scaler = StandardScaler()

    patients_data_train = scaler.fit_transform(patients_data_train.values)

    patients_data_test = scaler.transform(patients_data_test.values)

    # Increase max_iter to avoid convergence warnings

    model = LogisticRegression(max_iter=1000, class_weight='balanced')

    model.fit(patients_data_train, disease_prediction_train)

    patients_data_train_prediction = model.predict(patients_data_train)

    accuracy_of_train_data = accuracy_score(patients_data_train_prediction, disease_prediction_train)

    disease_prediction_test_prediction = model.predict(patients_data_test)

    test_data_accuracy = accuracy_score(disease_prediction_test_prediction, disease_prediction_test)

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

        st.markdown(
            f'<h2 style="font-size:20px; margin-bottom:10px;">Please choose how you would like to provide your medical details:</h2>',
            unsafe_allow_html=True
        )

        input_mode = st.radio(
            "Select how you want to enter patient data:",
            ["📷 Scan My Report", "⌨️ I can manually enter my data"],
            horizontal=True,
            key="diabetes_input_mode"
        )

        if input_mode == "📷 Scan My Report":

            uploaded_img = st.file_uploader(
                "Upload Medical Reports",
                type=["jpg", "jpeg", "png"],
                key="diabetes_report_uploader"
            )

            if uploaded_img:

                img = Image.open(uploaded_img)

                st.image(img, caption="Scanned Image Preview", width=400)

                extracted_text = pytesseract.image_to_string(img)

                def extract(pattern, text, default=0):

                    match = re.search(pattern, text, re.IGNORECASE)

                    return match.group(1).strip() if match else default

                # Extract values from the uploaded report (OCR-based)

                age = extract(r"age[: ]+(\d+(?:\.\d+)?)", extracted_text, 0)

                bmi = extract(r"bmi[: ]+(\d+(?:\.\d+)?)", extracted_text, 0)

                hba1c = extract(r"(?:hba1c|hb a1c|a1c)(?: level)?[: ]+(\d+(?:\.\d+)?)", extracted_text, 0)

                blood_glucose = extract(r"(?:blood glucose|glucose)(?: level)?[: ]+(\d+(?:\.\d+)?)", extracted_text, 0)

                hypertension = extract(r"hypertension[: ]+([01])", extracted_text, 0)

                heart_disease = extract(r"heart disease[: ]+([01])", extracted_text, 0)

                gender = extract(r"(?:gender|sex)[: ]+(male|female|other)", extracted_text, "Female")

                smoking_history = extract(r"smoking history[: ]+([a-z ]+)", extracted_text, "No Info")

                # Normalize OCR text values

                gender = str(gender).strip().title()

                if gender not in ["Male", "Female", "Other"]:

                    gender = "Female"

                smoking_history = str(smoking_history).strip().lower()

                if smoking_history not in ["never", "former", "current", "not current", "ever", "no info"]:

                    smoking_history = "no info"

                smoking_history = "No Info" if smoking_history == "no info" else smoking_history

                age = float(age)

                bmi = float(bmi)

                hba1c = float(hba1c)

                blood_glucose = float(blood_glucose)

                hypertension = int(hypertension)

                heart_disease = int(heart_disease)

                st.subheader("Auto-Filled Form Below (Editable)")

                # STEP 3 — UI fields auto-fill

                age = st.number_input("Age", min_value=0.0, max_value=100.0, value=age)

                gender = st.selectbox("Gender", ["Female", "Male", "Other"], index=["Female", "Male", "Other"].index(gender))

                hypertension = st.selectbox("Hypertension", [0, 1], index=hypertension, format_func=lambda x: "Yes" if x == 1 else "No")

                heart_disease = st.selectbox("Heart Disease", [0, 1], index=heart_disease, format_func=lambda x: "Yes" if x == 1 else "No")

                smoking_history = st.selectbox("Smoking History", ["No Info", "never", "former", "current", "not current", "ever"], index=["No Info", "never", "former", "current", "not current", "ever"].index(smoking_history))

                bmi = st.number_input("BMI", min_value=5.0, max_value=100.0, value=bmi, step=0.1)

                hba1c = st.number_input("HbA1c Level (%)", min_value=0.0, max_value=20.0, value=hba1c, step=0.1)

                blood_glucose = st.number_input("Blood Glucose Level (mg/dL)", min_value=0, max_value=600, value=int(blood_glucose))

                if st.button("DiabetesAnalyze"):

                    input_data = pd.DataFrame([{
                        "age": age,
                        "hypertension": hypertension,
                        "heart_disease": heart_disease,
                        "bmi": bmi,
                        "HbA1c_level": hba1c,
                        "blood_glucose_level": blood_glucose,
                        "gender": gender,
                        "smoking_history": smoking_history
                    }])

                    input_data = pd.get_dummies(
                        input_data,
                        columns=['gender', 'smoking_history'],
                        dtype=int
                    )

                    input_data = input_data.reindex(columns=feature_columns, fill_value=0)

                    input_data_scaled = scaler.transform(input_data.values)

                    prediction = model.predict(input_data_scaled)

                    if prediction[0] == 0:

                        st.success("✅ Amazing News! Low chance of Diabetes!")

                    else:

                        st.error("⚠️ High chance of Diabetes! Please consult a doctor using the sidebar on the left.")

        else:

            # Manual data entry form

            with st.form("diabetes_form"):

                age = st.number_input("Enter the age:", min_value=0.0, max_value=100.0, value=0.0)

                gender = st.selectbox("Select the gender:", ["Female", "Male", "Other"])

                hypertension = st.selectbox("Does the patient have hypertension?", ["No", "Yes"])

                heart_disease = st.selectbox("Does the patient have heart disease?", ["No", "Yes"])

                smoking_history = st.selectbox("Select the smoking history:", ["No Info", "never", "former", "current", "not current", "ever"])

                bmi = st.number_input("Enter the BMI:", min_value=0.0, max_value=100.0, value=0.0, step=0.1)

                hba1c = st.number_input("Enter the HbA1c level (%):", min_value=0.0, max_value=20.0, value=0.0, step=0.1)

                blood_glucose = st.number_input("Enter the blood glucose level (mg/dL):", min_value=0, max_value=600, value=0)

                submitDiabetes = st.form_submit_button("DiabetesAnalyze")

                if submitDiabetes:

                    hypertension_value = 1 if hypertension == "Yes" else 0

                    heart_disease_value = 1 if heart_disease == "Yes" else 0

                    input_data = pd.DataFrame([{
                        "age": age,
                        "hypertension": hypertension_value,
                        "heart_disease": heart_disease_value,
                        "bmi": bmi,
                        "HbA1c_level": hba1c,
                        "blood_glucose_level": blood_glucose,
                        "gender": gender,
                        "smoking_history": smoking_history
                    }])

                    input_data = pd.get_dummies(
                        input_data,
                        columns=['gender', 'smoking_history'],
                        dtype=int
                    )

                    input_data = input_data.reindex(columns=feature_columns, fill_value=0)

                    input_data_scaled = scaler.transform(input_data.values)

                    prediction = model.predict(input_data_scaled)

                    if prediction[0] == 0:

                        st.success("✅ Amazing News! Low chance of Diabetes!")

                    else:

                        st.error("⚠️ High chance of Diabetes! Please consult a doctor using the sidebar on the left.")
