import json
import re
from io import BytesIO
from PIL import Image

SAFETY_SCHEMA = {
    "safety_score": 0,
    "overall_status": "Review Required",
    "ppe_detection": {
        "helmets": "Not clearly visible / requires on-site verification",
        "high_visibility_vests": "Not clearly visible / requires on-site verification",
        "steel_toe_boots": "Cannot reliably verify from image",
        "safety_harnesses": "Required where applicable; verify on site"
    },
    "hazards": []
}
CRACK_SCHEMA = {
    "defect_type": "Uncertain",
    "estimated_width_mm": "Not measurable from image alone",
    "root_causes": ["Image evidence is insufficient for a reliable diagnosis."],
    "recommended_repairs": ["Arrange an on-site inspection by a qualified structural engineer."],
    "urgency": "Inspection advised"
}

def _demo(mode):
    if mode == "safety":
        return {
            "safety_score": 72,
            "overall_status": "Review Required",
            "ppe_detection": {
                "helmets": "Check each worker; not all helmets can be confirmed from this sample.",
                "high_visibility_vests": "Verify high-visibility vests for all personnel in active work zones.",
                "steel_toe_boots": "Footwear certification cannot be confirmed visually; inspect PPE compliance.",
                "safety_harnesses": "Use and anchor fall protection for applicable work-at-height tasks."
            },
            "hazards": [
                {"hazard": "Unprotected work-at-height exposure", "severity": "High", "observation": "Potential fall exposure should be checked around edges and elevated work areas.", "remedy": "Install compliant guardrails or approved fall-arrest systems; verify anchor points and training."},
                {"hazard": "Material / housekeeping risk", "severity": "Medium", "observation": "Keep access and circulation routes clear of loose materials.", "remedy": "Establish housekeeping zones and remove trip hazards before work continues."}
            ],
            "disclaimer": "Demonstration output, not an analysis of the uploaded image."
        }
    return {
        "defect_type": "Hairline",
        "estimated_width_mm": "Uncertain — field measurement required",
        "root_causes": ["Possible drying shrinkage", "Possible thermal movement; not confirmable from image alone"],
        "recommended_repairs": ["Measure crack width and monitor for movement.", "Seal only after the cause and exposure requirements are assessed.", "Escalate active, widening, diagonal, or load-related cracks to a structural engineer."],
        "urgency": "Routine inspection unless movement, leakage, displacement, or structural symptoms are present",
        "disclaimer": "Demonstration output, not an analysis of the uploaded image."
    }

def _extract_json(text):
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end < start:
        raise ValueError("Model response did not contain JSON.")
    return json.loads(text[start:end+1])

def analyze_image(image, mode, api_key):
    if not api_key:
        return _demo(mode)
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        if mode == "safety":
            prompt = """Analyze this construction site photo for visible PPE and hazards. Return ONLY valid JSON with keys safety_score (integer 0-100), overall_status (Safe/Review Required/Unsafe), ppe_detection (object with helmets, high_visibility_vests, steel_toe_boots, safety_harnesses; each must state observed/not visible/uncertain), hazards (array of objects hazard, severity (Low/Medium/High/Critical), observation, remedy). Be conservative: do not claim boots or certification can be verified if not visible. Mention that OSHA/IS 456 applicability must be confirmed by local safety/engineering professionals. Never infer unseen conditions."""
        else:
            prompt = """Assess this concrete/wall image for preliminary defect triage. Return ONLY valid JSON with keys defect_type (one of Hairline, Settlement, Structural Shear, Thermal Expansion, Spalling, Uncertain), estimated_width_mm (number or string stating uncertain), root_causes (array), recommended_repairs (array, consider epoxy injection or structural re-grouting only if appropriate after engineer review), urgency (Low/Moderate/High/Urgent). Do not present image estimates as measurements; if scale is absent, say width cannot be reliably measured. Clearly state uncertainty."""
        bio = BytesIO()
        image.save(bio, format="JPEG")
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt, {"mime_type": "image/jpeg", "data": bio.getvalue()}],
            config={"response_mime_type": "application/json"}
        )
        return _extract_json(response.text)
    except Exception as exc:
        fallback = _demo(mode)
        fallback["ai_error"] = f"Gemini request failed; demonstration fallback used ({type(exc).__name__}). Check key, quota, and network."
        return fallback

def chat_response(query, history, api_key):
    if api_key:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            context = "\n".join(f"{m['role']}: {m['content']}" for m in history[-10:])
            prompt = ("You are a cautious construction site assistant. Provide practical general guidance, "
                      "call out assumptions, and defer structural design, code interpretation, and site-specific "
                      "decisions to qualified professionals. Never claim to inspect drawings not provided.\n\n"
                      f"Conversation:\n{context}\n\nAnswer the latest user question.")
            response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
            return response.text or "I couldn't generate a response. Please try again."
        except Exception:
            pass
    q = query.lower()
    if any(w in q for w in ["crack", "concrete", "spalling"]):
        return ("For a crack or concrete defect, record its location, length, width (using a crack gauge), "
                "orientation, moisture, and whether it is changing. Photograph it with a scale and monitor it. "
                "Do not choose epoxy injection or re-grouting until the cause and structural significance are assessed. "
                "Escalate widening, diagonal, displaced, leaking, or load-related cracks to a structural engineer. "
                "\n\n*Demo guidance; verify against approved drawings and local codes.*")
    if any(w in q for w in ["crane", "wind", "rain", "heat", "weather"]):
        return ("Follow the site-specific risk assessment, equipment manufacturer's limits, and approved method statement. "
                "Stop affected operations when thresholds are exceeded; secure loose materials, maintain access routes, "
                "and brief the team before restarting. For severe weather, follow the site's emergency procedure.")
    if any(w in q for w in ["ppe", "helmet", "harness", "safety"]):
        return ("Use a task-specific PPE assessment. Typical controls may include a properly fitted helmet, high-visibility "
                "clothing, suitable safety footwear, eye/hand protection, and fall protection where required. Inspect PPE "
                "before use and verify local regulatory requirements and site rules.")
    return ("Start with the approved drawings, specifications, method statement, and site risk assessment. Confirm the "
            "scope, materials, sequence, inspection hold points, and responsible engineer before acting. If you share "
            "the specific task and context, I can help create a general checklist. This demo assistant is not an engineer "
            "of record.")
