
import json
from pathlib import Path

import faiss
import numpy as np

from src.embeddings import embed_documents, embed_query

ROOT = Path(__file__).resolve().parent.parent
CHUNKS_FILE = ROOT / "data" / "processed" / "chunks.json"
INDEX_FILE = ROOT / "data" / "processed" / "schemes.faiss"
META_FILE = ROOT / "data" / "processed" / "index_metadata.json"

_index = None
_metadata = None


def build_index(chunks):
    """Create and save a FAISS inner-product index."""
    global _index, _metadata

    if not chunks:
        raise ValueError("No chunks supplied. Run process_documents() first.")

    texts = [item["text"] for item in chunks]
    vectors = np.asarray(embed_documents(texts), dtype="float32")

    if vectors.ndim != 2 or vectors.shape[0] != len(chunks):
        raise ValueError("Embedding output shape does not match chunk count.")

    faiss.normalize_L2(vectors)

    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)

    INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(INDEX_FILE))

    with open(META_FILE, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

    _index, _metadata = index, chunks
    return index


def load_index():
    """Load FAISS index and matching metadata."""
    global _index, _metadata

    if not INDEX_FILE.exists() or not META_FILE.exists():
        raise FileNotFoundError(
            "FAISS index or metadata missing. Build the index first."
        )

    index = faiss.read_index(str(INDEX_FILE))

    with open(META_FILE, encoding="utf-8") as f:
        metadata = json.load(f)

    if index.ntotal != len(metadata):
        raise ValueError("Index and metadata counts do not match.")

    _index, _metadata = index, metadata
    return _index


def _normalise(value):
    return " ".join(str(value or "").casefold().strip().split())


def _contains_phrase(query, phrase):
    """Match an alias or keyword as a phrase."""
    query = _normalise(query)
    phrase = _normalise(phrase)

    if not query or not phrase:
        return False

    # English matching with word boundaries.
    if phrase.isascii():
        import re
        return bool(
            re.search(
                r"(?<!\w)" + re.escape(phrase) + r"(?!\w)",
                query
            )
        )

    # Hindi / Unicode phrase matching.
    return phrase in query


def _detect_scheme(query):
    """Detect an explicitly named scheme using its aliases and ID."""

    matches = set()

    for item in _metadata:
        scheme_id = item.get("scheme_id")

        if not scheme_id:
            continue

        aliases = item.get("aliases", [])

        if isinstance(aliases, str):
            aliases = [aliases]

        candidates = aliases + [
            item.get("scheme_name", ""),
            scheme_id
        ]

        if any(_contains_phrase(query, candidate)
               for candidate in candidates):
            matches.add(scheme_id)

    # Avoid guessing when multiple schemes are named.
    if len(matches) == 1:
        return next(iter(matches))

    return None


def _detect_categories(query):
    """
    Detect broad scheme categories from English/Hindi keywords.
    Returns None if no supported category intent is detected.
    """

    category_keywords = {
        "Agriculture": [
            "farmer", "farmers", "farming", "agriculture",
            "agricultural", "kisan", "kisans", "किसान",
            "किसानों", "कृषि", "खेती", "फसल", "crop"
        ],

        "Health": [
            "health", "hospital", "medical", "treatment",
            "स्वास्थ्य", "अस्पताल", "इलाज", "चिकित्सा"
        ],

        "Housing": [
            "urban housing", "urban house", "city house",
            "शहरी आवास", "शहर में घर"
        ],

        "Rural Housing": [
            "rural housing", "village house", "rural house",
            "ग्रामीण आवास", "गांव में घर", "गांव का घर"
        ],

        "Financial Inclusion": [
            "bank account", "banking", "jan dhan",
            "बैंक खाता", "जन धन", "बैंकिंग"
        ],

        "Pension / Social Security": [
            "pension", "retirement", "old age pension",
            "पेंशन", "बुढ़ापा पेंशन", "सेवानिवृत्ति"
        ],

        "Life Insurance": [
            "life insurance", "जीवन बीमा"
        ],

        "Accident Insurance": [
            "accident insurance", "personal accident",
            "दुर्घटना बीमा"
        ],

        "Micro-enterprise Finance": [
            "small business loan", "business loan",
            "micro enterprise", "mudra loan",
            "व्यापार ऋण", "मुद्रा लोन"
        ],

        "LPG / Clean Cooking": [
            "lpg", "gas connection", "cooking gas",
            "उज्ज्वला", "गैस कनेक्शन", "रसोई गैस"
        ]
    }

    matched = set()

    for category, keywords in category_keywords.items():
        if any(_contains_phrase(query, keyword)
               for keyword in keywords):
            matched.add(category)

    # Farmer / agriculture queries can include crop insurance.
    if "Agriculture" in matched:
        matched.add("Agriculture / Crop Insurance")

    if not matched:
        return None

    return matched


def retrieve(query, top_k=5):
    """
    Scheme-aware and category-aware semantic retrieval.

    1. Explicit scheme query:
       Return only chunks of that scheme.

    2. Category query:
       Return chunks belonging to matching categories.

    3. General query:
       Return semantic matches across all schemes.

    score = reranking score
    semantic_score = original cosine similarity
    """

    global _index, _metadata

    if not isinstance(query, str) or not query.strip():
        return []

    if top_k <= 0:
        return []

    if _index is None or _metadata is None:
        load_index()

    query_vector = np.asarray(
        embed_query(query),
        dtype="float32"
    )

    if query_vector.ndim == 1:
        query_vector = query_vector.reshape(1, -1)

    faiss.normalize_L2(query_vector)

    scores, ids = _index.search(
        query_vector,
        len(_metadata)
    )

    target_scheme = _detect_scheme(query)

    target_categories = None

    if target_scheme is None:
        target_categories = _detect_categories(query)

    results = []

    for semantic_score, idx in zip(scores[0], ids[0]):

        if idx < 0:
            continue

        item = dict(_metadata[int(idx)])

        # Explicit scheme filtering.
        if target_scheme:
            if item.get("scheme_id") != target_scheme:
                continue

        # Category filtering for broad discovery.
        elif target_categories:
            item_category = item.get("category", "")

            if item_category not in target_categories:
                continue

        semantic_score = float(semantic_score)

        item["semantic_score"] = semantic_score
        item["alias_match"] = bool(target_scheme)

        item["score"] = semantic_score + (
            0.25 if target_scheme else 0.0
        )

        results.append(item)

    results.sort(
        key=lambda result: result["score"],
        reverse=True
    )

    return results[:top_k]


def build_index_from_file():
    """Build FAISS index from processed chunks."""

    if not CHUNKS_FILE.exists():
        raise FileNotFoundError(
            f"{CHUNKS_FILE} not found. "
            "Run python -m src.data_pipeline first."
        )

    with open(CHUNKS_FILE, encoding="utf-8") as f:
        chunks = json.load(f)

    return build_index(chunks)
