import os
import json
import urllib.request
import urllib.error

class GeminiClient:
    """
    Direct REST API Client for Gemini 3.1 Pro.
    Bypasses the AGY CLI to completely eliminate UI chat pollution and fork-bomb risks.
    """
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables.")
        self.url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-pro-preview:generateContent?key={self.api_key}"

    def generate_content(self, prompt: str) -> str:
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(self.url, data=data, headers=headers, method='POST')
        
        try:
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result['candidates'][0]['content']['parts'][0]['text']
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            raise Exception(f"Gemini API Error: {e.code} - {error_body}")
        except Exception as e:
            raise Exception(f"Failed to communicate with Gemini API: {e}")
