import time 
import os
import requests

from src.prompts import SYSTEM_PROMPT, build_user_prompt


def _sources(chunks):
    """Collect unique official source links."""
    seen = set()
    sources = []

    for chunk in chunks:
        url = chunk.get("source_url", "")
        title = chunk.get("source_title", "Official source")

        if url and url not in seen:
            seen.add(url)

            sources.append({
                "source_title": title,
                "source_url": url
            })

    return sources


def _extract_answer(data):
    """Safely extract text from an OpenAI-compatible response."""

    choices = data.get("choices", [])

    if not choices:
        raise ValueError("The API returned no choices.")

    message = choices[0].get("message", {})
    content = message.get("content", "")

    # Some compatible APIs may return content as text blocks.
    if isinstance(content, list):
        text_parts = []

        for part in content:
            if isinstance(part, dict) and part.get("type") == "text":
                text_parts.append(part.get("text", ""))

        content = "\n".join(text_parts)

    if not isinstance(content, str) or not content.strip():
        raise ValueError("The LLM returned an empty answer.")

    return content.strip()


def generate_answer(
    query,
    retrieved_chunks,
    eligibility_result=None,
    language="auto"
):
    """
    Generate evidence-grounded answers using
    an OpenAI-compatible LLM endpoint.
    """

    if not retrieved_chunks:
        return {
            "answer": "No relevant scheme information was found.",
            "language": language,
            "sources": [],
            "disclaimer": (
                "Please consult the relevant official government portal."
            )
        }

    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_BASE_URL", "").rstrip("/")
    model = os.getenv("LLM_MODEL")

    sources = _sources(retrieved_chunks)

    if not api_key or not base_url or not model:
        return {
            "answer": (
                "Relevant scheme information was retrieved, "
                "but the LLM API is not configured. "
                "Configure LLM_API_KEY, LLM_BASE_URL and LLM_MODEL."
            ),
            "language": language,
            "sources": sources,
            "disclaimer": "Preliminary guidance only."
        }

    url = (
        base_url
        if base_url.endswith("/chat/completions")
        else base_url + "/chat/completions"
    )

    try:
        user_prompt = build_user_prompt(
            query,
            retrieved_chunks,
            eligibility_result,
            language
        )

        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            "temperature": 0.2,
            "max_tokens": 600
        }

        
        response = None

        for attempt in range(3):
            response = requests.post(
                url,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=120
            )

            if response.status_code != 503:
                break

            if attempt < 2:
                wait_time = 2 ** (attempt + 1)

                print(
                    f"Gemini temporarily overloaded. "
                    f"Retrying in {wait_time} seconds..."
                )

                time.sleep(wait_time)

        response.raise_for_status()


        data = response.json()
        answer = _extract_answer(data)

        return {
            "answer": answer,
            "language": language,
            "sources": sources,
            "disclaimer": (
                "Preliminary guidance only. "
                "Final eligibility is decided by the relevant "
                "government authority."
            )
        }

    except requests.exceptions.HTTPError as error:
        status_code = (
            error.response.status_code
            if error.response is not None
            else "Unknown"
        )

        # Avoid exposing credentials or full request details.
        if status_code == 429:
            message = (
                "The LLM API rate limit or quota has been reached. "
                "Please wait and try again."
            )
        elif status_code in (401, 403):
            message = (
                "LLM authentication failed. Check your API key "
                "and provider permissions."
            )
        elif status_code == 404:
            message = (
                "LLM model or endpoint not found. "
                "Check LLM_MODEL and LLM_BASE_URL."
            )
        else:
            message = f"LLM API returned HTTP status {status_code}."

        return {
            "answer": message,
            "language": language,
            "sources": sources,
            "disclaimer": "Please verify information using official sources."
        }

    except requests.exceptions.Timeout:
        return {
            "answer": "The LLM request timed out. Please try again.",
            "language": language,
            "sources": sources,
            "disclaimer": "Please consult the official government portal."
        }

    except requests.exceptions.RequestException:
        return {
            "answer": (
                "Could not connect to the LLM service. "
                "Please check your internet connection and API settings."
            ),
            "language": language,
            "sources": sources,
            "disclaimer": "Please consult the official government portal."
        }

    except (ValueError, KeyError, IndexError, TypeError):
        return {
            "answer": (
                "The LLM returned an unexpected response. "
                "Please try again."
            ),
            "language": language,
            "sources": sources,
            "disclaimer": "Please verify information using official sources."
        }
