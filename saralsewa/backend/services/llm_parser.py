import json
import httpx
import asyncio
from fastapi import HTTPException

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "gemma3:4b"

PROMPT_TEMPLATE = """
Extract information from the following user message and output **only** a valid JSON object. 
Do not include any explanations, greetings, or markdown formatting outside of the JSON object.

The JSON object must restrict its values based on these rules:
- "age": An integer (or null if not found)
- "income": An integer (or null if not found)
- "occupation": Must be exactly one of: "farmer", "student", "unemployed", "salaried", "self-employed". Use null if not found.
- "gender": A string (or null if not found)
- "state": A string representing the state name (or null if not found)
- "documents": A list of strings. Each string must be exactly one of: "aadhaar", "bpl_card", "bank_account", "land_records", "pan_card", "income_certificate", "caste_certificate", "ration_card". Omit items that do not match. Use an empty list [] if none found.

User message:
"{message}"
"""

async def parse_user_profile(message: str) -> dict:
    prompt = PROMPT_TEMPLATE.format(message=message)
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(OLLAMA_URL, json=payload, timeout=30.0)
            response.raise_for_status()
            data = response.json()
            
            raw_text = data.get("response", "").strip()

            # Ensure we strip markdown code fences if Ollama wraps the output
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            elif raw_text.startswith("```"):
                raw_text = raw_text[3:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]
            
            raw_text = raw_text.strip()
            
            extracted_data = json.loads(raw_text)
            
    except (httpx.RequestError, httpx.HTTPStatusError, json.JSONDecodeError, ValueError) as e:
        # Catch network, HTTP, and JSON parsing errors to surface a 503
        raise HTTPException(
            status_code=503, 
            detail=f"LLM service unavailable: {str(e)}"
        )

    # 4. Apply null-safe fallbacks
    return {
        "age": extracted_data.get("age", None),
        "income": extracted_data.get("income", None),
        "occupation": extracted_data.get("occupation") or "unemployed",
        "gender": extracted_data.get("gender") or "other",
        "state": extracted_data.get("state", None),
        "documents": extracted_data.get("documents") or []
    }

def parse_user_profile_sync(message: str) -> dict:
    """Synchronous wrapper for use in tests"""
    return asyncio.run(parse_user_profile(message))
