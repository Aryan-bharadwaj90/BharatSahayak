
from sentence_transformers import SentenceTransformer

MODEL_NAME = "intfloat/multilingual-e5-small"
_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model

def embed_documents(texts):
    texts = [f"passage: {text}" for text in texts]
    return get_model().encode(texts, normalize_embeddings=True, convert_to_numpy=True)

def embed_query(query):
    return get_model().encode(
        [f"query: {query}"],
        normalize_embeddings=True,
        convert_to_numpy=True
    )
