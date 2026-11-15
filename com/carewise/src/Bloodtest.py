
import streamlit as st
import pytesseract
import re
import io
import csv
from PIL import Image, ImageEnhance

# Parameters below are limited to those present in the supplied sample report.
# Reference intervals are taken from that report where available.

PARAMETERS = {
    # COMPLETE URINE EXAMINATION
    "Volume": {"aliases": ["volume"], "unit": "mL", "ref": ">1.5", "kind": "number"},
    "Colour": {"aliases": ["colour", "color"], "unit": "", "ref": "Not stated", "kind": "text"},
    "Transparency": {"aliases": ["transparency"], "unit": "", "ref": "Clear", "kind": "text"},
    "pH": {"aliases": ["ph"], "unit": "", "ref": "5.0 - 8.0", "kind": "number", "low": 5.0, "high": 8.0},
    "Specific Gravity": {"aliases": ["specific gravity"], "unit": "", "ref": "1.001 - 1.030", "kind": "number", "low": 1.001, "high": 1.030},
    "Protein": {"aliases": ["protein"], "unit": "", "ref": "Negative", "kind": "qualitative"},
    "Glucose": {"aliases": ["glucose"], "unit": "", "ref": "Negative", "kind": "qualitative"},
    "Blood (urine)": {"aliases": ["blood"], "unit": "", "ref": "Negative", "kind": "qualitative"},
    "Ketone": {"aliases": ["ketone"], "unit": "", "ref": "Negative", "kind": "qualitative"},
    "Bilirubin (urine)": {"aliases": ["bilirubin"], "unit": "", "ref": "Negative", "kind": "qualitative"},
    "Urobilinogen": {"aliases": ["urobilinogen"], "unit": "", "ref": "Negative", "kind": "qualitative"},
    "Nitrite": {"aliases": ["nitrite"], "unit": "", "ref": "Negative", "kind": "qualitative"},
    "Leucocyte Esterase": {"aliases": ["leucocyte esterase", "leukocyte esterase"], "unit": "", "ref": "Absent", "kind": "qualitative"},
    "WBC / Pus Cells": {"aliases": ["wbc pus cells", "pus cells", "wbc"], "unit": "/hpf", "ref": "0 - 5", "kind": "number", "low": 0, "high": 5},
    "Transitional / Squamous epithelial cells": {"aliases": ["transitional squamous epithelial cells", "squamous epithelial cells", "epithelial cells"], "unit": "/hpf", "ref": "0 - 4", "kind": "number", "low": 0, "high": 4},
    "RBCs (urine)": {"aliases": ["rbcs"], "unit": "/hpf", "ref": "0 - 2", "kind": "number", "low": 0, "high": 2},
    "Crystals": {"aliases": ["crystals"], "unit": "", "ref": "Absent", "kind": "qualitative"},
    "Casts": {"aliases": ["casts"], "unit": "", "ref": "Absent", "kind": "qualitative"},
    "Bacteria": {"aliases": ["bacteria"], "unit": "", "ref": "Not stated", "kind": "qualitative"},

    # COMPLETE BLOOD COUNT
    "Haemoglobin": {"aliases": ["hemoglobin hb", "haemoglobin hb", "hemoglobin", "haemoglobin", "hb"], "unit": "g/dL", "ref": "12 - 15", "kind": "number", "low": 12, "high": 15},
    "RBC Count": {"aliases": ["red blood cell rbc count", "rbc count", "red blood cell count"], "unit": "million/cu.mm", "ref": "3.8 - 4.8", "kind": "number", "low": 3.8, "high": 4.8},
    "PCV / Haematocrit": {"aliases": ["packed cell volume pcv hematocrit", "packed cell volume", "hematocrit", "haematocrit", "pcv"], "unit": "%", "ref": "36 - 46", "kind": "number", "low": 36, "high": 46},
    "MCV": {"aliases": ["mean corpuscular volume mcv", "mean corpuscular volume", "mcv"], "unit": "fL", "ref": "83 - 101", "kind": "number", "low": 83, "high": 101},
    "MCH": {"aliases": ["mean corpuscular hemoglobin mch", "mean corpuscular haemoglobin mch", "mean corpuscular hemoglobin", "mean corpuscular haemoglobin", "mch"], "unit": "pg", "ref": "27 - 32", "kind": "number", "low": 27, "high": 32},
    "MCHC": {"aliases": ["mean corpuscular hb concentration mchc", "mean corpuscular hemoglobin concentration", "mean corpuscular haemoglobin concentration", "mchc"], "unit": "g/dL", "ref": "31.5 - 34.5", "kind": "number", "low": 31.5, "high": 34.5},
    "RDW": {"aliases": ["red cell distribution width rdw", "red cell distribution width", "rdw"], "unit": "%", "ref": "11.6 - 14", "kind": "number", "low": 11.6, "high": 14},
    "Total Leucocyte Count (TLC)": {"aliases": ["total leucocyte count tlc", "total leukocyte count", "tlc"], "unit": "cells/µL", "ref": "4000 - 11000", "kind": "number", "low": 4000, "high": 11000},

    # DIFFERENTIAL LEUCOCYTE COUNT
    "Neutrophils (%)": {"aliases": ["neutrophils"], "unit": "%", "ref": "40 - 75", "kind": "number", "low": 40, "high": 75},
    "Lymphocytes (%)": {"aliases": ["lymphocytes"], "unit": "%", "ref": "20 - 40", "kind": "number", "low": 20, "high": 40},
    "Monocytes (%)": {"aliases": ["monocytes"], "unit": "%", "ref": "0 - 6", "kind": "number", "low": 0, "high": 6},
    "Eosinophils (%)": {"aliases": ["eosinophils"], "unit": "%", "ref": "0 - 6", "kind": "number", "low": 0, "high": 6},
    "Basophils (%)": {"aliases": ["basophils"], "unit": "%", "ref": "1 - 2", "kind": "number", "low": 1, "high": 2},
    "Neutrophils (absolute)": {"aliases": ["neutrophils cells cu mm", "neutrophils absolute"], "unit": "cells/cu.mm", "ref": "2000 - 7000", "kind": "number", "low": 2000, "high": 7000},
    "Lymphocytes (absolute)": {"aliases": ["lymphocytes cells cu mm", "lymphocytes absolute"], "unit": "cells/cu.mm", "ref": "1000 - 3000", "kind": "number", "low": 1000, "high": 3000},
    "Monocytes (absolute)": {"aliases": ["monocytes cells cu mm", "monocytes absolute"], "unit": "cells/cu.mm", "ref": "200 - 1000", "kind": "number", "low": 200, "high": 1000},
    "Eosinophils (absolute)": {"aliases": ["eosinophils cells cu mm", "eosinophils absolute"], "unit": "cells/cu.mm", "ref": "10 - 600", "kind": "number", "low": 10, "high": 600},
    "Basophils (absolute)": {"aliases": ["basophils cells cu mm", "basophils absolute"], "unit": "cells/cu.mm", "ref": "0 - 100", "kind": "number", "low": 0, "high": 100},
    "Platelet Count": {"aliases": ["platelet count"], "unit": "10^3/µL", "ref": "150 - 410", "kind": "number", "low": 150, "high": 410},
    "MPV": {"aliases": ["mean platelet volume mpv", "mean platelet volume", "mpv"], "unit": "fL", "ref": "7.6 - 9.6", "kind": "number", "low": 7.6, "high": 9.6},

    # PERIPHERAL BLOOD SMEAR
    "RBC smear description": {"aliases": ["rbc"], "unit": "", "ref": "Descriptive finding", "kind": "smear"},
    "WBC smear description": {"aliases": ["wbc"], "unit": "", "ref": "Descriptive finding", "kind": "smear"},
    "Platelet smear description": {"aliases": ["platelets"], "unit": "", "ref": "Descriptive finding", "kind": "smear"},
    "Hemoparasites": {"aliases": ["hemoparasites"], "unit": "", "ref": "Not seen", "kind": "qualitative"},
    "Peripheral smear impression": {"aliases": ["impression"], "unit": "", "ref": "Descriptive finding", "kind": "smear"},

    # IMMUNOASSAYS
    "TSH": {"aliases": ["thyroid stimulating hormone tsh", "thyroid stimulating hormone", "tsh"], "unit": "µIU/mL", "ref": "0.51 - 4.3", "kind": "number", "low": 0.51, "high": 4.3},
    "Vitamin D, 25-OH": {"aliases": ["vitamin d 25 oh", "vitamin d"], "unit": "ng/mL", "ref": "30 - 100 (sufficiency)", "kind": "number", "low": 30, "high": 100},
    "Vitamin B12": {"aliases": ["vitamin b12 cyanocobalamin", "vitamin b12", "cyanocobalamin"], "unit": "pg/mL", "ref": "197 - 771", "kind": "number", "low": 197, "high": 771}
}


