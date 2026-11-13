# BharatSahayak — Team Onboarding & Development Guide

## 1. Project Overview

BharatSahayak is a bilingual (Hindi and English) Generative AI assistant that helps Indian citizens discover government schemes, understand benefits, check preliminary eligibility, and access application information.

**Technology Stack**
- Python
- Google Colab
- GitHub
- Gradio
- FAISS
- Multilingual Sentence Transformers
- LLM API
- PyMuPDF

## 2. Step 1 — Access the GitHub Repository

Open the central project repository:

https://github.com/Aryan-bharadwaj90/BharatSahayak

Every team member should have collaborator access.

Do not create a separate repository. All members work in the same central repository.

## 3. Step 2 — Understand the Branch Structure

We use Git branches to allow four members to work independently.

| Branch | Assigned Member | Responsibility |
|---|---|---|
| main | Team | Final stable project |
| dev | Team | Integration and testing |
| feature/data-pipeline | Sharma | Data collection and processing |
| feature/retrieval | Abhishek | Multilingual retrieval |
| feature/rag-eligibility | Shivanshu | RAG and eligibility |
| feature/integration-ui | Bharadwaj | Integration and Gradio UI |

**Important rules:**
- Never work directly on main.
- Never push directly to dev.
- Work only on your assigned feature branch.
- Submit a Pull Request to merge your work into dev.

## 4. Step 3 — Open Google Colab

1. Visit https://colab.research.google.com/
2. Sign in with your Google account.
3. Click New Notebook.
4. Rename your notebook using your name and project responsibility.

## 5. Step 4 — Clone the Repository

Create a code cell in Google Colab and execute:

```python
!git clone https://github.com/Aryan-bharadwaj90/BharatSahayak.git
```

This downloads the central GitHub repository into your Colab environment.

If authentication is requested, use an approved secure GitHub authentication method. Never share passwords or personal access tokens.

## 6. Step 5 — Enter the Project Folder

Execute:

```python
%cd BharatSahayak
```

You are now working inside the downloaded project.

## 7. Step 6 — Switch to Your Assigned Branch

First, fetch the latest branches:

```python
!git fetch origin
```

Then switch to your assigned branch.

**Sharma:**

```python
!git checkout feature/data-pipeline
```

**Abhishek:**

```python
!git checkout feature/retrieval
```

**Shivanshu:**

```python
!git checkout feature/rag-eligibility
```

**Bharadwaj:**

```python
!git checkout feature/integration-ui
```

Verify your current branch:

```python
!git branch --show-current
```

Make sure it displays your assigned branch.

## 8. Step 7 — Synchronize with the Latest dev Branch

Before starting work, update your feature branch with the latest shared project changes:

```python
!git fetch origin
!git merge origin/dev
```

If Git reports conflicts, resolve them carefully before continuing. Do not blindly overwrite another member's work.

## 9. Step 8 — Install Project Dependencies

Execute:

```python
!pip install -r requirements.txt
```

This installs the libraries required by BharatSahayak.

You normally need to install dependencies once per fresh Colab runtime.

## 10. Step 9 — Start Working on Your Assigned Module

Each member must work on their assigned files.

### Sharma — Data Pipeline

Files:
- `src/data_pipeline.py`
- `data/schemes.json`

Responsibilities:
- Collect official government scheme information.
- Extract information from PDFs and official websites.
- Clean and structure scheme data.
- Include eligibility, benefits, documents, application steps and source URLs.

### Abhishek — Multilingual Retrieval

Files:
- `src/embeddings.py`
- `src/retrieval.py`

Responsibilities:
- Generate multilingual embeddings.
- Build a FAISS index.
- Implement semantic retrieval.
- Test Hindi and English queries.

### Shivanshu — RAG and Eligibility

Files:
- `src/eligibility.py`
- `src/rag.py`
- `src/prompts.py`

Responsibilities:
- Implement the LLM integration.
- Generate answers grounded in retrieved information.
- Implement deterministic eligibility checks.
- Return satisfied, not satisfied and unknown conditions.
- Include source references and uncertainty handling.

### Bharadwaj — Integration and UI

Files:
- `app.py`
- `evaluation/evaluation.py`
- `notebooks/BharatSahayak_Demo.ipynb`

Responsibilities:
- Integrate all team modules.
- Build the Gradio interface.
- Test the complete application.
- Evaluate the system.
- Prepare the final demonstration notebook.

## 11. Step 10 — Save Your Code to GitHub

After completing and testing your assigned work, execute:

```python
!git status
```

Add your own files:

```python
!git add .
```

Commit your changes:

```python
!git commit -m "Describe your completed work"
```

Push your changes:

```python
!git push origin YOUR_BRANCH_NAME
```

Replace `YOUR_BRANCH_NAME` with your assigned branch.

For example:

```python
!git push origin feature/retrieval
```

## 12. Step 11 — Create a Pull Request

After pushing your code:

1. Open the GitHub repository.
2. Click Pull requests.
3. Click New pull request, or Compare & pull request.
4. Select the correct branches.

**Base branch:** `dev`

**Compare branch:** Your assigned feature branch.

5. Review the changes.
6. Add a meaningful title and description.
7. Click Create pull request.
8. Ask another team member to review the code.
9. Merge after approval and successful testing.

Never merge directly into main during development.

## 13. Step 12 — Update Your Branch Again

Before starting your next development session, synchronize with the latest dev:

```python
!git fetch origin
!git merge origin/dev
```

Continue coding, testing, committing and pushing.

## 14. Step 13 — Final Integration

After all four members have completed their modules:

1. Merge all approved feature branches into dev.
2. Install the dependencies.
3. Test all module imports.
4. Run the complete Gradio application.
5. Test Hindi and English queries.
6. Check retrieval quality, eligibility results and citations.
7. Fix integration errors.
8. Prepare the final demonstration.
9. Merge the tested dev branch into main.

## 15. Important Team Rules

1. Each member owns their assigned files.
2. Do not rename shared functions without team agreement.
3. Do not commit API keys, passwords or secrets.
4. Test your code before pushing.
5. Communicate interface changes with the team.
6. Review Pull Requests before merging.
7. Keep dev updated and main stable.
8. Commit your work regularly.

## 16. Shared Development Workflow

The standard workflow for every team member is:

**GitHub Repository → Google Colab → Clone Repository → Switch Feature Branch → Merge Latest dev → Install Dependencies → Write Code → Test → Commit → Push → Pull Request → Review → Merge into dev**

---

**BharatSahayak Team**

Build independently. Integrate collaboratively. Deliver together.
