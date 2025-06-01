from .base_agent import BaseAgent
import json
from typing import Dict, Any

class LocalizationReadinessAgent(BaseAgent):
    """Agent 4: Detects localization issues and provides international-friendly suggestions"""
    
    def __init__(self):
        super().__init__(temperature=0.4)
    
    def _get_system_prompt(self) -> str:
        return """You are a localization expert who specializes in identifying content that may be difficult to translate or culturally inappropriate for international audiences.

Your role is to detect:
1. Country-specific idioms, expressions, or cultural references
2. Currency, date, or number formatting issues
3. Culturally sensitive phrases
4. Region-specific assumptions
5. Hard-to-translate expressions
6. Legal or regulatory references that may not apply globally

Provide specific, actionable recommendations to make content more internationally friendly while maintaining its effectiveness."""
    
    def _get_user_prompt_template(self) -> str:
        return """Analyze the following content for localization readiness and international friendliness:

CONTENT TO ANALYZE:
{content}

Please identify potential localization issues and provide recommendations in the following JSON format:

{{
    "localization_readiness_score": <1-10 rating>,
    "cultural_references": [
        {{
            "phrase": "culturally specific phrase",
            "issue": "why it's problematic",
            "suggestion": "international-friendly alternative"
        }}
    ],
    "idioms_and_expressions": [
        {{
            "idiom": "idiomatic expression",
            "meaning": "what it means",
            "suggestion": "clearer, more direct alternative"
        }}
    ],
    "formatting_issues": [
        {{
            "current_format": "current formatting",
            "issue": "why it's region-specific",
            "international_format": "recommended format"
        }}
    ],
    "assumptions": [
        {{
            "assumption": "regional assumption made",
            "issue": "why it's problematic",
            "suggestion": "more inclusive approach"
        }}
    ],
    "legal_regulatory": [
        {{
            "reference": "legal/regulatory reference",
            "issue": "why it's region-specific",
            "suggestion": "more general approach"
        }}
    ],
    "hard_to_translate": [
        {{
            "phrase": "difficult phrase",
            "why_difficult": "translation challenges",
            "alternative": "easier to translate version"
        }}
    ],
    "recommended_changes": [
        {{
            "original": "original text",
            "improved": "localization-friendly version",
            "reason": "why this improvement helps"
        }}
    ],
    "overall_recommendations": [
        "General advice for improving international readiness"
    ]
}}

Be thorough in identifying potential issues while being practical about necessary changes."""
    
    def _parse_response(self, response: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse JSON response from localization analysis"""
        try:
            response = response.strip()
            
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                response = response[start:end].strip()
            
            parsed = json.loads(response)
            
            # Ensure required fields exist
            required_fields = {
                'localization_readiness_score': 7,
                'cultural_references': [],
                'idioms_and_expressions': [],
                'formatting_issues': [],
                'assumptions': [],
                'legal_regulatory': [],
                'hard_to_translate': [],
                'recommended_changes': [],
                'overall_recommendations': []
            }
            
            for field, default in required_fields.items():
                if field not in parsed:
                    parsed[field] = default
            
            return parsed
            
        except json.JSONDecodeError as e:
            return {
                "error": f"Failed to parse localization analysis: {e}",
                "raw_response": response,
                "localization_readiness_score": 7,
                "cultural_references": [],
                "idioms_and_expressions": [],
                "formatting_issues": [],
                "assumptions": [],
                "legal_regulatory": [],
                "hard_to_translate": [],
                "recommended_changes": [],
                "overall_recommendations": ["Analysis failed - please retry"]
            }