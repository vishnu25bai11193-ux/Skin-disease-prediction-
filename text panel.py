"""
Equiderma AI - Clinical Advisor Dashboard
Multimodal Skin Disease Prediction across Diverse Skin Tones (Zero OpenCV)
Flask Backend (Port 9999) + ChromaDB RAG + Ollama Multimodal Vision Advisor
"""

import base64
import io
import datetime
import requests
import streamlit as st
from PIL import Image

# Import local fallback knowledge so UI is never blank even if server is offline
from backend.knowledge_data import DERMATOLOGY_KNOWLEDGE_BASE
from backend.config import FITZPATRICK_SCALE

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Equiderma Clinical Advisor",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- MODERN MEDICAL STYLING ---
st.markdown("""
<style>
/* Main typography and card layout */
.stApp {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}
.clinical-banner {
    background: linear-gradient(135deg, #102a43 0%, #243b53 50%, #334e68 100%);
    padding: 22px 28px;
    border-radius: 12px;
    color: white;
    margin-bottom: 20px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}
.clinical-banner h1 {
    margin: 0;
    color: #ffffff !important;
    font-size: 2rem;
    font-weight: 700;
}
.clinical-banner p {
    margin: 6px 0 0 0;
    color: #bcccdc;
    font-size: 1rem;
}
.badge-high {
    background: #ffebee;
    color: #c62828;
    border: 1.5px solid #ef5350;
    padding: 5px 14px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 0.95rem;
    display: inline-block;
}
.badge-med {
    background: #fff8e1;
    color: #e65100;
    border: 1.5px solid #ffa726;
    padding: 5px 14px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 0.95rem;
    display: inline-block;
}
.badge-low {
    background: #e8f5e9;
    color: #2e7d32;
    border: 1.5px solid #66bb6a;
    padding: 5px 14px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 0.95rem;
    display: inline-block;
}
.tone-box {
    background: #f0f4f8;
    border-left: 4px solid #334e68;
    border-radius: 0 8px 8px 0;
    padding: 14px 18px;
    margin: 12px 0;
}
.rag-card {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 12px 14px;
    margin-bottom: 8px;
}
</style>
""", unsafe_allow_html=True)

# Target Port 9999
FLASK_API_URL = "http://127.0.0.1:9999"

# Check Backend Status
backend_online = False
backend_stats = {}
try:
    health_resp = requests.get(f"{FLASK_API_URL}/api/health", timeout=2)
    if health_resp.status_code == 200:
        backend_online = True
        backend_stats = health_resp.json()
except Exception:
    backend_online = False


