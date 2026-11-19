# BharatSahayak 🇮🇳

## A Multilingual, Evidence-Grounded AI Assistant for Indian Government Schemes

BharatSahayak is a Generative AI course-project prototype that helps
people explore Indian government welfare schemes in **English and
Hindi**. It retrieves relevant information from a curated knowledge
base, generates an evidence-grounded response, and displays official
source links.

> **Important:** This is an informational prototype, not a government
> service. It does not access live beneficiary databases or make
> official eligibility decisions. Always confirm current rules with the
> relevant official portal or authority.

## 1. What we built

-   Hindi and English question answering.
-   Scheme discovery by name and broad category.
-   Retrieval-grounded answers with official source links.
-   Guidance on benefits, eligibility, documents and application steps
    when present in the knowledge base.
-   Preliminary, deterministic eligibility checks using Python rules.
-   Three-valued eligibility outcomes: `satisfied`, `not_satisfied`, and
    `unknown`.
-   A Gradio web interface for interactive use.

### Schemes in the curated dataset

1.  PM-KISAN
2.  Ayushman Bharat -- PM-JAY
3.  PMAY-Urban
4.  PMAY-Gramin
5.  Pradhan Mantri Jan-Dhan Yojana (PMJDY)
6.  Atal Pension Yojana
7.  Pradhan Mantri Jeevan Jyoti Bima Yojana (PMJJBY)
8.  Pradhan Mantri Suraksha Bima Yojana (PMSBY)
9.  Pradhan Mantri MUDRA Yojana
10. Pradhan Mantri Ujjwala Yojana (PMUY)
11. Pradhan Mantri Fasal Bima Yojana (PMFBY)

Scheme data is curated project data, not a live feed. Benefits,
exclusions, deadlines and State/UT rules can change; users should verify
details with official sources.

## 2. Technology stack

  -----------------------------------------------------------------------
  Layer                               Technology
  ----------------------------------- -----------------------------------
  Language                            Python

  Interface                           Gradio

  LLM                                 Gemini API using its
                                      OpenAI-compatible endpoint

  Embeddings                          `intfloat/multilingual-e5-small`

  Vector retrieval                    FAISS, normalized vectors with
                                      inner-product similarity

  Keyword retrieval                   BM25 (`rank-bm25`)

  Hybrid fusion                       Reciprocal Rank Fusion (RRF)

  Reranker                            `BAAI/bge-reranker-v2-m3` via
                                      Sentence Transformers

  PDF extraction                      PyMuPDF

  Data/evaluation                     JSON, NumPy, Pandas, custom tests,
                                      RAGAS
  -----------------------------------------------------------------------

## 3. How the pipeline works

``` text
User question (Hindi or English)
             |
             v
        Gradio UI
             |
             v
  Scheme / category / section intent
             |
             v
       Parallel retrieval
       /              \
      v                v
 FAISS semantic      BM25 keyword
   retrieval           retrieval
       \              /
        \            /
         v          v
       RRF hybrid fusion
             |
             v
      Candidate deduplication
             |
             v
 Multilingual cross-encoder reranking
             |
             v
       Top evidence chunks
             |
             v
      Gemini answer generation
             |
             v
  Answer, source links, disclaimer
```

### Data preparation

The data pipeline processes scheme records and creates section-oriented
chunks for benefits, eligibility/exclusions, documents, application
process, and deadlines/amounts. Chunk metadata carries scheme
identifiers, category, section, and source information where available.

### Retrieval

1.  **FAISS semantic search:** `multilingual-e5-small` embeds chunks and
    queries. Vectors are L2-normalized and searched with a FAISS
    inner-product index.
2.  **BM25 keyword search:** tokenized text and scheme metadata are
    searched for exact names, abbreviations, numbers and terms.
3.  **RRF fusion:** the two ranked lists are combined using Reciprocal
    Rank Fusion. RRF combines ranks rather than treating raw FAISS and
    BM25 scores as directly comparable.
4.  **Reranking:** `BAAI/bge-reranker-v2-m3` scores query--chunk pairs
    and reorders the candidate evidence. If reranker loading or
    inference fails, the current implementation falls back to RRF
    results.
