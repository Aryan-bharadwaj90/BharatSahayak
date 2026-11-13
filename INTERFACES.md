# BharatSahayak - Team Interfaces

## Sharma - Data Pipeline
def process_documents(pdf_paths):
    return chunks

## Abhishek - Retrieval
def build_index(chunks):
    pass

def retrieve(query, top_k=5):
    return results

## Shivanshu - RAG and Eligibility
def check_eligibility(scheme_id, user_profile):
    return result

def generate_answer(query, retrieved_chunks, eligibility_result, language):
    return answer

## Bharadwaj - Integration
def answer_user(query, user_profile=None, language="auto"):
    return response
