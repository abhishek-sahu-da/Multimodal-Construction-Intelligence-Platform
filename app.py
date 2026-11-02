import json
import os
from datetime import datetime
from io import BytesIO

import streamlit as st
from PIL import Image

st.set_page_config(page_title="Construction Intelligence Platform", page_icon="🏗️", layout="wide")

# ---------- Styling ----------
st.markdown("""
<style>
.block-container {padding-top: 1.4rem; padding-bottom: 2rem;}
.hero {padding: 1.2rem 1.4rem; border-radius: 16px; background: linear-gradient(120deg,#12233f,#2563a6); color: white;}
.hero h1 {color:white; margin-bottom:.3rem;}
.small-note {color:#667085;font-size:.9rem}
div[data-testid="stMetric"] {border:1px solid #e4e7ec;padding:12px;border-radius:12px;background:#fafbfc}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
<h1>🏗️ Multimodal Construction Intelligence Platform</h1>
<p>AI-assisted site safety, crack diagnostics, project budgeting, and weather-aware site guidance.</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Google Gemini API key (optional)", type="password",
                            help="Used only for image analysis. Leave blank to use clearly labelled demo mode.")
    st.caption("Your key is kept in this session and is not saved by this app.")
    st.divider()
    st.subheader("Architecture")
    st.write("Streamlit UI → analysis service → structured JSON report")
    st.write("Image input: JPG / PNG")
    st.write("Outputs: safety audit, crack diagnostics, budget estimates, advisory")
    st.info("Demo mode uses transparent heuristic examples. It is not a substitute for a qualified safety officer or structural engineer.")

def gemini_image_analysis(image, prompt, api_key):
    """Optional Gemini multimodal analysis; returns parsed JSON or raises a helpful error."""
    if not api_key:
        return None
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content([prompt, image])
        raw = response.text.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        start, end = raw.find("{"), raw.rfind("}")
        if start < 0 or end < start:
            raise ValueError("The model did not return a JSON object.")
        return json.loads(raw[start:end+1])
    except Exception as exc:
        st.warning(f"AI service unavailable; showing demo result instead. Details: {exc}")
        return None

def show_json_download(data, filename):
    payload = json.dumps(data, indent=2, ensure_ascii=False)
    st.download_button("⬇️ Download JSON report", payload, file_name=filename, mime="application/json")

def demo_safety_result():
    return {
        "safety_score": 82,
        "overall_status": "Review required",
        "ppe_detection": {
            "helmet": "Needs visual confirmation",
            "high_visibility_vest": "Needs visual confirmation",
            "steel_toe_boots": "Not reliably verifiable from many images",
            "safety_harness": "Required when working at height; verify on site"
        },
        "hazards": [
            {"hazard": "PPE visibility cannot be confirmed for every worker", "severity": "Medium",
             "remedy": "Conduct a close-range PPE check before work begins."},
            {"hazard": "Potential trip hazards around the work area", "severity": "Medium",
             "remedy": "Keep access routes clear and mark restricted zones."}
        ],
        "disclaimer": "Demonstration output only. Confirm findings with a qualified site safety officer."
    }

def demo_crack_result():
    return {
        "defect_type": "Hairline (provisional demo classification)",
        "estimated_crack_width_mm": None,
        "severity": "Requires on-site inspection",
        "possible_root_causes": ["Drying shrinkage", "Thermal movement", "Settlement (if accompanied by other signs)"],
        "recommended_action": [
            "Measure and photograph the crack with a scale.",
            "Record whether it is growing and check both sides of the wall if accessible.",
            "Ask a qualified structural engineer to assess wide, growing, diagonal, leaking, or load-bearing cracks."
        ],
        "disclaimer": "Image-only estimates cannot certify structural safety. Width is intentionally not fabricated in demo mode."
    }

def money_inr(value):
    if value >= 1e7:
        return f"₹{value/1e7:.2f} Cr"
    if value >= 1e5:
        return f"₹{value/1e5:.2f} L"
    return f"₹{value:,.0f}"

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🦺 Site Safety & PPE", "🧱 Crack Diagnostics", "📐 Planning & Valuation",
    "🌦️ Site Assistant", "📘 About & Validation"
])

with tab1:
    st.subheader("Site Safety & PPE Audit")
    st.write("Upload a construction-site photo to create a structured safety checklist.")
    safety_file = st.file_uploader("Construction site photo", type=["jpg", "jpeg", "png"], key="safety_img")
    if safety_file:
        img = Image.open(safety_file).convert("RGB")
        st.image(img, caption="Uploaded site photo", use_container_width=True)
        if st.button("Analyze safety photo", type="primary", key="safety_analyze"):
            prompt = """Analyze this construction site photo for visible PPE and safety hazards. Return ONLY valid JSON with keys:
safety_score (integer 0-100), overall_status (string), ppe_detection (object with helmet, high_visibility_vest, steel_toe_boots, safety_harness),
hazards (array of objects with hazard, severity [Low/Medium/High/Critical], remedy), limitations (array).
Do not claim unseen equipment is present. If an item cannot be verified, say so. This is preliminary decision support, not a certification."""
            result = gemini_image_analysis(img, prompt, api_key) or demo_safety_result()
            st.session_state["safety_result"] = result
    if "safety_result" in st.session_state:
        result = st.session_state["safety_result"]
        score = result.get("safety_score", "—")
        status = result.get("overall_status", "Review required")
        c1, c2 = st.columns(2)
        c1.metric("Safety score (AI/demo estimate)", f"{score}/100" if isinstance(score, (int,float)) else str(score))
        c2.metric("Overall status", str(status))
        st.markdown("#### PPE checklist")
        st.json(result.get("ppe_detection", {}))
        st.markdown("#### Identified hazards")
        hazards = result.get("hazards", [])
        if hazards:
            st.dataframe(hazards, use_container_width=True, hide_index=True)
        show_json_download(result, "site_safety_audit.json")
        st.warning("Do not use this result alone to approve work or determine legal compliance. Verify on site.")

with tab2:
    st.subheader("Crack Diagnostics & Structural Integrity")
    st.write("Upload a wall or concrete-surface photo for preliminary defect triage.")
    crack_file = st.file_uploader("Concrete / wall surface photo", type=["jpg", "jpeg", "png"], key="crack_img")
    if crack_file:
        crack_img = Image.open(crack_file).convert("RGB")
        st.image(crack_img, caption="Uploaded surface photo", use_container_width=True)
        if st.button("Analyze crack photo", type="primary", key="crack_analyze"):
            prompt = """Analyze this concrete/wall surface image for visible cracking. Return ONLY valid JSON with keys:
defect_type (one of Hairline, Settlement, Structural Shear, Thermal Expansion, Spalling, Unclear),
estimated_crack_width_mm (number or null; use null if image scale is insufficient), root_causes (array),
recommended_repairs (array), urgency (Low/Medium/High/Critical), limitations (array).
Never certify structural safety. Recommend professional assessment for significant, growing, diagonal, load-bearing, or water-ingress cracks."""
            result = gemini_image_analysis(crack_img, prompt, api_key) or demo_crack_result()
            st.session_state["crack_result"] = result
    if "crack_result" in st.session_state:
        result = st.session_state["crack_result"]
        st.metric("Preliminary defect classification", str(result.get("defect_type", "Unclear")))
        st.write("**Urgency:**", result.get("urgency", result.get("severity", "Requires inspection")))
        width = result.get("estimated_crack_width_mm")
        st.write("**Estimated crack width:**", f"{width} mm" if width is not None else "Not available — a scale/onsite measurement is needed.")
        st.write("**Possible causes**")
        st.write(result.get("root_causes", result.get("possible_root_causes", [])))
        st.write("**Recommended next steps / repairs**")
        st.write(result.get("recommended_repairs", result.get("recommended_action", [])))
        show_json_download(result, "crack_diagnostics.json")
        st.error("Image analysis cannot determine load-bearing capacity. Seek a structural engineer for concerning cracks.")

with tab3:
    st.subheader("Planning & Real Estate Valuation")
    left, right = st.columns(2)
    with left:
        structure = st.selectbox("Structure type", ["Residential", "Commercial", "Industrial", "Warehouse"])
        area = st.number_input("Built-up area (sq ft)", min_value=100, max_value=2_000_000, value=1500, step=100)
        tier = st.selectbox("Location tier", ["Tier 1", "Tier 2", "Tier 3"])
        completion = st.slider("Construction completion (%)", 0, 100, 35)
    with right:
        cost_rate = {"Residential": 2200, "Commercial": 3000, "Industrial": 1800, "Warehouse": 1400}[structure]
        tier_factor = {"Tier 1": 1.25, "Tier 2": 1.0, "Tier 3": 0.82}[tier]
        unit_cost = cost_rate * tier_factor
        budget = area * unit_cost
        incurred = budget * completion / 100
        market_rate = {"Tier 1": 6500, "Tier 2": 4200, "Tier 3": 2800}[tier]
        market_value = area * market_rate * (0.75 + completion/400)
        steel_kg = area * 4.0
        cement_bags = area * 0.4
        st.caption("Planning assumptions are illustrative estimates only. Replace rates with local BOQ/engineer estimates.")
        st.metric("Estimated total budget", money_inr(budget))
        st.metric("Estimated expenditure incurred", money_inr(incurred))
        st.metric("Indicative asset valuation", money_inr(market_value))
        st.metric("Indicative steel requirement", f"{steel_kg:,.0f} kg")
        st.metric("Indicative cement requirement", f"{cement_bags:,.0f} bags")
    st.progress(completion / 100, text=f"Milestone completion: {completion}%")
    valuation = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "structure_type": structure, "built_up_area_sqft": area, "location_tier": tier,
        "completion_percent": completion, "assumed_cost_per_sqft_inr": round(unit_cost, 2),
        "estimated_total_budget_inr": round(budget, 2), "estimated_cost_incurred_inr": round(incurred, 2),
        "indicative_market_asset_value_inr": round(market_value, 2),
        "indicative_steel_requirement_kg": round(steel_kg, 2),
        "indicative_cement_requirement_bags": round(cement_bags, 2),
        "assumptions": "Illustrative demo rates; not a quote, valuation certificate, or engineering BOQ."
    }
    show_json_download(valuation, "planning_valuation.json")

with tab4:
    st.subheader("Daily Site Assistant & Weather-Aware Advisory")
    weather = st.selectbox("Current / forecast condition", ["Normal", "High Wind", "Heavy Rain", "Extreme Heat"])
    advice = {
        "Normal": ["Continue only under approved method statements and site risk assessment.", "Maintain housekeeping and routine PPE checks."],
        "High Wind": ["Pause crane and lifting operations when wind exceeds equipment/site limits.", "Secure loose materials and review work-at-height controls."],
        "Heavy Rain": ["Inspect drainage, excavations, access routes, and electrical equipment.", "Stop work in unsafe conditions; protect fresh concrete and follow engineer-approved curing guidance."],
        "Extreme Heat": ["Provide water, shade, rest breaks, and heat-stress monitoring.", "Schedule strenuous work for cooler periods and follow the site's heat plan."]
    }
    st.info(f"Weather advisory: {weather}")
    for item in advice[weather]:
        st.write("• " + item)
    st.divider()
    st.markdown("#### Ask the site assistant")
    question = st.text_input("Question", placeholder="e.g., What should we check before concrete pouring?")
    if st.button("Get guidance", key="chat_submit"):
        q = question.lower()
        if any(w in q for w in ["concrete", "pour", "curing"]):
            answer = "Before pouring, verify approved drawings and mix design, formwork stability, reinforcement cover, embedded services, access, weather, inspection sign-off, and concrete delivery records. Follow the project engineer's method statement."
        elif any(w in q for w in ["crack", "wall", "structural"]):
            answer = "Photograph and measure the crack, record location and change over time, and restrict the area if there are signs of instability. A qualified structural engineer must assess significant or growing cracks."
        elif any(w in q for w in ["helmet", "ppe", "safety"]):
            answer = "Check task-specific PPE, fit and condition, site access controls, fall protection, housekeeping, and permit requirements. Escalate imminent hazards and follow the approved site safety plan."
        elif any(w in q for w in ["rain", "wind", "heat", "weather"]):
            answer = "Use the selected weather advisory above alongside the official site forecast and equipment operating limits. The site supervisor should decide whether work must stop."
        else:
            answer = "Use the approved drawings, method statement, risk assessment, and local regulations. Escalate engineering, structural, or imminent safety concerns to the qualified site lead. This assistant provides general guidance only."
        st.markdown("**Guidance**")
        st.write(answer)
    st.caption("This is a rule-based demonstration assistant; it does not replace project-specific engineering instructions.")

with tab5:
    st.subheader("Project overview & validation")
    st.markdown("""
**Capstone alignment**
- Site Safety & PPE Audit: construction photo upload, structured JSON, score, PPE checklist, hazards and remedies.
- Crack Diagnostics: defect classification, width only when supportable, possible causes, repair/urgency guidance.
- Planning & Real Estate Valuation: structure, area, city tier, completion %, INR budget/valuation, steel/cement indicators.
- Site Assistant: weather-aware alerts and multi-turn-style guidance.
- JSON contracts: each major analysis can be downloaded as JSON.
- Deployment: Streamlit Community Cloud compatible; no external database required.

**Important limitations**
- Gemini vision analysis is optional and requires a valid API key plus the `google-generativeai` package.
- Without a key, the app runs in demo mode and labels the outputs accordingly.
- Budget, valuation, steel and cement quantities are simplified planning estimates, not professional estimates.
- PPE/crack image results are not legal compliance determinations or structural certifications.
""")
    st.markdown("**Suggested validation checklist**")
    st.checkbox("Test safety tab with JPG and PNG images")
    st.checkbox("Test crack tab with a clear surface image and an unclear image")
    st.checkbox("Check Tier 1/2/3 and completion slider calculations")
    st.checkbox("Download and validate each JSON output")
    st.checkbox("Deploy and test the public HTTPS URL")
