# Multimodal Construction Intelligence Platform
**Skill Wallet Capstone — Project 1**

A Streamlit application with four modules:
1. Site Safety & PPE Audit
2. Crack Diagnostics & Structural Integrity
3. Planning & Real Estate Valuation
4. Daily Site Assistant & Weather-Aware Advisory

## Run locally
```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Open the local URL printed by Streamlit. No database is required. Without a Gemini key, image analysis uses a clearly labelled demonstration response. With a key, the app attempts Gemini multimodal analysis and falls back gracefully if the call fails.

## Deploy to Streamlit Community Cloud
1. Push this folder to a GitHub repository.
2. In Streamlit Community Cloud, create an app using `app.py` as the entry point.
3. Ensure `requirements.txt` is in the repository root.
4. Enter your Google Gemini API key in the app sidebar when needed. Do not commit secrets to GitHub.

## Important safety / engineering note
This is a capstone prototype, not a certified inspection system. Image-only PPE checks can miss people and cannot verify footwear certification. Crack widths cannot be measured reliably without scale and field measurement. The budget, market valuation, steel, and cement outputs use simplified assumptions and are not a quantity survey, bill of quantities, registered valuation, or structural design. OSHA and IS 456 applicability and all corrective actions must be confirmed by qualified professionals against current local rules and project documents.

## Project structure
```text
app.py
modules/
  __init__.py
  ai_engine.py
  calculations.py
  ui.py
requirements.txt
README.md
.streamlit/config.toml
```
