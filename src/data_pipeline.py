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
    return re.sub(r"\s+", " ", text).strip()


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


def create_structured_chunks(scheme):
    aliases = scheme.get("aliases", [])
    if isinstance(aliases, str):
        aliases = [aliases]
    aliases = [str(a).strip() for a in aliases if str(a).strip()]

    header_parts = [
        f"Scheme Name: {scheme.get('scheme_name', '')}",
        f"Scheme ID: {scheme.get('scheme_id', '')}",
        f"Category: {scheme.get('category', '')}",
    ]
    if aliases:
        header_parts.append("Alternative Names: " + "; ".join(aliases))

    body_parts = [f"Description: {scheme.get('description', '')}"]
    for label, key in [
        ("Benefits", "benefits"),
        ("Eligibility", "eligibility"),
        ("Required Documents", "documents"),
        ("Application Process", "application_process"),
    ]:
        value = scheme.get(key, "")
        if isinstance(value, list):
            value = "; ".join(str(item) for item in value)
        elif value is not None:
            value = str(value)
        if value:
            body_parts.append(f"{label}: {value}")

    header = "\n".join(header_parts)
    body = "\n".join(body_parts)
    pieces = chunk_text(body) or [body]

    chunks = []
    for piece in pieces:
        chunks.append({
            # Repeat scheme identity in every chunk so every vector retains context.
            "text": f"{header}\n{piece}",
            "scheme_id": scheme.get("scheme_id", ""),
            "scheme_name": scheme.get("scheme_name", ""),
            "category": scheme.get("category", ""),
            "aliases": aliases,
            "source_url": scheme.get("official_url", ""),
            "source_title": scheme.get("source_title", "Official Scheme Information"),
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
                    pages.append({"text": text, "page_number": page_number})
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
        print(f"Processed: {scheme.get('scheme_name')} ({len(scheme_chunks)} chunks)")

    print("\nProcessing PDF documents...")
    if pdf_paths is None:
        pdf_paths = list(RAW_DIR.glob("*.pdf")) if RAW_DIR.exists() else []

    for pdf_path in pdf_paths:
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            print(f"File not found: {pdf_path}")
            continue

        for page in extract_pdf_text(pdf_path):
            for piece in chunk_text(page["text"]):
                all_chunks.append({
                    "text": piece,
                    "scheme_id": "",
                    "scheme_name": pdf_path.stem,
                    "category": "",
                    "aliases": [],
                    "source_url": "",
                    "source_title": pdf_path.name,
                    "page_number": page["page_number"],
                })
        print(f"Processed PDF: {pdf_path.name}")

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=2)

    print("\n========== PROCESSING COMPLETE ==========")
    print(f"Total schemes: {len(schemes)}")
    print(f"Total chunks: {len(all_chunks)}")
    print(f"Output file: {OUT_FILE}")
    return all_chunks


if __name__ == "__main__":
    chunks = process_documents()
    if chunks:
        print("\nSample chunk:")
        print(json.dumps(chunks[0], ensure_ascii=False, indent=2))