# =========================================================================
# SIDEBAR: MULTIMODAL EQUIDERMA AI PANEL
# =========================================================================
with st.sidebar:
    st.markdown("### 🤖 Equiderma AI Panel")
    st.write("Real-time multimodal clinical diagnostic queries & tone analysis.")
    
    # Backend Status Badge
    if backend_online:
        st.success("🟢 Backend Connected (Port 9999)")
    else:
        st.error("🔴 Backend Offline (Port 9999)")
        st.caption("Start with: `python run_backend.py`")

    st.markdown("---")

    # Quick Test Case Presets
    st.markdown("##### ⚡ Quick Clinical Presets")
    col_p1, col_p2 = st.columns(2)
    preset_symptoms = ""
    preset_tone = "Auto-Detect from Image"
    
    if col_p1.button("🩹 Eczema (Dark)", use_container_width=True):
        st.session_state["symptoms_val"] = "Intense itching, dry thickened gray-brown hyperpigmented patches on inner elbows for 2 weeks."
        st.session_state["tone_val"] = "Type V (Dark Brown / Afro-Caribbean)"
    if col_p2.button("⚠️ Melanoma", use_container_width=True):
        st.session_state["symptoms_val"] = "New asymmetrical dark spot on leg, notched irregular border, multiple shades of black and brown, 7mm diameter."
        st.session_state["tone_val"] = "Type II (Fair, burns easily)"
        
    col_p3, col_p4 = st.columns(2)
    if col_p3.button("🔴 Shingles", use_container_width=True):
        st.session_state["symptoms_val"] = "Severe unilateral burning nerve pain with clustered fluid-filled blisters across right ribcage."
        st.session_state["tone_val"] = "Type III (Medium / Olive tone)"
    if col_p4.button("🔘 Ringworm", use_container_width=True):
        st.session_state["symptoms_val"] = "Circular itchy rash with elevated red scaling active border and clearing center on forearm."
        st.session_state["tone_val"] = "Type IV (Moderate Brown / South Asian)"

    # Initialize session state values if not present
    if "symptoms_val" not in st.session_state:
        st.session_state["symptoms_val"] = ""
    if "tone_val" not in st.session_state:
        st.session_state["tone_val"] = "Auto-Detect from Image"

    # Multimodal Image Input (NO OpenCV)
    st.markdown("##### 📷 Lesion Photograph (Multimodal)")
    img_mode = st.radio("Input Source", ["Upload Photo", "Webcam Capture"], horizontal=True)
    uploaded_image = None
    image_base64 = None

    if img_mode == "Upload Photo":
        uploaded_image = st.file_uploader("Select lesion image", type=["jpg", "jpeg", "png", "webp"])
    else:
        uploaded_image = st.camera_input("Capture lesion photo")

    if uploaded_image is not None:
        try:
            pil_img = Image.open(uploaded_image)
            st.image(pil_img, caption="Patient Lesion Preview", use_column_width=True)
            
            # Convert to base64 for Flask backend
            buf = io.BytesIO()
            fmt = pil_img.format if pil_img.format in ["JPEG", "PNG", "WEBP"] else "JPEG"
            if pil_img.mode != "RGB":
                pil_img = pil_img.convert("RGB")
            pil_img.save(buf, format=fmt)
            image_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        except Exception as e:
            st.error(f"Image load error: {e}")

    # Patient Symptoms Input
    st.markdown("##### 📝 Clinical Symptoms")
    ai_input = st.text_area(
        "Describe skin anomaly symptoms:",
        value=st.session_state["symptoms_val"],
        placeholder="e.g., Red itchy patch on arm spreading over 3 days with mild scaling...",
        height=100
    )

    # Fitzpatrick Phototype Palette
    st.markdown("##### 🎨 Fitzpatrick Phototype")
    phototypes = [
        "Auto-Detect from Image",
        "Type I (Very pale, always burns)",
        "Type II (Fair, light eyes/hair)",
        "Type III (Medium / Olive tone)",
        "Type IV (Moderate Brown / South Asian / Hispanic)",
        "Type V (Dark Brown / Afro-Caribbean)",
        "Type VI (Deeply Pigmented / Dark to Black)"
    ]
    current_tone_idx = 0
    if st.session_state["tone_val"] in phototypes:
        current_tone_idx = phototypes.index(st.session_state["tone_val"])
        
    selected_phototype = st.selectbox("Baseline Skin Tone", phototypes, index=current_tone_idx)
    skin_tone_hint = None if "Auto-Detect" in selected_phototype else selected_phototype.split(" (")[0]

    # Run Analysis Button
    run_button = st.button("🔬 Run Multimodal Analysis", type="primary", use_container_width=True)


# =========================================================================
# ACTION TRIGGER: EXECUTE ANALYSIS VIA FLASK ON PORT 9999
# =========================================================================
if run_button:
    if not ai_input.strip() and not image_base64:
        st.sidebar.warning("Please provide a symptom description or upload a lesion photograph.")
    elif not backend_online:
        st.sidebar.error("❌ Cannot reach backend! Please ensure your Flask server is running on Port 9999.")
    else:
        with st.spinner("🤖 Running Multimodal RAG & Local Ollama Reasoning Node..."):
            try:
                payload = {
                    "image": image_base64,
                    "symptoms": ai_input.strip(),
                    "skin_tone_hint": skin_tone_hint
                }
                
                res = requests.post(f"{FLASK_API_URL}/api/analyze", json=payload, timeout=40)
                
                if res.status_code == 200:
                    analysis_result = res.json()
                    st.session_state["active_result"] = analysis_result
                    st.sidebar.success("✅ Analysis Complete!")
                else:
                    st.sidebar.error(f"Backend Error: {res.status_code}")
            except Exception as e:
                st.sidebar.error(f"Connection Error: {e}")


