import requests


class AIEngine:
    def __init__(self, api_key: str, base_url: str = "https://generativelanguage.googleapis.com/v1beta"):
        self._api_key = api_key
        self._base_url = base_url

    def generate(self, prompt: str, model_name: str = "gemini-2.5-flash") -> str:
        """Call Gemini API and return text output only."""
        url = self._base_url + f"/models/{model_name}:generateContent?key=" + self._api_key

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 8192
            }
        }

        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=120)
            response.raise_for_status()
            data = response.json()
            candidates = data.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                if parts:
                    return {
                        "success": True,
                        "content": parts[0].get("text", "No response generated.")
                    }
            return {
                "success": False,
                "error": "AI request failed. Please check your connection."
            }
        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                return {
                    "success": False,
                    "error": "Rate limit exceeded. Please try again later."
                }
            return {
                "success": False,
                "error": "AI request failed. Please check your connection."
            }
        except Exception as e:
            return {
                "success": False,
                "error": "AI request failed. Please check your connection."
            }
