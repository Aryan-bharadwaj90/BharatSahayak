
import json
import re
from pathlib import Path

import pymupdf

ROOT = Path(__file__).resolve().parent.parent
SCHEMES_FILE = ROOT / "data" / "schemes.json"
RAW_DIR = ROOT / "data" / "raw"
OUT_FILE = ROOT / "data" / "processed" / "chunks.json"

CHUNK_SIZE = 180
CHUNK_OVERLAP = 30


def clean_text(text):
    return re.sub(r"\s+", " ", str(text)).strip()


def format_value(value):
    """Convert strings, lists and dictionaries into readable text."""
    if value is None:
        return ""

    if isinstance(value, str):
        return clean_text(value)

    if isinstance(value, list):
        items = [format_value(item) for item in value]
        return "; ".join(item for item in items if item)

    if isinstance(value, dict):
        items = []
        for key, item in value.items():
            formatted = format_value(item)
            if formatted:
                items.append(f"{key}: {formatted}")
        return "; ".join(items)

    return str(value)


def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    words = text.split()

    if not words:
        return []

    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    chunks = []
    start = 0

    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunks.append(" ".join(words[start:end]))

        if end == len(words):
            break

        start = end - overlap

    return chunks


def read_schemes():
    if not SCHEMES_FILE.exists():
        return []

    with open(SCHEMES_FILE, encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("schemes.json must contain a JSON list")

    return data


# Each section is independently searchable.
SECTION_FIELDS = {
    "benefits": [
        "benefits",
        "benefit",
    ],
    "eligibility": [
        "eligibility",
        "eligibility_rules",
        "exclusions",
    ],
    "documents": [
        "documents",
        "required_documents",
    ],
    "application_process": [
        "application_process",
        "application_steps",
        "how_to_apply",
    ],
    "deadlines_and_amounts": [
        "important_deadlines_and_amounts",
        "important_deadlines",
        "deadlines",
        "important_dates",
        "key_dates",
        "application_deadline",
        "last_date",
        "amounts",
        "premium",
        "important_notes",
    ],
}


def extract_amounts_and_deadlines(scheme):
    """
    Extract existing amount and deadline statements from scheme data.
    Does not create or infer new scheme facts.
    """
    patterns = re.compile(
        r"₹|rs\.?\s*[\d,]+|\b\d[\d,]*\s*(?:rupees?|lakh|lakhs|crore|crores|%|percent|"
        r"days?|months?|years?|instalments?|installments?)\b|"
        r"\b(?:deadline|last date|due date|cut.?off|premium|interest rate|"
        r"application period|enrolment period|enrollment period|"
        r"from \d{1,2}\s+\w+|before \d{1,2}\s+\w+)\b",
        re.IGNORECASE,
    )

    results = []

    # Search only existing source fields.
    source_fields = [
    "important_deadlines_and_amounts",
    "important_deadlines",
    "deadlines",
    "important_dates",
    "application_deadline",
    "last_date",
    "premium",
    "important_notes",
    ]

    seen = set()

    for field in source_fields:
        value = scheme.get(field, [])

        if isinstance(value, str):
            value = [value]
        elif not isinstance(value, list):
            value = [format_value(value)]

        for item in value:
            statement = format_value(item)

            if statement and patterns.search(statement):
                normalized = statement.casefold()

                if normalized not in seen:
                    results.append(statement)
                    seen.add(normalized)

    return results



def create_structured_chunks(scheme):
    aliases = scheme.get("aliases", [])

    if isinstance(aliases, str):
        aliases = [aliases]

    aliases = [
        str(alias).strip()
        for alias in aliases
        if str(alias).strip()
    ]

    scheme_name = scheme.get("scheme_name", "")
    scheme_id = scheme.get("scheme_id", "")
    category = scheme.get("category", "")

    header_parts = [
        f"Scheme Name: {scheme_name}",
        f"Scheme ID: {scheme_id}",
        f"Category: {category}",
    ]

    if aliases:
        header_parts.append(
            "Alternative Names: " + "; ".join(aliases)
        )

    description = format_value(scheme.get("description", ""))

    if description:
        header_parts.append(f"Description: {description}")

    header = "\n".join(header_parts)

    chunks = []
    amount_deadline_items = extract_amounts_and_deadlines(scheme)
    for section_type, field_names in SECTION_FIELDS.items():

        section_parts = []

        for field_name in field_names:
            value = format_value(scheme.get(field_name))

            if value:
                section_parts.append(value)

        # Do not invent content for missing sections.
        if not section_parts:
            continue

        section_content = "\n".join(section_parts)

        section_text = (
            f"{header}\n"
            f"Information Section: {section_type}\n"
            f"{section_content}"
        )

        pieces = chunk_text(section_text)

        for piece_index, piece in enumerate(pieces):

            chunks.append({
                "text": piece,
                "scheme_id": scheme_id,
                "scheme_name": scheme_name,
                "category": category,
                "aliases": aliases,
                "section_type": section_type,
                "chunk_index": piece_index,
                "source_url": scheme.get("official_url", ""),
                "source_title": scheme.get(
                    "source_title",
                    "Official Scheme Information"
                ),
                "page_number": None,
            })
            if amount_deadline_items:
                    section_content = "\n".join(amount_deadline_items)

        section_text = (
            f"{header}\n"
            "Information Section: deadlines_and_amounts\n"
            f"{section_content}"
        )

        for piece_index, piece in enumerate(chunk_text(section_text)):
            chunks.append({
                "text": piece,
                "scheme_id": scheme_id,
                "scheme_name": scheme_name,
                "category": category,
                "aliases": aliases,
                "section_type": "deadlines_and_amounts",
                "chunk_index": piece_index,
                "source_url": scheme.get("official_url", ""),
                "source_title": scheme.get(
                    "source_title",
                    "Official Scheme Information"
                ),
                "page_number": None,
            })

    return chunks


def extract_pdf_text(pdf_path):
    pages = []

    try:
        with pymupdf.open(pdf_path) as document:
            for page_number, page in enumerate(document, start=1):
                text = clean_text(page.get_text("text"))

                if text:
                    pages.append({
                        "text": text,
                        "page_number": page_number,
                    })

    except Exception as exc:
        print(f"PDF processing error: {pdf_path} - {exc}")

    return pages


def process_documents(pdf_paths=None):
    schemes = read_schemes()
    all_chunks = []

    print("Processing structured scheme information...")

    for scheme in schemes:
        scheme_chunks = create_structured_chunks(scheme)
        all_chunks.extend(scheme_chunks)

        section_types = sorted({
            chunk["section_type"]
            for chunk in scheme_chunks
        })

        print(
            f"Processed: {scheme.get('scheme_name')} "
            f"({len(scheme_chunks)} chunks)"
        )
        print(f"  Sections found: {', '.join(section_types)}")

    print("\nProcessing PDF documents...")

    if pdf_paths is None:
        pdf_paths = (
            list(RAW_DIR.glob("*.pdf"))
            if RAW_DIR.exists()
            else []
        )

    for pdf_path in pdf_paths:
        pdf_path = Path(pdf_path)

        if not pdf_path.exists():
            print(f"File not found: {pdf_path}")
            continue

        for page in extract_pdf_text(pdf_path):
            for piece_index, piece in enumerate(
                chunk_text(page["text"])
            ):
                all_chunks.append({
                    "text": piece,
                    "scheme_id": "",
                    "scheme_name": pdf_path.stem,
                    "category": "",
                    "aliases": [],
                    "section_type": "official_pdf",
                    "chunk_index": piece_index,
                    "source_url": "",
                    "source_title": pdf_path.name,
                    "page_number": page["page_number"],
                })

        print(f"Processed PDF: {pdf_path.name}")

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(
            all_chunks,
            f,
            ensure_ascii=False,
            indent=2
        )

    print("\n========== PROCESSING COMPLETE ==========")
    print(f"Total schemes: {len(schemes)}")
    print(f"Total chunks: {len(all_chunks)}")
    print(f"Output file: {OUT_FILE}")

    return all_chunks


if __name__ == "__main__":
    chunks = process_documents()

    if chunks:
        print("\nSample chunk:")
        print(
            json.dumps(
                chunks[0],
                ensure_ascii=False,
                indent=2
            )
        )
