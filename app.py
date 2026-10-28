import json
import streamlit as st
from PIL import Image
from modules.ai_engine import analyze_image, chat_response
from modules.calculations import estimate_project
from modules.ui import inject_css, status_badge, metric_card

st.set_page_config(page_title="Multimodal Construction Intelligence", page_icon="🏗️", layout="wide")
inject_css()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

with st.sidebar:
    st.markdown("## 🏗️ Construction Intelligence")
    st.caption("Skill Wallet Capstone · Project 1")
    api_key = st.text_input("Google Gemini API key", type="password", help="Optional. Leave blank to use deterministic demonstration mode.")
    if api_key:
        st.success("API key entered · AI mode enabled")
    else:
        st.info("Demo mode · no API key required")
    st.markdown("---")
    st.markdown("### Architecture")
    st.markdown("**Streamlit UI** → **AI service** → **Structured JSON**")
    st.markdown("- Vision analysis: Gemini multimodal")
    st.markdown("- Calculations: local Python")
    st.markdown("- Storage: session state only")
    st.markdown("- Deployment: Streamlit Community Cloud")
    st.markdown("---")
    st.caption("Engineering decisions must be verified by a qualified professional. AI outputs are advisory only.")

st.title("Multimodal Construction Intelligence Platform")
st.markdown("A unified workspace for site safety, defect triage, project estimation, and weather-aware site guidance.")
tabs = st.tabs(["🦺 Site Safety & PPE Audit", "🧱 Crack Diagnostics", "📐 Planning & Valuation", "🌦️ Daily Site Assistant"])

with tabs[0]:
    st.subheader("Site Safety & PPE Audit")
    st.write("Upload a site photo to review visible PPE and potential hazards.")
    safety_image = st.file_uploader("Construction site photo", type=["jpg", "jpeg", "png"], key="safety")
    if safety_image:
        img = Image.open(safety_image).convert("RGB")
        st.image(img, caption="Uploaded construction site photo", use_container_width=True)
        if st.button("Run PPE & hazard audit", type="primary", key="run_safety"):
            with st.spinner("Reviewing visible safety conditions..."):
                result = analyze_image(img, "safety", api_key)
            st.session_state.safety_result = result
    result = st.session_state.get("safety_result")
    if result:
        st.markdown("### Audit result")
        c1, c2, c3 = st.columns(3)
        metric_card(c1, "Safety score", f"{result.get('safety_score', 0)}/100")
        metric_card(c2, "Overall status", result.get("overall_status", "Review"))
        metric_card(c3, "Hazards identified", str(len(result.get("hazards", []))))
        status_badge(result.get("overall_status", "Review"))
        st.markdown("#### PPE checklist")
        ppe = result.get("ppe_detection", {})
        if isinstance(ppe, dict):
            for item, detail in ppe.items():
                st.write(f"**{item.replace('_',' ').title()}**: {detail}")
        else:
            st.write(ppe)
        st.markdown("#### Hazards & corrective actions")
        hazards = result.get("hazards", [])
        if hazards:
            for h in hazards:
                with st.expander(f"{h.get('hazard','Potential hazard')} · {h.get('severity','Unknown')}"):
                    st.write(h.get("observation", "No additional detail supplied."))
                    st.write("**Corrective remedy:**", h.get("remedy", "Review on site."))
        else:
            st.info("No specific hazards were returned. This is not proof that the site is hazard-free.")
        st.download_button("Download safety report (JSON)", json.dumps(result, indent=2), "site_safety_report.json", "application/json")

with tabs[1]:
    st.subheader("Crack Diagnostics & Structural Integrity")
    st.write("Upload a concrete or wall surface image for preliminary defect triage.")
    crack_image = st.file_uploader("Concrete / wall image", type=["jpg", "jpeg", "png"], key="crack")
    if crack_image:
        crack_img = Image.open(crack_image).convert("RGB")
        st.image(crack_img, caption="Uploaded surface image", use_container_width=True)
        if st.button("Analyze surface defect", type="primary", key="run_crack"):
            with st.spinner("Assessing visible surface features..."):
                st.session_state.crack_result = analyze_image(crack_img, "crack", api_key)
    crack = st.session_state.get("crack_result")
    if crack:
        st.markdown("### Diagnostic summary")
        a, b, c = st.columns(3)
        metric_card(a, "Defect class", crack.get("defect_type", "Uncertain"))
        metric_card(b, "Estimated width", f"{crack.get('estimated_width_mm', 'N/A')} mm")
        metric_card(c, "Urgency", crack.get("urgency", "Inspection advised"))
        st.write("**Possible root causes**")
        for cause in crack.get("root_causes", []):
            st.write(f"- {cause}")
        st.write("**Recommended next steps**")
        for repair in crack.get("recommended_repairs", []):
            st.write(f"- {repair}")
        st.warning("Image-only crack-width estimates are not measurements. Confirm with a crack gauge and an on-site structural engineer.")
        st.download_button("Download diagnostic report (JSON)", json.dumps(crack, indent=2), "crack_diagnostic_report.json", "application/json")