# =========================================================================
# MAIN DASHBOARD SECTION
# =========================================================================
st.markdown("""
<div class="clinical-banner">
    <h1>🏥 Equiderma Clinical Advisor Dashboard</h1>
    <p>Multimodal Diagnostic Intelligence across Diverse Skin Tones • ChromaDB RAG Grounding • Melanin-Aware Risk Stratification</p>
</div>
""", unsafe_allow_html=True)


# --- SECTION 1: ACTIVE CLINICAL ANALYSIS DISPLAY ---
if "active_result" in st.session_state:
    res = st.session_state["active_result"]
    cond_name = res.get("condition_prediction", "Clinical Review Recommended")
    sev_level = res.get("severity_level", "Medium")
    conf = res.get("confidence_score", 0)
    latency = res.get("latency_ms", 0)
    engine_name = res.get("model_used", "Equiderma Clinical Engine")

    st.markdown("### 📋 Active Diagnostic Evaluation")
    
    # Metrics Row
    col_res1, col_res2, col_res3, col_res4 = st.columns([2, 1, 1, 1])
    with col_res1:
        st.markdown(f"#### {cond_name}")
        # Severity Badge
        sev_lower = str(sev_level).lower()
        if "high" in sev_lower:
            st.markdown('<div class="badge-high">🚨 HIGH SEVERITY (URGENT EVALUATION)</div>', unsafe_allow_html=True)
        elif "med" in sev_lower:
            st.markdown('<div class="badge-med">⚠️ MEDIUM SEVERITY (SEE PHYSICIAN)</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="badge-low">✅ LOW SEVERITY (ROUTINE / OTC)</div>', unsafe_allow_html=True)

    with col_res2:
        st.metric("Confidence Score", f"{conf}%")
        st.progress(max(0, min(100, conf)) / 100.0)

    with col_res3:
        st.metric("Inference Latency", f"{latency} ms")
        st.caption(f"Engine: `{engine_name}`")

    with col_res4:
        diffs = res.get("differential_diagnoses", [])
        st.write("**Differentials:**")
        st.write(", ".join(diffs[:3]) if diffs else "None")

    st.markdown("---")

    # Skin Tone & Morphology Columns
    col_tone, col_morph = st.columns(2)
    with col_tone:
        st.markdown("""
        <div class="tone-box">
            <h4 style="margin:0 0 6px 0; color:#102a43;">🎨 Skin Tone & Melanin Evaluation</h4>
        """, unsafe_allow_html=True)
        st.write(f"**Baseline:** {res.get('skin_tone_assessment', 'Assessed')}")
        st.write(f"{res.get('tone_specific_observations', '')}")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_morph:
        st.markdown("##### 🔍 Observed Lesion Morphology")
        st.write(res.get("visual_morphology", "Standard lesion evaluation."))
        st.markdown("##### 🩺 Clinical Summary")
        st.write(res.get("clinical_summary", ""))

    # Next Steps & Action Plan
    st.markdown("##### 📌 Recommended Clinical Action Plan")
    for step in res.get("recommended_next_steps", []):
        st.markdown(f"- {step}")

    # RAG Citations
    citations = res.get("rag_grounding_citations", [])
    if citations:
        with st.expander(f"📚 ChromaDB RAG Grounded Medical Literature ({len(citations)} Citations)", expanded=False):
            for c in citations:
                meta = c.get("metadata", {})
                st.markdown(f"""
                <div class="rag-card">
                    <strong>{meta.get('condition_name', 'Literature')}</strong> (Relevance: {c.get('relevance_score', 80)}% | Severity: {meta.get('severity', 'N/A')})<br>
                    <small>{c.get('document', '')}</small>
                </div>
                """, unsafe_allow_html=True)

    # Downloadable Consultation Report
    report_text = f"""# EQUIDERMA AI - CLINICAL CONSULTATION REPORT
Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## PATIENT PRESENTATION
- Symptoms: {ai_input if ai_input else 'Visual photo evaluation'}
- Skin Tone Baseline: {selected_phototype}

## DIAGNOSTIC OPINION
- Primary Suspected Condition: {cond_name}
- Severity Risk Stratification: {sev_level}
- Model Confidence Score: {conf}%
- Differential Diagnoses: {', '.join(diffs)}

## MELANIN & PHOTOTYPE CONSIDERATIONS
{res.get('tone_specific_observations', '')}

## VISUAL MORPHOLOGY
{res.get('visual_morphology', '')}

## RECOMMENDED CLINICAL TRIAGE
{chr(10).join(['- ' + s for s in res.get('recommended_next_steps', [])])}

## MEDICAL DISCLAIMER
{res.get('disclaimer', '')}
"""
    st.download_button(
        label="📥 Download Clinical Consultation Summary Report (.txt)",
        data=report_text,
        file_name=f"Equiderma_Report_{cond_name.replace(' ', '_')}.txt",
        mime="text/plain"
    )

    st.markdown("---")


