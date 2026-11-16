# BharatSahayak team code handoff

## Branch ownership
- Sharma: `feature/data-pipeline` — `src/data_pipeline.py`, `data/schemes.json`
- Abhishek: `feature/retrieval` — `src/embeddings.py`, `src/retrieval.py`
- Shivanshu: `feature/rag-eligibility` — `src/eligibility.py`, `src/prompts.py`, `src/rag.py`
- Bharadwaj: `feature/integration-ui` — `app.py`, `evaluation/`

## Shared workflow
1. Clone repository in Colab.
2. `cd BharatSahayak`
3. `git fetch origin`
4. Checkout your assigned feature branch.
5. Merge latest `origin/dev` into your feature branch.
6. `pip install -r requirements.txt`
7. Create and test only your assigned files.
8. Commit and push your feature branch.
9. Open PR with base `dev` and compare your feature branch.
10. Review and merge only after tests pass.

## Run
```bash
python -m src.data_pipeline
```
Then build FAISS index:
```python
from src.retrieval import build_index_from_file
build_index_from_file()
```
Then:
```bash
python app.py
```

## Important
- Scheme JSON is a starter template. Verify and complete every scheme fact from current official sources before demo.
- Eligibility currently returns `unknown` until reviewed, explicit rule predicates are implemented. Do not claim official eligibility.
- Configure `LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL` as environment secrets. Never commit credentials.
- Run all tests after integration. Retrieval hit-rate is not a substitute for human evaluation of answer correctness or citation accuracy.