5.  **Generation:** retrieved chunks are passed to Gemini. The prompt
    instructs the model to answer in the requested language, stay
    grounded in the supplied evidence, avoid inventing scheme details
    and provide sources. Grounding reduces, but does not eliminate,
    hallucinations.

### Eligibility logic

Eligibility is evaluated separately from Gemini using deterministic
Python rules. Missing profile details produce `unknown`; failed
configured conditions can produce `not_satisfied`; a profile satisfying
all configured conditions can produce `satisfied`. This is only a
preliminary assessment. For example, the app cannot query a live PM-JAY
beneficiary database.

## 4. Project structure

The key project files are expected to resemble:

``` text
BharatSahayak/
├── app.py
├── requirements.txt
├── README.md
├── src/
│   ├── data_pipeline.py
│   ├── embeddings.py
│   ├── retrieval.py
│   ├── rag.py
│   └── eligibility.py
├── data/
│   ├── raw/
│   │   └── schemes.json
│   └── processed/
│       ├── chunks.json
│       ├── schemes.faiss
│       └── index_metadata.json
└── evaluation/
    ├── evaluation.py
    ├── test_questions.json
    ├── test_eligibility.py
    └── results.csv
```

Actual folders or filenames may vary slightly. Keep the paths consistent
with the code.

## 5. Run locally (Windows)

From the project root in PowerShell:

``` powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If the processed knowledge base/index has not been built:

``` powershell
python -m src.data_pipeline
```

Set Gemini configuration in the current PowerShell session:

``` powershell
$env:LLM_API_KEY="YOUR_GEMINI_API_KEY"
$env:LLM_BASE_URL="https://generativelanguage.googleapis.com/v1beta/openai"
$env:LLM_MODEL="gemini-3.5-flash-lite"
```

Launch:

``` powershell
python app.py
```

Open the local URL printed by Gradio, usually `http://127.0.0.1:7860`.

Never commit the API key or hard-code it in source files.

## 6. Run on Google Colab

Create a **fresh ZIP from the latest project folder** so it includes the
new BM25/RRF/reranker code and updated dependencies.

### A. Create the ZIP on Windows

Run from the parent directory of your project folder (adjust the folder
name if yours differs):

``` powershell
Compress-Archive -Path ".\BharatSahayak_team_code\*" -DestinationPath ".\BharatSahayak_Final.zip" -Force
```

Exclude `.venv`, `.git`, `__pycache__`, and local secrets. Include
`app.py`, `requirements.txt`, `src/`, and `data/`. Include `evaluation/`
if you want the test scripts in Colab.

### B. Upload and extract in Colab

``` python
from google.colab import files
uploaded = files.upload()  # Select BharatSahayak_Final.zip
```

``` python
import os
import zipfile

zip_name = "BharatSahayak_Final.zip"
project_dir = "/content/BharatSahayak"
os.makedirs(project_dir, exist_ok=True)

with zipfile.ZipFile(zip_name, "r") as z:
    z.extractall(project_dir)

print(os.listdir(project_dir))
```

Change into the directory that actually contains `app.py`. If the ZIP
has an enclosing folder, `%cd` into that folder:

``` python
%cd /content/BharatSahayak
!ls
```

If `app.py` is nested, use `%cd /content/BharatSahayak/<nested-folder>`
instead.

### C. Install dependencies

``` python
!pip install -r requirements.txt
```

Check that `requirements.txt` includes the packages used by the latest
code, particularly `rank-bm25` and `sentence-transformers`, in addition
to the project's existing dependencies.

### D. Configure the Gemini key using Colab Secrets

In Colab, open the **Secrets** panel (key icon), create a secret named
`LLM_API_KEY`, and enable notebook access. Then run:

``` python
import os
from google.colab import userdata

os.environ["LLM_API_KEY"] = userdata.get("LLM_API_KEY")
os.environ["LLM_BASE_URL"] = "https://generativelanguage.googleapis.com/v1beta/openai"
os.environ["LLM_MODEL"] = "gemini-3.5-flash-lite"
```

Do not print the key or put it in the notebook source.

### E. Launch

If `app.py` already contains `demo.launch(share=True)`, run:

``` python
!python app.py
```

Open the temporary `gradio.live` URL printed in the output. The link
only works while the Colab runtime and app process remain active; it is
not permanent hosting. Anyone with the link may be able to access the
demo, so do not enter sensitive personal information.

