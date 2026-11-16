
import json, time
import pandas as pd
from src.retrieval import retrieve

def evaluate_questions(test_file="evaluation/test_questions.json", top_k=5):
    with open(test_file, encoding="utf-8") as f:
        tests = json.load(f)
    rows = []
    for item in tests:
        start = time.time()
        results = retrieve(item["question"], top_k=top_k)
        latency = time.time() - start
        expected = item.get("expected_scheme")
        found = [r.get("scheme_id") for r in results]
        rows.append({
            "question": item["question"],
            "language": item.get("language", "unknown"),
            "expected_scheme": expected,
            "retrieved_scheme_ids": found,
            "hit_at_5": int(expected in found) if expected else None,
            "latency_seconds": round(latency, 3)
        })
    df = pd.DataFrame(rows)
    df.to_csv("evaluation/results.csv", index=False)
    print(df.to_string(index=False))
    if "hit_at_5" in df and df["hit_at_5"].notna().any():
        print("Precision-like hit rate@5:", df["hit_at_5"].dropna().mean())
    return df

if __name__ == "__main__":
    evaluate_questions()