def _normalise(text):
    text = text.lower().replace("µ", "u").replace("μ", "u")
    text = re.sub(r"[^a-z0-9./+\- ]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _find_numeric_after_label(text, aliases):
    lines = text.splitlines()
    for line in lines:
        norm = _normalise(line)
        for alias in sorted(aliases, key=len, reverse=True):
            a = _normalise(alias)
            match = re.search(r"(?<![a-z])" + re.escape(a) + r"(?![a-z])", norm)
            if not match:
                continue
            tail = norm[match.end():]
            nums = re.findall(r"(?<![a-z])[-+]?\d[\d,]*(?:\.\d+)?", tail)
            if nums:
                try:
                    return float(nums[0].replace(",", ""))
                except ValueError:
                    pass
    return None


def extract_report_values(image):
    img = image.convert("RGB")
    img = img.resize((img.width * 2, img.height * 2))
    img = ImageEnhance.Contrast(img).enhance(1.6)
    text = pytesseract.image_to_string(img, config="--psm 6")
    found = {}
    for name, info in PARAMETERS.items():
        if info["kind"] == "number":
            value = _find_numeric_after_label(text, info["aliases"])
            if value is not None:
                found[name] = value
    return found, text


def analyse_value(name, value):
    info = PARAMETERS[name]
    low = info.get("low")
    high = info.get("high")

    if low is None or high is None:
        return "REVIEW", "Compare this result with the laboratory's printed reference information."
    if value < low:
        return "LOW", f"{name} is below the reference interval shown in the sample report."
    if value > high:
        return "HIGH", f"{name} is above the reference interval shown in the sample report."
    return "NORMAL", f"{name} is within the reference interval shown in the sample report."


def get_suggestion(name, status):
    suggestions = {
        "Haemoglobin": {
            "LOW": "Include iron-containing foods such as lentils, beans, leafy greens and fortified cereals. Pair plant-based iron foods with vitamin-C foods such as citrus, guava or tomatoes. Ask a clinician whether ferritin, iron, B12 or folate testing is needed. Do not start iron tablets without advice.",
            "HIGH": "A high result can have several causes, including dehydration. Maintain normal hydration and arrange a clinician review; do not try to lower it through diet alone."
        },
        "RBC Count": {
            "LOW": "Discuss possible causes such as iron, B12 or folate deficiency with a clinician. Food changes depend on the cause.",
            "HIGH": "Maintain normal hydration and ask a clinician to interpret this alongside haemoglobin and haematocrit."
        },
        "PCV / Haematocrit": {
            "LOW": "Discuss this alongside haemoglobin and RBC count. Ask a clinician whether iron, B12 or folate testing is appropriate.",
            "HIGH": "Dehydration can affect this result. Maintain normal hydration and arrange clinical review."
        },
        "MCV": {
            "LOW": "A low MCV can be associated with iron deficiency or other conditions. Ask a clinician about ferritin and iron studies; do not self-start iron.",
            "HIGH": "A high MCV can be associated with B12 or folate deficiency, among other causes. Discuss B12 and folate testing with a clinician."
        },
        "MCH": {
            "LOW": "Discuss this with a clinician alongside haemoglobin, MCV and iron studies. Include balanced iron-containing foods if appropriate.",
            "HIGH": "Interpret this with MCV and MCHC. Ask a clinician whether further testing is needed."
        },
        "MCHC": {
            "LOW": "Discuss this alongside haemoglobin and MCV. A clinician can determine whether iron studies or other tests are needed.",
            "HIGH": "A raised MCHC needs interpretation with the full blood count and sometimes a repeat test. Discuss it with a clinician."
        },
        "RDW": {
            "HIGH": "A raised RDW can occur with nutritional deficiencies or mixed red-cell changes. Ask a clinician whether ferritin, B12 or folate testing is appropriate."
        },
        "Total Leucocyte Count (TLC)": {
            "LOW": "Review this with a clinician alongside the differential count and medicines. Seek prompt medical advice if you have fever or feel unwell.",
            "HIGH": "This can occur with infection, inflammation, stress or medicines. Discuss symptoms and the full CBC with a clinician."
        },
        "Platelet Count": {
            "LOW": "Avoid self-treatment or supplements intended to raise platelets. Contact a clinician for advice; seek urgent care for unusual bleeding, blood in urine or stool, or widespread bruising.",
            "HIGH": "A high platelet count can have several causes, including inflammation or iron deficiency. Discuss the result and whether a repeat CBC is needed."
        },
        "MPV": {
            "LOW": "Interpret this with the platelet count and full blood count. Ask a clinician whether follow-up is needed.",
            "HIGH": "Interpret this with the platelet count and full blood count. Discuss persistent abnormalities with a clinician."
        },
        "TSH": {
            "LOW": "A low TSH may need thyroid hormone testing and clinical review. Do not change thyroid medication without medical advice.",
            "HIGH": "A high TSH may need free T4 testing and clinical review. Do not start or change thyroid medication without medical advice."
        },
        "Vitamin D, 25-OH": {
            "LOW": "Include suitable sources such as fortified foods, eggs and oily fish if part of your diet. Discuss safe sunlight exposure and whether supplementation is appropriate with a clinician.",
            "HIGH": "Avoid high-dose vitamin D supplements unless prescribed. Discuss the result and any supplements you take with a clinician."
        },
        "Vitamin B12": {
            "LOW": "Include B12 sources such as dairy, eggs, fish, meat or fortified foods, depending on your diet. Discuss the cause and whether supplementation or treatment is needed with a clinician.",
            "HIGH": "Review supplements and injections with a clinician. Do not stop prescribed treatment without advice."
        },
        "pH": {
            "LOW": "Urine pH can vary with diet and other factors. Do not try to change it with foods or supplements; discuss persistent abnormalities with a clinician.",
            "HIGH": "Urine pH varies with diet, medicines and health conditions. Discuss this with a clinician, particularly if you have urinary symptoms."
        },
        "Specific Gravity": {
            "LOW": "This can reflect dilute urine. Maintain normal hydration and discuss persistent results with a clinician.",
            "HIGH": "This can occur with concentrated urine. Maintain normal hydration unless fluid restriction has been prescribed, and discuss persistent results with a clinician."
        },
        "WBC / Pus Cells": {
            "HIGH": "This can occur with urinary tract inflammation or infection, but it is not diagnostic by itself. Contact a clinician, especially with burning urination, fever, urgency or pain; a urine culture may be considered."
        },
        "RBCs (urine)": {
            "HIGH": "Blood cells in urine need clinical assessment. Contact a clinician for interpretation and possible repeat urine testing; seek prompt care if you can see blood or have pain or fever."
        },
        "Transitional / Squamous epithelial cells": {
            "HIGH": "A raised count can sometimes reflect sample contamination. Ask whether a repeat clean-catch urine sample is needed, especially if other urine findings are abnormal."
        },
        "Volume": {
            "LOW": "Urine volume depends on fluid intake and health conditions. Maintain normal hydration unless fluid restriction has been prescribed, and discuss persistently low output with a clinician."
        },
        "Neutrophils (%)": {
            "LOW": "Review this alongside the total WBC and absolute neutrophil count with a clinician. Seek prompt medical advice if you have fever or signs of infection.",
            "HIGH": "This can occur with infection, inflammation, stress or medicines. Discuss the result and symptoms with a clinician."
        },
        "Lymphocytes (%)": {
            "LOW": "Interpret this with the absolute lymphocyte count and total WBC. Ask a clinician whether repeat testing or follow-up is needed.",
            "HIGH": "This can occur with infections and other conditions. Discuss it with a clinician, who can interpret the absolute count and symptoms."
        },
        "Monocytes (%)": {
            "LOW": "Interpret this with the absolute count and other CBC findings. Ask a clinician whether follow-up is needed.",
            "HIGH": "This can occur during or after infections and with inflammatory conditions. Discuss persistent elevation with a clinician."
        },
        "Eosinophils (%)": {
            "LOW": "A low percentage is often interpreted with the absolute count and other CBC findings. Ask a clinician if follow-up is needed.",
            "HIGH": "This can be associated with allergies, asthma, medication reactions or parasites. Discuss symptoms and possible causes with a clinician; do not self-treat for parasites."
        },
        "Basophils (%)": {
            "LOW": "Interpret this with the absolute count and full CBC. A low percentage alone often has limited meaning; ask your clinician if follow-up is needed.",
            "HIGH": "Discuss this with a clinician alongside the absolute basophil count and other CBC results, particularly if it remains elevated."
        },
        "Neutrophils (absolute)": {
            "LOW": "A low absolute neutrophil count can increase infection risk. Contact a clinician for interpretation; seek urgent medical advice for fever, especially if you feel unwell.",
            "HIGH": "Discuss the result with a clinician; infection, inflammation, stress and some medicines can affect the count."
        },
        "Lymphocytes (absolute)": {
            "LOW": "Discuss this with a clinician alongside your symptoms, medicines and other CBC results. Seek prompt advice if you have recurrent or severe infections.",
            "HIGH": "Discuss persistent elevation with a clinician, who may consider a repeat CBC or further tests based on symptoms."
        },
        "Monocytes (absolute)": {
            "LOW": "Interpret this with the rest of the CBC. Ask a clinician whether any follow-up is needed.",
            "HIGH": "This can occur with infection or inflammation. Discuss persistent elevation and symptoms with a clinician."
        },
        "Eosinophils (absolute)": {
            "LOW": "A low result alone often has limited significance. Review it with the full CBC if your clinician recommends follow-up.",
            "HIGH": "Discuss possible allergies, asthma, medication reactions or parasitic exposure with a clinician. Do not start treatment without identifying the cause."
        },
        "Basophils (absolute)": {
            "LOW": "A low result alone often has limited significance. Interpret it with the full CBC and ask your clinician if follow-up is needed.",
            "HIGH": "Discuss this with a clinician alongside the rest of the CBC, especially if the elevation persists."
        }
    }

    if name in suggestions and status in suggestions[name]:
        return suggestions[name][status]
    if status == "LOW":
        return "Discuss this result with a healthcare professional and interpret it alongside your symptoms and other test results. Do not start supplements or medicines based on this result alone."
    return "Discuss this result with a healthcare professional to identify the cause. Do not try to correct it through diet or supplements alone."


def render():
    st.title("Please provide your medical details")
    st.write("Please choose how you would like to provide your medical details:")

    left_col, right_col = st.columns([2, 1])

    with right_col:
        st.markdown(
            '<div style="background-color:#e8f5e8;border-left:3px solid #4caf50;padding:8px;margin:6px 0;border-radius:4px;">'
            '<p style="color:#2e7d32;margin:0;font-weight:600;font-size:14px;">🩺 Blood Test Report</p>'
            '<p style="color:#388e3c;margin:2px 0 0 0;font-size:12px;">OCR-assisted report reading</p></div>',
            unsafe_allow_html=True
        )

    with left_col:
        input_mode = st.radio(
            "Select how you want to enter patient data:",
            ["📷 Scan Blood Test Report", "⌨️ Manually Enter Data"],
            horizontal=True,
            key="cw_lab_input_mode"
        )

    prefill = {}

    if input_mode == "📷 Scan Blood Test Report":
        uploaded = st.file_uploader(
            "Upload Medical Report",
            type=["jpg", "jpeg", "png"],
            key="carewise_lab_report_uploader"
        )

        if uploaded:
            img = Image.open(uploaded).convert("RGB")
            st.image(img, width=250)

            if st.button("Read Blood Test Report", key="cw_lab_scan_button"):
                with st.spinner("Reading report..."):
                    try:
                        extracted_values, raw_text = extract_report_values(img)

                        for parameter_name in PARAMETERS:
                            st.session_state.pop(f"cw_lab_input_{parameter_name}", None)

                        st.session_state["cw_lab_prefill"] = {
                            name: str(value) for name, value in extracted_values.items()
                        }
                        st.session_state["cw_lab_raw_text"] = raw_text
                        st.session_state.pop("cw_lab_results", None)
                        st.session_state.pop("cw_lab_results_ready", None)

                        if extracted_values:
                            st.success(
                                f"Extracted {len(extracted_values)} numeric parameters. Please verify the values below."
                            )
                        else:
                            st.warning(
                                "No numeric parameters were confidently extracted. Please enter your values manually below."
                            )

                    except Exception as exc:
                        st.error(f"Could not read the image: {exc}")

        prefill = st.session_state.get("cw_lab_prefill", {})

        if uploaded and not prefill:
            st.info("Upload a report and select Read Blood Test Report to extract available values.")

    else:
        st.session_state.pop("cw_lab_prefill", None)
        prefill = {}

    st.subheader(
        "Enter Medical Details"
        if input_mode == "⌨️ Manually Enter Data"
        else "Auto-Filled Form Below (Editable)"
    )

    st.caption(
        "Values start at 0.0. Replace them with the values shown on your laboratory report. "
        "Text-based observations can be entered in the relevant fields."
    )

    section_names = {
        "COMPLETE URINE EXAMINATION": [
            "Volume", "Colour", "Transparency", "pH", "Specific Gravity",
            "Protein", "Glucose", "Blood (urine)", "Ketone", "Bilirubin (urine)",
            "Urobilinogen", "Nitrite", "Leucocyte Esterase", "WBC / Pus Cells",
            "Transitional / Squamous epithelial cells", "RBCs (urine)",
            "Crystals", "Casts", "Bacteria"
        ],
        "COMPLETE BLOOD COUNT": [
            "Haemoglobin", "RBC Count", "PCV / Haematocrit", "MCV",
            "MCH", "MCHC", "RDW", "Total Leucocyte Count (TLC)"
        ],
        "DIFFERENTIAL LEUCOCYTE COUNT": [
            "Neutrophils (%)", "Lymphocytes (%)", "Monocytes (%)",
            "Eosinophils (%)", "Basophils (%)", "Neutrophils (absolute)",
            "Lymphocytes (absolute)", "Monocytes (absolute)",
            "Eosinophils (absolute)", "Basophils (absolute)",
            "Platelet Count", "MPV"
        ],
        "PERIPHERAL BLOOD SMEAR": [
            "RBC smear description", "WBC smear description",
            "Platelet smear description", "Hemoparasites",
            "Peripheral smear impression"
        ],
        "IMMUNOASSAYS": [
            "TSH", "Vitamin D, 25-OH", "Vitamin B12"
        ]
    }

    entered_values = {}

    with st.form("cw_lab_results_form"):
        for section, names in section_names.items():
            st.markdown(f"### {section.title()}")
            columns = st.columns(2)

            for index, name in enumerate(names):
                info = PARAMETERS[name]

                with columns[index % 2]:
                    if info["kind"] == "number":
                        default = str(prefill.get(name, "0.0"))

                        raw_value = st.text_input(
                            f"{name} ({info['unit']})" if info["unit"] else name,
                            value=default,
                            key=f"cw_lab_input_{name}"
                        )

                        entered_values[name] = raw_value

                    else:
                        entered_values[name] = st.text_input(
                            name,
                            value=str(prefill.get(name, "")),
                            key=f"cw_lab_input_{name}"
                        )

        analyze = st.form_submit_button(
            "Analyze Report",
            use_container_width=True
        )

    if analyze:
        results = {}
        invalid = []

        for name, raw_value in entered_values.items():
            info = PARAMETERS[name]

            if info["kind"] == "number":
                try:
                    results[name] = float(
                        str(raw_value).replace(",", "").strip() or "0"
                    )
                except ValueError:
                    invalid.append(name)

            elif str(raw_value).strip():
                results[name] = str(raw_value).strip()

        if invalid:
            st.error("Please enter a valid number for: " + ", ".join(invalid))
        else:
            st.session_state["cw_lab_results"] = results
            st.session_state["cw_lab_results_ready"] = True

    if st.session_state.get("cw_lab_results_ready") and "cw_lab_results" in st.session_state:
        results = st.session_state["cw_lab_results"]

        st.divider()
        st.subheader("Blood Test Analysis Results")

        rows = []

        for name, value in results.items():
            info = PARAMETERS[name]

            if info["kind"] == "number":
                status, explanation = analyse_value(name, float(value))
                suggestion = (
                    get_suggestion(name, status)
                    if status in ["LOW", "HIGH"]
                    else ""
                )
            else:
                status = "RECORDED"
                explanation = "Recorded for clinician review; no automatic interpretation applied."
                suggestion = ""

            rows.append({
                "Parameter": name,
                "Value": value,
                "Unit": info["unit"],
                "Reference range": info["ref"],
                "Status": status,
                "Explanation": explanation
            })

            if suggestion:
                st.warning(
                    f"**{name}: {status}**\n\n{suggestion}"
                )

        if rows:
            st.dataframe(
                rows,
                use_container_width=True,
                hide_index=True
            )

            output = io.StringIO()
            writer = csv.DictWriter(
                output,
                fieldnames=list(rows[0].keys())
            )
            writer.writeheader()
            writer.writerows(rows)

            st.download_button(
                "Download extracted results",
                data=output.getvalue(),
                file_name="CareWise_Lab_Report_Results.csv",
                mime="text/csv"
            )

    st.caption(
        "Important: Reference intervals are reproduced from the supplied report where stated. "
        "They are specific to that laboratory and patient context and should not be treated as universal ranges. "
        "OCR results must be checked against the original report. This tool is not a diagnosis."
    )
