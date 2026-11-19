
import os
import json
import time
import pandas as pd

from openai import AsyncOpenAI
from ragas.llms import llm_factory
from ragas.embeddings import HuggingFaceEmbeddings
from ragas.metrics.collections import (
    Faithfulness,
    AnswerRelevancy,
    ContextPrecision,
    ContextRecall,
)

from src.retrieval import retrieve
from src.rag import generate_answer


TEST_FILE = "evaluation/test_questions.json"
OUTPUT_FILE = "evaluation/results.csv"
TOP_K = 5


def setup_ragas():
    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_BASE_URL")
    model_name = os.getenv("LLM_MODEL")

    if not api_key:
        raise ValueError("LLM_API_KEY environment variable is missing.")

    if not model_name:
        raise ValueError("LLM_MODEL environment variable is missing.")

    client = AsyncOpenAI(
        api_key=api_key,
        base_url=base_url if base_url else None
    )

    evaluator_llm = llm_factory(
        model_name,
        client=client,
        temperature=0.0
    )

    # Local multilingual embeddings for AnswerRelevancy.
    evaluator_embeddings = HuggingFaceEmbeddings(
        model="intfloat/multilingual-e5-small",
        device="cpu",
        normalize_embeddings=True
    )

    metrics = {
        "faithfulness": Faithfulness(llm=evaluator_llm),
        "answer_relevancy": AnswerRelevancy(
            llm=evaluator_llm,
            embeddings=evaluator_embeddings
        ),
        "context_precision": ContextPrecision(llm=evaluator_llm),
        "context_recall": ContextRecall(llm=evaluator_llm),
    }

    return metrics





def get_score(metric, **kwargs):
    try:
        result = metric.score(**kwargs)
        return round(float(result.value), 4)

    except Exception as error:
        print(
            f"Metric skipped: {type(error).__name__}: {error}",
            flush=True
        )
        return None



def evaluate_questions():
    with open(TEST_FILE, encoding="utf-8") as file:
        tests = json.load(file)

    # Optional limit for an initial small test.
    limit = int(os.getenv("EVAL_LIMIT", "0"))

    if limit > 0:
        tests = tests[:limit]

    metrics = setup_ragas()
    rows = []

    print(f"\nEvaluating {len(tests)} questions...\n")

    for index, item in enumerate(tests, start=1):
        question = item["question"]
        reference = item["reference_answer"]
        language = item.get("language", "en")

        print(f"\n[{index}/{len(tests)}] {question}")

        start = time.time()

        try:
            # Step 1: Retrieve relevant chunks.
            retrieved_chunks = retrieve(question, top_k=TOP_K)

            retrieved_contexts = [
                chunk.get("text", "")
                for chunk in retrieved_chunks
                if chunk.get("text")
            ]

            found_schemes = [
                chunk.get("scheme_id")
                for chunk in retrieved_chunks
            ]

            expected_scheme = item.get("expected_scheme")

            hit_at_5 = (
                int(expected_scheme in found_schemes)
                if expected_scheme else None
            )

            # Step 2: Generate the actual RAG answer.
            generated = generate_answer(
                question,
                retrieved_chunks,
                language=language
            )

            answer = generated.get("answer", "")

            # Step 3: Calculate RAGAS metrics.
            scores = {}

            if answer.strip() and retrieved_contexts:
                scores["faithfulness"] = get_score(
                    metrics["faithfulness"],
                    user_input=question,
                    response=answer,
                    retrieved_contexts=retrieved_contexts
                )

                scores["answer_relevancy"] = get_score(
                    metrics["answer_relevancy"],
                    user_input=question,
                    response=answer
                )

                scores["context_precision"] = get_score(
                    metrics["context_precision"],
                    user_input=question,
                    reference=reference,
                    retrieved_contexts=retrieved_contexts
                )

                scores["context_recall"] = get_score(
                    metrics["context_recall"],
                    user_input=question,
                    reference=reference,
                    retrieved_contexts=retrieved_contexts
                )
            else:
                scores = {
                    "faithfulness": None,
                    "answer_relevancy": None,
                    "context_precision": None,
                    "context_recall": None
                }

            latency = round(time.time() - start, 2)

            row = {
                "question": question,
                "language": language,
                "expected_scheme": expected_scheme,
                "retrieved_scheme_ids": json.dumps(found_schemes),
                "hit_at_5": hit_at_5,
                "generated_answer": answer,
                "reference_answer": reference,
                **scores,
                "latency_seconds": latency
            }

        except Exception as error:
            print(f"Question evaluation failed: {error}")

            row = {
                "question": question,
                "language": language,
                "expected_scheme": item.get("expected_scheme"),
                "hit_at_5": None,
                "faithfulness": None,
                "answer_relevancy": None,
                "context_precision": None,
                "context_recall": None,
                "latency_seconds": round(time.time() - start, 2),
                "error": str(error)
            }

        rows.append(row)

        # Save after every question to preserve completed results.
        pd.DataFrame(rows).to_csv(OUTPUT_FILE, index=False)

        print("Scores:", {
            key: row.get(key)
            for key in (
                "faithfulness",
                "answer_relevancy",
                "context_precision",
                "context_recall"
            )
        })

    df = pd.DataFrame(rows)

    print("\n========== EVALUATION SUMMARY ==========")

    for metric in (
        "hit_at_5",
        "faithfulness",
        "answer_relevancy",
        "context_precision",
        "context_recall"
    ):
        if metric in df.columns:
            average = pd.to_numeric(
                df[metric], errors="coerce"
            ).mean()

            if pd.notna(average):
                print(f"{metric}: {average:.4f}")

    print(f"\nResults saved to: {OUTPUT_FILE}")

    return df


if __name__ == "__main__":
    evaluate_questions()