with tabs[2]:
    st.subheader("Planning & Real Estate Valuation")
    left, right = st.columns([1, 1])
    with left:
        structure = st.selectbox("Structure type", ["Residential", "Commercial", "Industrial", "Institutional"])
        sqft = st.number_input("Built-up area (sq ft)", min_value=100, max_value=2_000_000, value=1800, step=100)
        tier = st.selectbox("Location tier", ["Tier 1", "Tier 2", "Tier 3"])
        completion = st.slider("Construction completion", 0, 100, 35, 5)
        custom_rate = st.number_input("Base construction rate (₹ / sq ft)", min_value=800, max_value=12000, value=2200, step=100)
    estimates = estimate_project(structure, sqft, tier, completion, custom_rate)
    with right:
        st.markdown("### Estimated project snapshot")
        metric_card(st, "Estimated project budget", f"₹{estimates['budget_lakhs']:,.2f} lakh")
        metric_card(st, "Capital expenditure incurred", f"₹{estimates['spent_lakhs']:,.2f} lakh")
        metric_card(st, "Indicative market asset value", estimates["market_value_display"])
        st.progress(completion / 100, text=f"Milestone progress · {completion}% complete")
        x, y = st.columns(2)
        metric_card(x, "Estimated steel", f"{estimates['steel_tonnes']:,.2f} tonnes")
        metric_card(y, "Estimated cement", f"{estimates['cement_bags']:,} bags")
        st.caption("Quantity factors and valuation multipliers are planning assumptions, not a bill of quantities or formal valuation.")
    st.markdown("### Conceptual 3D visualization prompt")
    prompt = f"Photorealistic conceptual architectural visualization of a {structure.lower()} building, {sqft:,} square feet built-up area, located in an Indian {tier.lower()} city, construction progress {completion}%, realistic materials, daylight, professional architectural render, no text, wide angle."
    st.text_area("Prompt for an image generator", value=prompt, height=95)
    st.markdown("[Open Pollinations AI image generator](https://image.pollinations.ai/)")
    st.download_button("Download estimate (JSON)", json.dumps(estimates, indent=2), "project_estimate.json", "application/json")

with tabs[3]:
    st.subheader("Daily Site Assistant & Weather-Aware Advisory")
    weather = st.selectbox("Current / forecast condition", ["Normal", "High Wind", "Heavy Rain", "Extreme Heat"])
    alerts = {
        "Normal": [("Routine operations", "Continue work under the approved method statement; inspect PPE, access routes, and housekeeping at shift start.")],
        "High Wind": [("Crane and lifting operations", "Pause lifts when wind exceeds equipment/manufacturer or lift-plan limits. Secure loose materials and re-check scaffolds."), ("Working at height", "Review wind exposure and suspend unsafe elevated work.")],
        "Heavy Rain": [("Electrical safety", "Isolate exposed electrical equipment where safe, protect temporary power, and use RCD/GFCI protection."), ("Concrete & excavation", "Protect fresh concrete from washout; inspect excavations, slopes, access routes, and water accumulation before re-entry.")],
        "Extreme Heat": [("Heat stress", "Provide shade, drinking water, rest breaks, acclimatization, and buddy monitoring; stop work for symptoms."), ("Concrete curing", "Follow the approved curing method and mix requirements; prevent rapid moisture loss and monitor placement conditions.")]
    }
    for title, body in alerts[weather]:
        st.warning(f"**{title}:** {body}" if weather != "Normal" else f"**{title}:** {body}")
    st.markdown("---")
    st.markdown("### Construction engineering assistant")
    st.caption("Ask about construction sequencing, materials, site safety, or general troubleshooting. Do not use this chatbot as a substitute for approved drawings or engineering sign-off.")
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    user_query = st.chat_input("Ask a construction question...")
    if user_query:
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)
        answer = chat_response(user_query, st.session_state.chat_history, api_key)
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        with st.chat_message("assistant"):
            st.markdown(answer)
    if st.button("Clear chat history"):
        st.session_state.chat_history = []
        st.rerun()
