import re
from rank_bm25 import BM25Okapi
import json
from pathlib import Path
from sentence_transformers import CrossEncoder
import faiss
import numpy as np

from src.embeddings import embed_documents, embed_query

ROOT = Path(__file__).resolve().parent.parent
CHUNKS_FILE = ROOT / "data" / "processed" / "chunks.json"
INDEX_FILE = ROOT / "data" / "processed" / "schemes.faiss"
META_FILE = ROOT / "data" / "processed" / "index_metadata.json"

_index = None
_metadata = None

_bm25 = None
_bm25_corpus = None

_reranker = None
_reranker_failed = False

def _tokenize(text):
    """Tokenize English and Hindi text while preserving numbers."""
    return re.findall(r"[^\W_]+", str(text).casefold(), flags=re.UNICODE)


def _build_bm25(chunks):
    """Build a BM25 keyword index from scheme chunks."""
    global _bm25, _bm25_corpus

    _bm25_corpus = [
        _tokenize(
            " ".join([
                item.get("text", ""),
                item.get("scheme_name", ""),
                item.get("scheme_id", ""),
                " ".join(item.get("aliases", []))
                if isinstance(item.get("aliases", []), list)
                else str(item.get("aliases", ""))
            ])
        )
        for item in chunks
    ]

    _bm25 = BM25Okapi(_bm25_corpus)

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
    _build_bm25(chunks)
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
    _build_bm25(metadata)
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

def keyword_search(query, top_k=5):
    """Retrieve chunks using BM25 keyword matching."""

    global _bm25, _metadata

    if not isinstance(query, str) or not query.strip():
        return []

    if top_k <= 0:
        return []

    if _metadata is None or _bm25 is None:
        load_index()

    tokens = _tokenize(query)

    if not tokens:
        return []

    scores = _bm25.get_scores(tokens)
    ranked_ids = np.argsort(scores)[::-1]

    results = []

    for idx in ranked_ids:
        score = float(scores[idx])

        if score <= 0:
            break

        item = dict(_metadata[int(idx)])
        item["keyword_score"] = score
        results.append(item)

        if len(results) >= top_k:
            break

    return results

# def retrieve(query, top_k=5):
#     """
#     Scheme-aware semantic retrieval with duplicate suppression.
#     """

#     global _index, _metadata

#     if not isinstance(query, str) or not query.strip():
#         return []

#     if top_k <= 0:
#         return []

#     if _index is None or _metadata is None:
#         load_index()

#     query_vector = np.asarray(
#         embed_query(query),
#         dtype="float32"
#     )

#     if query_vector.ndim == 1:
#         query_vector = query_vector.reshape(1, -1)

#     faiss.normalize_L2(query_vector)

#     scores, ids = _index.search(
#         query_vector,
#         len(_metadata)
#     )

#     target_scheme = _detect_scheme(query)
#     target_categories = None

#     if target_scheme is None:
#         target_categories = _detect_categories(query)

#     results = []
#     seen = set()

#     for semantic_score, idx in zip(scores[0], ids[0]):

#         if idx < 0:
#             continue

#         item = dict(_metadata[int(idx)])

#         if target_scheme:
#             if item.get("scheme_id") != target_scheme:
#                 continue

#         elif target_categories:
#             if item.get("category", "") not in target_categories:
#                 continue

#         # Suppress identical text chunks.
#         normalized_text = " ".join(
#             item.get("text", "").casefold().split()
#         )

#         if normalized_text in seen:
#             continue

#         seen.add(normalized_text)

#         semantic_score = float(semantic_score)

#         item["semantic_score"] = semantic_score
#         item["alias_match"] = bool(target_scheme)
#         item["score"] = semantic_score + (
#             0.25 if target_scheme else 0.0
#         )

#         results.append(item)

#         query_lower = query.casefold()

#     section_keywords = {
#         "benefits": [
#             "benefit", "benefits", "what do i get",
#             "how much assistance", "लाभ", "फायदे"
#         ],
#         "eligibility": [
#             "eligibility", "eligible", "qualify",
#             "exclusions", "who can apply",
#             "पात्रता", "कौन पात्र"
#         ],
#         "documents": [
#             "document", "documents", "required papers",
#             "proof", "कागजात", "दस्तावेज"
#         ],
#         "application_process": [
#             "apply", "application", "registration",
#             "how to apply", "आवेदन", "रजिस्ट्रेशन"
#         ],
#         "deadlines_and_amounts": [
#             "deadline", "last date", "due date",
#             "premium", "instalment", "installment",
#             "amount", "₹", "rupees", "राशि", "अंतिम तिथि"
#         ],
#     }

#     preferred_section = None

#     for section, keywords in section_keywords.items():
#         if any(keyword in query_lower for keyword in keywords):
#             preferred_section = section
#             break

#     if preferred_section:
#         for result in results:
#             if result.get("section_type") == preferred_section:
#                 result["score"] += 0.05

#     results.sort(
#         key=lambda result: result["score"],
#         reverse=True
#     )

#     return results[:top_k]


