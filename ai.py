import os
import json
import fitz
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.environ["GROQ_API_KEY"])

MERAPATH_PROFILE = {
    "company": "MeraPath Education Limited",
    "established": 2004,
    "certifications": ["ISO 9001", "ISO 14001", "ISO 45001", "ISO 21001", "ISO 22000", "MSME registered", "DPIIT", "EPF", "ESIC", "GST", "FSSAI"],
    "presence": "14+ states, 100+ districts, 500+ blocks, 3000+ panchayats",
    "total_beneficiaries": "4.2 lakh+",
    "nsdc_empanelled": True,
    "flagship_projects": [
        "PMGDISHA — 1,59,547 beneficiaries",
        "Jal Jeevan Mission — 1,34,627 trainees",
        "PMAY-G Rural Mason Training — 26,720 trainees",
        "NDLM — 41,873 beneficiaries",
        "Lakhpati Didi — 65,186 beneficiaries across 75 districts",
        "Saubhagya — 1,500 technicians trained"
    ],
    "specialisations": [
        "Skill development and vocational training",
        "Digital literacy programs",
        "Capacity building for government schemes",
        "Rural and grassroots delivery",
        "Call center and BPO training",
        "Toolkit-based livelihood solutions",
        "AI and digital training"
    ]
}

MATCH_CRITERIA = [
    {"key": "pmgdisha", "label": "PMGDISHA Experience", "detail": "1,59,547 beneficiaries"},
    {"key": "jjm", "label": "Jal Jeevan Mission", "detail": "1,34,627 trainees"},
    {"key": "lakhpati", "label": "Lakhpati Didi Experience", "detail": "65,186 beneficiaries"},
    {"key": "ndlm", "label": "NDLM Experience", "detail": "41,873 beneficiaries"},
    {"key": "pmay", "label": "PMAY-G Experience", "detail": "26,720 trainees"},
    {"key": "iso", "label": "ISO Certifications", "detail": "ISO 9001, 14001, 45001, 21001, 22000"},
    {"key": "msme", "label": "MSME Status", "detail": "MSME registered"},
    {"key": "geographic", "label": "Geographic Reach", "detail": "14+ states, 3000+ panchayats"},
    {"key": "scale", "label": "Beneficiary Scale", "detail": "4.2 lakh+ trained"},
]

GROQ_MODEL = "llama-3.3-70b-versatile"


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages = [page.get_text() for page in doc]
    doc.close()
    return "".join(pages)


def _call_groq(prompt: str) -> str:
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        max_tokens=2500,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "You are a precise document analysis assistant. Always respond with valid JSON only — no markdown, no explanation, no code fences. Never omit any field requested in the schema, even if the answer requires inference."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()


def analyse_tender(pdf_bytes: bytes) -> dict:
    raw_text = extract_text_from_pdf(pdf_bytes)

    # Groq free tier for 70b-versatile has a hard limit of 12,000 Tokens Per Minute.
    # To safely stay under this, we must limit the text to ~35,000 characters.
    MAX_CHARS = 35000
    if len(raw_text) > MAX_CHARS:
        # For huge documents (e.g. 300+ pages), keep the beginning and the end.
        # The middle is usually generic boilerplate terms & conditions.
        half = MAX_CHARS // 2
        text_to_send = raw_text[:half] + "\n\n... [MIDDLE CONTENT OMITTED FOR LENGTH] ...\n\n" + raw_text[-half:]
    else:
        text_to_send = raw_text

    prompt = f"""You are a senior bid analyst for MeraPath Education Limited.

MeraPath Profile:
- Established: {MERAPATH_PROFILE['established']} (20+ years)
- Certifications: {', '.join(MERAPATH_PROFILE['certifications'])}
- Pan-India presence: {MERAPATH_PROFILE['presence']}
- Total beneficiaries trained: {MERAPATH_PROFILE['total_beneficiaries']}
- NSDC empanelled: Yes
- Major projects: {', '.join(MERAPATH_PROFILE['flagship_projects'])}
- Specialisations: {', '.join(MERAPATH_PROFILE['specialisations'])}

Analyse this tender document and return ONLY valid JSON. No markdown, no explanation.

CRITICAL INSTRUCTION FOR MATCH ENGINE: 
For the `match_engine` object, output `true` if MeraPath's profile meets the tender's requirement OR if the tender does NOT require that specific criteria. Output `false` ONLY if the tender explicitly requires that experience/certification and MeraPath does not meet it.

TENDER TEXT:
{text_to_send}

Return this exact JSON structure:
{{
  "bid_number": "tender/bid reference number or empty string",
  "ra_option": "Yes or No — whether reverse auction is mentioned",
  "start_date": "tender start date or empty string",
  "end_date": "submission deadline with time or empty string",
  "department_name": "full department name and address",
  "estimated_cost": "tender value in rupees",
  "epbg": "earnest money deposit / performance bank guarantee amount or empty string",
  "processing_fee": "processing fee amount or Not mentioned",
  "tender_fee": "tender document fee or Not mentioned",
  "appraisal_fee": "appraisal fee or Not mentioned",
  "project_name": "name of the project or scheme",
  "scope_of_work": ["point 1", "point 2", "point 3"],
  "eligibility_criteria": ["criterion 1", "criterion 2", "criterion 3"],
  "documents_required": ["document 1", "document 2", "document 3"],
  "remarks_risk": ["risk or remark 1", "risk or remark 2"],
  "jist": "One paragraph plain English summary of what this tender wants — who is issuing it, what they need, how big it is, and when it closes.",
  "state": "Indian state where work will be done",
  "region": "district or region if mentioned",
  "category": "one of: skill_development, digital_literacy, agriculture, healthcare, infrastructure, corporate_training, ai_training, other",
  "portal": "GeM or CPPP or State Portal or NSDC or other",
  "match_engine": {{
    "pmgdisha": true or false,
    "jjm": true or false,
    "lakhpati": true or false,
    "ndlm": true or false,
    "pmay": true or false,
    "iso": true or false,
    "msme": true or false,
    "geographic": true or false,
    "scale": true or false
  }},
  "bid_strength_score": "number between 0 and 100",
  "win_probability": "number between 0 and 100",
  "score_reasoning": "2-3 sentences explaining the score",
  "proposal_sections": ["Section 1: title", "Section 2: title", "Section 3: title", "Section 4: title", "Section 5: title"]
}}"""

    raw = _call_groq(prompt)
    return json.loads(raw)


