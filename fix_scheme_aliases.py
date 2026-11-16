
import json
from pathlib import Path

path = Path("data/schemes.json")

ALIASES = {
    "PM_KISAN": [
        "PM-KISAN", "PM Kisan", "PMKISAN",
        "PM Kisan Samman Nidhi",
        "Pradhan Mantri Kisan Samman Nidhi",
        "पीएम-किसान", "पीएम किसान",
        "प्रधानमंत्री किसान सम्मान निधि"
    ],
    "AYUSHMAN_BHARAT_PMJAY": [
        "Ayushman Bharat", "Ayushman Bharat PM-JAY",
        "Ayushman Bharat PMJAY", "PM-JAY", "PMJAY",
        "AB PM-JAY", "AB-PMJAY",
        "आयुष्मान भारत", "आयुष्मान भारत योजना",
        "प्रधानमंत्री जन आरोग्य योजना",
        "पीएम जन आरोग्य योजना"
    ],
    "PMAY_URBAN": [
        "PMAY-U", "PMAY Urban", "PMAY Urban 2.0",
        "PM Awas Yojana Urban",
        "Pradhan Mantri Awas Yojana Urban",
        "प्रधानमंत्री आवास योजना शहरी",
        "प्रधानमंत्री आवास योजना-शहरी"
    ],
    "PMAY_GRAMIN": [
        "PMAY-G", "PMAY Gramin", "PMAY Rural",
        "PM Awas Yojana Gramin",
        "Pradhan Mantri Awaas Yojana Gramin",
        "प्रधानमंत्री आवास योजना ग्रामीण",
        "प्रधानमंत्री आवास योजना-ग्रामीण"
    ],
    "PMJDY": [
        "PMJDY", "Jan Dhan Yojana",
        "Pradhan Mantri Jan Dhan Yojana",
        "Jan Dhan", "जन धन योजना",
        "प्रधानमंत्री जन धन योजना",
        "पीएम जन धन योजना"
    ],
    "ATAL_PENSION_YOJANA": [
        "APY", "Atal Pension Yojana",
        "अटल पेंशन योजना", "एपीवाई"
    ],
    "PMJJBY": [
        "PMJJBY", "PM Jeevan Jyoti Bima Yojana",
        "Jeevan Jyoti Bima",
        "प्रधानमंत्री जीवन ज्योति बीमा योजना",
        "जीवन ज्योति बीमा योजना"
    ],
    "PMSBY": [
        "PMSBY", "PM Suraksha Bima Yojana",
        "Suraksha Bima",
        "प्रधानमंत्री सुरक्षा बीमा योजना",
        "सुरक्षा बीमा योजना"
    ],
    "PM_MUDRA": [
        "PMMY", "MUDRA", "MUDRA Yojana",
        "PM Mudra", "Mudra Loan",
        "Pradhan Mantri MUDRA Yojana",
        "प्रधानमंत्री मुद्रा योजना",
        "मुद्रा योजना", "पीएम मुद्रा योजना"
    ],
    "PM_UJJWALA": [
        "PMUY", "Ujjwala Yojana",
        "PM Ujjwala", "PM Ujjwala Yojana",
        "Pradhan Mantri Ujjwala Yojana",
        "प्रधानमंत्री उज्ज्वला योजना",
        "उज्ज्वला योजना", "पीएम उज्ज्वला योजना"
    ],
    "PMFBY": [
        "PMFBY", "PM Fasal Bima Yojana",
        "Fasal Bima", "Crop Insurance Scheme",
        "Pradhan Mantri Fasal Bima Yojana",
        "प्रधानमंत्री फसल बीमा योजना",
        "फसल बीमा योजना", "पीएम फसल बीमा योजना"
    ]
}

with path.open("r", encoding="utf-8-sig") as f:
    schemes = json.load(f)

found = {item["scheme_id"] for item in schemes}
missing = set(ALIASES) - found

if missing:
    raise ValueError(f"Missing scheme IDs in JSON: {sorted(missing)}")

backup = path.with_suffix(".json.bak")
backup.write_text(
    path.read_text(encoding="utf-8-sig"),
    encoding="utf-8"
)

for scheme in schemes:
    scheme_id = scheme["scheme_id"]
    existing = scheme.get("aliases", [])

    if isinstance(existing, str):
        existing = [existing]

    combined = existing + ALIASES.get(scheme_id, [])

    # Remove duplicates without changing original order.
    seen = set()
    clean = []

    for alias in combined:
        key = alias.casefold().strip()
        if key and key not in seen:
            seen.add(key)
            clean.append(alias.strip())

    scheme["aliases"] = clean

with path.open("w", encoding="utf-8") as f:
    json.dump(schemes, f, ensure_ascii=False, indent=2)
    f.write("\n")

print("SUCCESS: aliases updated for all 11 schemes")
print("Backup created:", backup)

for scheme in schemes:
    print(scheme["scheme_id"], "->", len(scheme["aliases"]), "aliases")
