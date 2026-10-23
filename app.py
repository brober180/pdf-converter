import streamlit as st
import google.generativeai as genai
import pdfplumber
import json
import pandas as pd

st.set_page_config(page_title="PDF to CSV Converter", layout="centered")

st.title("📊 PDF Statement to CSV Converter")
st.write("Drop any messy PDF statement, invoice, or report below to instantly convert it into a clean spreadsheet.")

api_key = st.text_input("Enter your free Google AI Studio API Key:", type="password")

uploaded_file = st.file_uploader("Upload your PDF document", type=["pdf"])

if uploaded_file and api_key:
    if st.button("Convert to Spreadsheet"):
        with st.spinner("Extracting and structuring data..."):
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel("gemini-1.5-flash")

                with pdfplumber.open(uploaded_file) as pdf:
                    raw_text = "".join([page.extract_text() or "" for page in pdf.pages])

                prompt = """
                You are an expert data parser. Extract all line-item data (such as dates, descriptions, amounts, categories, or reference numbers) from the document text below.
                Return ONLY a valid JSON array of objects representing rows in a spreadsheet table. 
                Example format:
                [
                  {"Date": "2026-10-01", "Description": "Grocery Store", "Amount": "-45.50", "Category": "Food"}
                ]
                Do not include markdown blocks like ```json or any conversational text. Output raw JSON only.
                """

                response = model.generate_content(
                    [f"{prompt}\n\nDOCUMENT TEXT:\n{raw_text}"],
                    generation_config={"response_mime_type": "application/json"}
                )

                data = json.loads(response.text)
                df = pd.DataFrame(data)

                st.success("Conversion Successful!")
                st.dataframe(df)

                csv_data = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Clean CSV File",
                    data=csv_data,
                    file_name="converted_statement.csv",
                    mime="text/csv"
                )

            except Exception as e:
                st.error(f"An error occurred during processing: {e}")