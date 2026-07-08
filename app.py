import streamlit as st
import json
import os
from groq import Groq
from dotenv import load_dotenv
import pypdf



# 1. PAGE SETUP

st.set_page_config(page_title="Llama Claims Agent", layout="wide")
st.title("⚡ Autonomous Claims Processing Agent (Powered by Groq & Llama)")
st.caption("A lightning-fast open-source pipeline for structural FNOL parsing and automated routing.")
st.markdown("---")



# 2. INITIALIZE GROQ CLIENT

load_dotenv()
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

# If you prefer testing locally without setting env vars, you can paste it here directly:
# GROQ_API_KEY = "gsk_xxxx..."
if not GROQ_API_KEY:
    st.warning("⚠️ GROQ_API_KEY not found. Please set it as an environment variable or add it directly to the script code.")
client = Groq(api_key=GROQ_API_KEY)




models = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant"
]

MODEL_NAME = st.selectbox("Choose Model", models)




# 3. CORE PROCESSING LOGIC
def extract_fields_with_llama(text_content: str) -> dict:
    """Sends raw text to Llama 3.3 on Groq and forces a strict JSON response."""
    system_prompt = """
    You are a precise insurance data extraction engine. Analyze the provided FNOL text and extract the target values.
    
    CRITICAL INSTRUCTIONS:
    1. Respond ONLY with a valid, raw JSON object. 
    2. Do NOT wrap your response in markdown formatting (no ```json or ``` blocks). No conversational filler text.
    3. If a field is missing or not mentioned, assign it null.
    4. Strip currency symbols like '$' or commas from 'estimated_damage' and 'initial_estimate'—extract them purely as numerical numbers (floats/integers).
    
    JSON Schema Template:
    {
        "policy_number": "string or null",
        "policyholder_name": "string or null",
        "effective_dates": "string or null",
        "incident_date": "string or null",
        "incident_time": "string or null",
        "incident_location": "string or null",
        "incident_description": "string or null",
        "claimant": "string or null",
        "third_parties": ["string"] or null,
        "contact_details": "string or null",
        "asset_type": "string or null",
        "asset_id": "string or null",
        "estimated_damage": number or null,
        "claim_type": "string or null",
        "attachments": ["string"] or null,
        "initial_estimate": number or null
    }
    """



    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Extract fields from this text:\n\n{text_content}"}
        ],
        temperature=0.0,
        response_format={"type": "json_object"}  # Forces Groq to guarantee valid JSON output
    )




    raw_json_string = completion.choices[0].message.content.strip()
    return json.loads(raw_json_string)




def run_business_rules(extracted_data: dict) -> dict:
    """Applies predictable Python logic to determine the routing queue."""
   
    if isinstance(extracted_data, list):
        if len(extracted_data) > 0 and isinstance(extracted_data[0], dict):
            extracted_data = extracted_data[0]
        else:
            
            extracted_data = {}
    mandatory_fields = [
        "policy_number","policyholder_name","effective_dates",
        "incident_date","incident_time","incident_location",
        "incident_description","claimant","contact_details",
        "asset_type","asset_id","estimated_damage",
        "claim_type","attachments","initial_estimate"
    ]
    missing_fields = [field for field in mandatory_fields if not extracted_data.get(field)]
    desc = (extracted_data.get("incident_description") or "").lower()
    claim_type = (extracted_data.get("claim_type") or "").strip().lower()
    damage = extracted_data.get("estimated_damage")
    try:
        damage = float(str(damage).replace(",","").replace("₹","").replace("$","").strip())
    except:
        damage = 0
    # Check for Fraud Keywords
    fraud_keywords = ["fraud","fraudulent","inconsistent","staged","fake","suspicious","intentional","collision scam","false statement"]
    flagged_for_fraud = any(word in desc for word in fraud_keywords)
    # Evaluation Flow Chart Logic
    if missing_fields:
        route = "Manual Review"
        reason = f"Mandatory fields missing: {', '.join(missing_fields)}."
    elif flagged_for_fraud:
        route = "Investigation Flag"
        reason = "Fraud-related keywords detected in the incident description."
    elif claim_type.strip().lower() == "injury":
        route = "Specialist Queue"
        reason = f"Claim type is '{claim_type}', so it requires a specialist."
    elif damage < 25000:
        route = "Fast-track"
        reason = f"Estimated damage (₹{damage:,.0f}) is below ₹25,000."
    else:
        route = "Standard Review"
        reason = f"Estimated damage (₹{damage:,.0f}) is ₹25,000 or above."

    return {
        "extractedFields": extracted_data,
        "missingFields": missing_fields,
        "recommendedRoute": route,
        "reasoning": reason
    }






# 4. SPLIT SCREEN FRONTEND
left_column, right_column = st.columns(2, gap="large")
# --- LEFT COLUMN: INPUT ---
with left_column:
    st.subheader("📁 1. Document Dropzone")
    uploaded_file = st.file_uploader(
        "Upload FNOL Document",
        type=["txt", "pdf"],
        label_visibility="collapsed"
    )
    raw_text = ""
    if uploaded_file is not None:
        st.success(f"📎 Loaded: {uploaded_file.name}")
        # Parse file types dynamically
        if uploaded_file.type == "text/plain":
            raw_text = uploaded_file.read().decode("utf-8")
        elif uploaded_file.type == "application/pdf":
            pdf_reader = pypdf.PdfReader(uploaded_file)
            pages=[]
            for page in pdf_reader.pages:
                text=page.extract_text()
                if text:
                    pages.append(text)
            raw_text="\n".join(pages)
        with st.expander("🔍 View Raw Text Input Preview"):
            st.text(raw_text)





# --- RIGHT COLUMN: OUTPUT ---
with right_column:
    st.subheader("📦 2. Generated Response JSON")
    if uploaded_file is not None and GROQ_API_KEY:
        if st.button("Run Autonomous Agent 🚀", type="primary", use_container_width=True):
            with st.spinner("Llama is reading file and computing route logic..."):
                try:
                    # Execute Agent pipeline steps
                    extracted_fields = extract_fields_with_llama(raw_text)
                    final_result = run_business_rules(extracted_fields)
                    # Highlight the Route Decision
                    st.info(f"**Route Assigned:** {final_result['recommendedRoute']}")
                    # Code display widget featuring built-in single-click "Copy" function
                    st.subheader("Extracted Fields")
                    st.json(extracted_fields)
                    st.code(json.dumps(final_result, indent=2), language="json")
                    st.download_button("Download JSON",json.dumps(final_result,indent=2),"claim_result.json","application/json")
                except Exception as e:
                    st.error(f"Execution Error: {e}")
    else:
        if not uploaded_file:
            st.info("Drop a file into the left panel to execute the AI agent pipeline.")
