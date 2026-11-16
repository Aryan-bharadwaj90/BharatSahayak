
import os
import requests

api_key = os.getenv("LLM_API_KEY")
base_url = os.getenv("LLM_BASE_URL", "").rstrip("/")

if not api_key or not base_url:
    raise ValueError("API key or base URL is missing.")

url = base_url + "/models"

try:
    response = requests.get(
        url,
        headers={
            "Authorization": f"Bearer {api_key}"
        },
        timeout=(10, 30)
    )

    print("HTTP STATUS:", response.status_code)
    response.raise_for_status()

    models = response.json().get("data", [])

    print("\nAVAILABLE FLASH MODELS:")

    for model in models:
        model_id = model.get("id", "")

        if "flash" in model_id.lower():
            print(model_id)

except requests.exceptions.Timeout:
    print("MODEL LIST REQUEST TIMED OUT.")

except requests.exceptions.RequestException as error:
    print("API ERROR:", str(error))