# --- SECTION 2: DERMATOLOGY RECORDS & COMPARATIVE SKIN TONE EXPLORER ---
st.markdown("### 📖 Dermatology Clinical Records & Comparative Tone Explorer")
st.write("Browse curated medical records and examine how conditions exhibit distinct visual hallmarks across light vs. dark phototypes.")

col_s1, col_s2 = st.columns([3, 1])
with col_s1:
    search_query = st.text_input("Search records by condition name, symptoms, or category:", placeholder="e.g. Eczema, Shingles, Melanoma, Violaceous, Scale...")
with col_s2:
    severity_filter = st.selectbox("Severity Filter", ["All", "High", "Medium", "Low"])

# Fetch live records from backend or fallback to local knowledge
records = []
if backend_online:
    try:
        params = {}
        if search_query:
            params["q"] = search_query
        if severity_filter != "All":
            params["severity"] = severity_filter
        r = requests.get(f"{FLASK_API_URL}/api/conditions", params=params, timeout=3)
        if r.status_code == 200:
            records = r.json().get("conditions", [])
    except Exception:
        records = []

# If backend returned nothing or is offline, filter local DERMATOLOGY_KNOWLEDGE_BASE
if not records:
    records = DERMATOLOGY_KNOWLEDGE_BASE
    if search_query:
        sq = search_query.lower()
        records = [
            x for x in records 
            if sq in x["condition"].lower() or sq in x["symptoms"].lower() or sq in x["category"].lower()
        ]
    if severity_filter != "All":
        records = [x for x in records if x["severity"].lower() == severity_filter.lower()]

# Display Records Cards
if records:
    for item in records:
        sev = item["severity"]
        with st.expander(f"**{item['condition']}** — {sev} Severity ({item['category']})", expanded=False):
            # Badge
            if "high" in sev.lower():
                st.markdown('<div class="badge-high">🚨 HIGH SEVERITY</div>', unsafe_allow_html=True)
            elif "med" in sev.lower():
                st.markdown('<div class="badge-med">⚠️ MEDIUM SEVERITY</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="badge-low">✅ LOW SEVERITY</div>', unsafe_allow_html=True)

            st.write(f"**Core Symptoms:** {item['symptoms']}")
            st.write(f"**Visual Morphology:** {item['visual_morphology']}")
            
            # Side-by-side comparative phototype presentation
            c_light, c_dark = st.columns(2)
            with c_light:
                st.markdown("##### ☀️ Light Skin (Fitzpatrick I–III)")
                st.info(item["skin_tone_presentation"]["light_skin (Types I-III)"])
            with c_dark:
                st.markdown("##### 🌙 Melanin-Rich / Dark Skin (Fitzpatrick IV–VI)")
                st.warning(item["skin_tone_presentation"]["dark_skin (Types IV-VI)"])
                
            st.write(f"**Differentials:** {', '.join(item['differential_diagnoses'])}")
            st.write(f"**Clinical Management:** {item['clinical_management']}")
else:
    st.info("No dermatological records matched your search query.")
