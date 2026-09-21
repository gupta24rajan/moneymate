import json
import re
from typing import Dict, Any
from ai.foundation.llm_client import LLMClient

class CategorizationService:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    def extract_merchant(self, description: str) -> str:
        clean_text = re.sub(r'₹|\d+|rs|paytm|upi|pos', '', description, flags=re.IGNORECASE)
        words = clean_text.strip().split()
        return words[0].capitalize() if words else "Unknown"

    async def suggest_category(self, description: str, amount: float) -> Dict[str, Any]:
        merchant = self.extract_merchant(description)
        
        prompt = f"""
You are a financial classifier. Analyze the expense and return ONLY a raw JSON object without any Markdown formatting or code blocks.

Expense Description: "{description}"
Amount: {amount}
Extracted Merchant: "{merchant}"

Return this exact JSON structure:
{{
    "suggested_category": "Food",
    "subcategory": "Food Delivery",
    "merchant": "{merchant}",
    "confidence": 0.95
}}
"""

        try:
            raw_response = await self.llm_client.generate(prompt)
            
            # Clean markdown wrappers if returned by LLM
            cleaned_json = raw_response.strip()
            if cleaned_json.startswith("```"):
                cleaned_json = re.sub(r"^```(?:json)?|```$", "", cleaned_json, flags=re.MULTILINE).strip()

            data = json.loads(cleaned_json)
            return data
            
        except Exception as err:
            # Fallback response so API doesn't crash with 500 Error
            return {
                "suggested_category": "Other",
                "subcategory": "General",
                "merchant": merchant,
                "confidence": 0.50
            }

    async def accept_suggestion(self, expense_id: int, category_id: int) -> bool:
        return True

categorization_service = CategorizationService(LLMClient())