**Reranker download:** The first use of `BAAI/bge-reranker-v2-m3`
downloads a large model (about 2.27 GB was observed during local
development). Allow sufficient disk space and startup time. The model is
reused within the running process. If loading fails, the code falls back
to the RRF ranking.

## 7. Evaluation completed and current status

The bilingual retrieval test set contains **22 questions**: English and
Hindi questions for each of the 11 schemes. The test records include
expected scheme IDs and reference information/evidence.

Observed during development:

-   Before hybrid retrieval was added, the semantic retrieval evaluation
    achieved Hit@5 = **1.00 (22/22)**.
-   BM25 was tested independently and returned relevant PM-KISAN chunks.
-   Hybrid FAISS + BM25 + RRF smoke tests in English and Hindi ranked
    PM-KISAN benefits first.
-   The multilingual reranker smoke tests in English and Hindi also
    ranked PM-KISAN benefits first.
-   Three eligibility tests passed: empty profile → `unknown`; synthetic
    profile satisfying configured PM-KISAN rules → `satisfied`; profile
    failing a configured exclusion → `not_satisfied`.
-   A two-question RAGAS pilot completed with non-null metric scores. A
    later full RAGAS run was blocked by Gemini free-tier API quota
    limits.

**Evaluation caveats:**

-   The 22/22 Hit@5 result was measured on the earlier semantic
    retrieval implementation. It must not be presented as a final
    hybrid/reranker benchmark.
-   The English and Hindi hybrid/reranker checks are smoke tests, not a
    full 22-question benchmark.
-   Reference answers/evidence were derived from the project's curated
    dataset, not an independent verification of all current government
    rules.
-   Full-dataset RAGAS evaluation remains incomplete due to API quota
    limits.

## 8. Team responsibilities

  Member      Main responsibility
  ----------- ----------------------------------------------
  Sharma      Scheme data and data pipeline
  Abhishek    Multilingual embeddings and retrieval
  Shivanshu   RAG, prompts and eligibility logic
  Bharadwaj   Integration, Gradio interface and evaluation

Update this table if the final division of work changed.

## 9. Demo checklist

-   [ ] Initialize/load the knowledge base.
-   [ ] Ask an English PM-KISAN question.
-   [ ] Ask the equivalent question in Hindi.
-   [ ] Ask about another scheme (for example PM-JAY or PMAY).
-   [ ] Ask separately about benefits, eligibility, documents and
    application steps.
-   [ ] Check official source links.
-   [ ] Confirm missing profile details do not become a false
    eligibility claim.
-   [ ] Confirm the preliminary-guidance disclaimer is visible.
-   [ ] Try an unrelated question or one with no supporting evidence.
-   [ ] Confirm the Colab link works while the runtime is active.

## 10. Limitations and future work

-   Independently verify and refresh scheme facts using official
    sources, including State/UT differences.
-   Run the complete 22-question retrieval evaluation on the final
    hybrid + reranker implementation.
-   Complete RAGAS evaluation when API quota is available; add
    quota-aware resume support.
-   Measure and optimize end-to-end latency.
-   Expand scheme coverage and Hindi/English test diversity.
-   Improve provenance and freshness tracking.
-   Add production hosting, access controls, monitoring and privacy
    safeguards before public-service use.

## 11. Official portals

-   PM-KISAN: https://pmkisan.gov.in/
-   Ayushman Bharat PM-JAY: https://pmjay.gov.in/
-   PMAY-Urban: https://pmay-urban.gov.in/
-   PMAY-Gramin: https://pmayg.dord.gov.in/
-   PMJDY: https://www.pmjdy.gov.in/
-   Atal Pension Yojana: https://www.jansuraksha.gov.in/
-   PMJJBY: https://jansuraksha.gov.in/
-   PMSBY: https://jansuraksha.gov.in/
-   PM MUDRA: https://www.mudra.org.in/
-   PMUY: https://pmuy.gov.in/
-   PMFBY: https://pmfby.gov.in/

------------------------------------------------------------------------

**Project:** BharatSahayak\
**Type:** Generative AI / Retrieval-Augmented Generation (RAG) course
project\
**Languages:** English and Hindi\
**Interface:** Gradio\
**Status:** Working prototype; full final-pipeline retrieval benchmark
and full RAGAS evaluation remain pending.