def fix_eligibility_gaps(tender_data: dict) -> dict:
    """
    For every criterion that did not match,
    AI explains why the gap exists and suggests exactly how to address it.
    """
    match = tender_data.get("match_engine", {})
    eligibility = tender_data.get("eligibility_criteria", [])
    project_name = tender_data.get("project_name", "")
    department = tender_data.get("department_name", "")

    gaps = {k: v for k, v in match.items() if not v}

    if not gaps:
        return {"gaps": [], "message": "No gaps found — all criteria matched."}

    gap_labels = {
        "pmgdisha":  "PMGDISHA Experience",
        "jjm":       "Jal Jeevan Mission Experience",
        "lakhpati":  "Lakhpati Didi Experience",
        "ndlm":      "NDLM Experience",
        "pmay":      "PMAY-G Experience",
        "iso":       "ISO Certifications",
        "msme":      "MSME Status",
        "geographic":"Geographic Reach",
        "scale":     "Beneficiary Scale",
    }

    gaps_text = "\n".join([f"- {k}: {gap_labels.get(k, k)}" for k in gaps.keys()])

    prompt = f"""You are a senior bid consultant helping an organisation win a government tender.

Organisation profile:
- Established: 2004 (20+ years experience)
- ISO certified: 9001, 14001, 45001, 21001, 22000
- MSME registered, DPIIT, EPF, ESIC, GST compliant
- Pan-India presence: 14+ states, 100+ districts, 500+ blocks, 3000+ panchayats
- Total beneficiaries trained: 4.2 lakh+
- NSDC empanelled
- Major projects: PMGDISHA (1.59L), JJM (1.34L), PMAY-G (26K), NDLM (41K), Lakhpati Didi (65K), Saubhagya (1.5K)
- Specialisations: Skill development, digital literacy, rural delivery, corporate training, AI training

Tender: {project_name}
Department: {department}
Tender eligibility criteria: {', '.join(eligibility)}

The following criteria were NOT directly matched in our profile:
{gaps_text}

CRITICAL INSTRUCTION: For EACH gap, you MUST include all seven fields below. Do not skip "why_gap_exists" under any circumstances — it is the most important field. If you are unsure, write at least one honest sentence about why the organisation's profile does not directly cover this criterion.

For EACH gap, return an object with EXACTLY these seven fields, in this order:
1. criterion — REQUIRED. The key name of the gap (e.g. "jjm", "pmgdisha", "lakhpati", etc. as provided in the list).
2. gap_label — REQUIRED. The description of the gap (e.g. "Jal Jeevan Mission Experience").
3. why_gap_exists — REQUIRED. One or two sentences explaining specifically why the organisation does not directly meet this criterion. Never leave this blank or omit it.
4. what_to_write
5. documents_to_reference
6. framing_strategy
7. risk_level

Return ONLY valid JSON in this exact structure, no markdown, no explanation:

{{
  "gaps": [
    {{
      "criterion": "string",
      "gap_label": "string",
      "why_gap_exists": "string — never empty",
      "what_to_write": "string",
      "documents_to_reference": ["string"],
      "framing_strategy": "string",
      "risk_level": "low or medium or high"
    }}
  ]
}}"""

    raw = _call_groq(prompt)
    result = json.loads(raw)

    # Safety net — guarantee why_gap_exists is never blank in the UI,
    # even if the model omits it
    for gap in result.get("gaps", []):
        if not gap.get("why_gap_exists"):
            gap["why_gap_exists"] = (
                f"Our organisation's documented project portfolio does not include "
                f"direct experience matching '{gap.get('gap_label', 'this criterion')}'."
            )

    return result