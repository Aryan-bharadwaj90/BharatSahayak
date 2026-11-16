
import os
import requests


def test_gemini():
    # Read configuration from environment variables
    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_BASE_URL", "").rstrip("/")
    model = os.getenv("LLM_MODEL")

    # Validate configuration
    if not api_key:
        print("ERROR: LLM_API_KEY is missing.")
        return

    if not base_url:
        print("ERROR: LLM_BASE_URL is missing.")
        return

    if not model:
        print("ERROR: LLM_MODEL is missing.")
        return

    # Build API endpoint
    if base_url.endswith("/chat/completions"):
        url = base_url
    else:
        url = base_url + "/chat/completions"

    print("Testing Gemini API...")
    print("Model:", model)
    print("Endpoint:", base_url)

    # Minimal test request
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": (
                    "Reply with exactly: "
                    "BharatSahayak AI connected successfully."
                )
            }
        ],
        "temperature": 0.2,
        "max_tokens": 150
    }

    try:
        response = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=(15, 120)
        )

        print("\nHTTP STATUS:", response.status_code)

        response.raise_for_status()

        result = response.json()

        answer = (
            result.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
        )

        if not answer:
            print("ERROR: Model returned an empty response.")
            print("Raw response:", result)
            return

        print("\nMODEL RESPONSE:")
        print(answer)

        print("\nGEMINI API TEST PASSED!")

    except requests.exceptions.Timeout:
        print("\nERROR: Gemini request timed out.")
        print("The model did not respond within 120 seconds.")

    except requests.exceptions.HTTPError:
        print("\nHTTP ERROR:", response.status_code)
        print("DETAILS:", response.text[:1500])

    except requests.exceptions.ConnectionError:
        print("\nERROR: Could not connect to Gemini.")
        print("Check your internet connection.")

    except requests.exceptions.RequestException as error:
        print("\nREQUEST ERROR:", str(error))

    except (ValueError, KeyError, IndexError, TypeError) as error:
        print("\nRESPONSE PARSING ERROR:", str(error))


if __name__ == "__main__":
    test_gemini()