def _rerank_results(query, results, top_k):
    """Rerank retrieved candidates using a multilingual cross-encoder."""

    global _reranker, _reranker_failed

    if not results:
        return []

    # If model loading previously failed, retain the RRF ranking.
    if _reranker_failed:
        return results[:top_k]

    try:
        if _reranker is None:
            print("Loading multilingual reranker...", flush=True)
            _reranker = CrossEncoder(
                "BAAI/bge-reranker-v2-m3",
                max_length=512
            )

        pairs = [
            [query, item.get("text", "")]
            for item in results
        ]

        scores = _reranker.predict(pairs)

        for item, score in zip(results, scores):
            item["rerank_score"] = float(score)

        results.sort(
            key=lambda item: item["rerank_score"],
            reverse=True
        )

        return results[:top_k]

    except Exception as error:
        print(
            f"Reranking unavailable; using RRF ranking: {error}",
            flush=True
        )
        _reranker_failed = True
        return results[:top_k]


def retrieve(query, top_k=5):
    """
    Hybrid retrieval using FAISS semantic search and BM25 keyword search.
    Combines rankings using Reciprocal Rank Fusion (RRF).
    """

    global _index, _metadata, _bm25

    if not isinstance(query, str) or not query.strip():
        return []

    if top_k <= 0:
        return []

    if _index is None or _metadata is None or _bm25 is None:
        load_index()

    # Detect explicit scheme and broad category intent.
    target_scheme = _detect_scheme(query)
    target_categories = None

    if target_scheme is None:
        target_categories = _detect_categories(query)

    # Apply the same filters to both retrieval methods.
    eligible_ids = set()

    for idx, item in enumerate(_metadata):
        if target_scheme:
            if item.get("scheme_id") != target_scheme:
                continue

        elif target_categories:
            if item.get("category", "") not in target_categories:
                continue

        eligible_ids.add(idx)

    if not eligible_ids:
        return []

    # 1. FAISS semantic retrieval.
    query_vector = np.asarray(
        embed_query(query),
        dtype="float32"
    )

    if query_vector.ndim == 1:
        query_vector = query_vector.reshape(1, -1)

    faiss.normalize_L2(query_vector)

    semantic_scores, semantic_ids = _index.search(
        query_vector,
        len(_metadata)
    )

    # 2. BM25 keyword retrieval.
    keyword_scores = _bm25.get_scores(_tokenize(query))
    keyword_ids = np.argsort(keyword_scores)[::-1]

    # 3. Reciprocal Rank Fusion.
    rrf_k = 60
    rrf_scores = {}

    semantic_score_map = {}
    keyword_score_map = {}

    for rank, idx in enumerate(semantic_ids[0], start=1):
        idx = int(idx)

        if idx < 0 or idx not in eligible_ids:
            continue

        semantic_score_map[idx] = float(
            semantic_scores[0][rank - 1]
        )

        rrf_scores[idx] = rrf_scores.get(idx, 0.0) + (
            1.0 / (rrf_k + rank)
        )

    for rank, idx in enumerate(keyword_ids, start=1):
        idx = int(idx)

        if idx not in eligible_ids:
            continue

        score = float(keyword_scores[idx])

        if score <= 0:
            continue

        keyword_score_map[idx] = score

        rrf_scores[idx] = rrf_scores.get(idx, 0.0) + (
            1.0 / (rrf_k + rank)
        )

    # 4. Section-intent boost.
    query_lower = query.casefold()

    section_keywords = {
        "benefits": [
            "benefit", "benefits", "what do i get",
            "how much assistance", "लाभ", "फायदे"
        ],
        "eligibility": [
            "eligibility", "eligible", "qualify",
            "exclusions", "who can apply",
            "पात्रता", "कौन पात्र"
        ],
        "documents": [
            "document", "documents", "required papers",
            "proof", "कागजात", "दस्तावेज"
        ],
        "application_process": [
            "apply", "application", "registration",
            "how to apply", "आवेदन", "रजिस्ट्रेशन"
        ],
        "deadlines_and_amounts": [
            "deadline", "last date", "due date",
            "premium", "instalment", "installment",
            "amount", "₹", "rupees", "राशि", "अंतिम तिथि"
        ],
    }

    preferred_section = None

    for section, keywords in section_keywords.items():
        if any(keyword in query_lower for keyword in keywords):
            preferred_section = section
            break

    # 5. Prepare final ranked results.
    results = []
    seen = set()

    for idx, fused_score in sorted(
        rrf_scores.items(),
        key=lambda pair: pair[1],
        reverse=True
    ):
        item = dict(_metadata[idx])

        normalized_text = " ".join(
            item.get("text", "").casefold().split()
        )

        if normalized_text in seen:
            continue

        seen.add(normalized_text)

        item["semantic_score"] = semantic_score_map.get(idx, 0.0)
        item["keyword_score"] = keyword_score_map.get(idx, 0.0)

        item["rrf_score"] = fused_score

        if target_scheme:
            fused_score += 0.25

        if preferred_section and item.get("section_type") == preferred_section:
            fused_score += 0.05

        item["score"] = fused_score
        item["alias_match"] = bool(target_scheme)

        results.append(item)

    results.sort(
        key=lambda result: result["score"],
        reverse=True
    )

    # return results[:top_k]
    candidate_pool = results[:max(top_k * 4, 20)]
    return _rerank_results(query, candidate_pool, top_k)


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
