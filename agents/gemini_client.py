import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))  # Project root

import google.generativeai as genai
import time
import json
from config.config import GEMINI_API_KEY  # Now works
from typing import Dict, Any, List

class GeminiClient:
    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY missing in .env")
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.5-flash-lite')  # Or 'gemini-1.5-flash' for speed

    def generate_content(self, prompt: str, system_instruction: str = "", max_retries: int = 3) -> str:
        """Robust content generation with retries."""
        full_prompt = f"{system_instruction}\n\nUser: {prompt}" if system_instruction else prompt
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(full_prompt, generation_config={"temperature": 0.1})
                if response.text:
                    return response.text.strip()
                else:
                    raise ValueError("Empty response")
            except Exception as e:
                print(f"Gemini attempt {attempt+1} failed: {e}")
                if attempt == max_retries - 1:
                    return f"Error: {str(e)}"  # Graceful fallback
                time.sleep(2 ** attempt)  # Exponential backoff

    def generate_structured(self, prompt: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """JSON mode for structured output (e.g., skills list)."""
        system = f"Respond ONLY with valid JSON matching schema: {json.dumps(schema)}."
        response = self.generate_content(prompt, system)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON", "raw": response}

# Singleton instance
client = GeminiClient()

def test_client():
    """Test function."""
    result = client.generate_content("Say 'Gemini ready!'")
    print(result)
    print("Gemini ready")

if __name__ == "__main__":
    test_client()
