import base64
import io
import os
import streamlit as st
from dotenv import load_dotenv
from PIL import Image
import pdf2image
import google.genai as genai
load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
def get_gemini_response(input_text, pdf_content, prompt):
    contents = [input_text]
    for pdf_part in pdf_content:
        contents.append({
            "inline_data": {
                "mime_type": pdf_part["mime_type"],
                "data": pdf_part["data"]
            }
        })
    contents.append(prompt)
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=contents
    )
    return response.text

def input_pdf_setup(upload_file):
    if upload_file is None:
        raise FileNotFoundError("No file uploaded")
    upload_file.seek(0)
    if upload_file.type != "application/pdf":
        st.error("Please upload a valid PDF file.")
        return None
    try:
        images = pdf2image.convert_from_bytes(
            upload_file.read(),
            poppler_path="/opt/homebrew/bin"  
        )
    except Exception as e:
        st.error(f"PDF processing failed: {e}")
        return None
    pdf_parts = []
    for image in images:
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format="JPEG")
        pdf_parts.append({
            "mime_type": "image/jpeg",
            "data": base64.b64encode(img_byte_arr.getvalue()).decode("utf-8")
        })
    return pdf_parts
st.set_page_config(page_title="ATS Resume Screener", layout="centered")
st.header("📄 ATS Resume Screener Using API")
input_text = st.text_area(
    "Enter the Job Description:",
    key="job_description"
)
uploaded_file = st.file_uploader(
    "Upload Candidate Resume (PDF)",
    type=["pdf"]
)
if uploaded_file:
    st.success("Resume uploaded successfully!")
submit1 = st.button("Analyze This Candidate")
input_prompt1 = """
You are an expert ATS and HR professional in data science.
Analyze the resume and provide:
1. Key strengths
2. Weaknesses
3. Skill gaps
4. Overall suitability
5. Recommendations for improvement
"""
if submit1:
    if not uploaded_file:
        st.warning("Please upload a resume first.")
    else:
        with st.spinner("Analyzing resume..."):
            pdf_content = input_pdf_setup(uploaded_file)
            if pdf_content:
                if submit1:
                    response = get_gemini_response(
                        input_text, pdf_content, input_prompt1
                    )
                    st.subheader("📌 Candidate Analysis")
                    st.write(response)