from .base_agent import BaseAgent
import json
from typing import Dict, Any

class PersonaFeedbackAgent(BaseAgent):
    """Agent 3: Provides persona-based feedback and adaptations"""
    
    def __init__(self):
        super().__init__(temperature=0.6)
    
    def _get_system_prompt(self) -> str:
        return """You are a user experience expert who specializes in adapting content for different professional personas.

Your role is to analyze content from a specific persona's perspective and provide targeted suggestions to make it more relevant and valuable for that user type.

You understand how different professionals (Marketers, Developers, Product Managers) consume information differently and what they prioritize when reading documentation.

Provide specific, actionable feedback that will make the content more effective for the target persona."""
    
    def _get_user_prompt_template(self) -> str:
        return """Analyze the following content from the perspective of a {persona} and provide persona-specific feedback:

PERSONA: {persona}
PERSONA DESCRIPTION: {persona_description}
PERSONA PRIORITIES: {persona_priorities}

CONTENT TO ANALYZE:
{content}

Please provide feedback in the following JSON format:

{{
    "persona_alignment_score": <1-10 rating>,
    "persona_specific_issues": [
        "List of issues specific to this persona's needs"
    ],
    "terminology_adjustments": [
        {{
            "current_term": "existing term",
            "suggested_term": "better term for this persona",
            "reason": "why this change helps"
        }}
    ],
    "tone_adjustments": [
        "Specific tone changes needed for this persona"
    ],
    "content_emphasis": [
        "What aspects should be emphasized more for this persona"
    ],
    "missing_elements": [
        "What this persona would expect to see but is missing"
    ],
    "sample_rewrites": [
        {{
            "original_paragraph": "original text",
            "rewritten_paragraph": "improved version for this persona",
            "explanation": "why this works better"
        }}
    ],
    "call_to_action_suggestions": [
        "Specific next steps that would appeal to this persona"
    ]
}}

Focus on making the content more valuable and actionable for the specific persona while maintaining accuracy."""
    
    def _parse_response(self, response: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse JSON response from persona analysis"""
        try:
            response = response.strip()
            
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                response = response[start:end].strip()
            
            parsed = json.loads(response)
            
            # Ensure required fields exist
            required_fields = {
                'persona_alignment_score': 5,
                'persona_specific_issues': [],
                'terminology_adjustments': [],
                'tone_adjustments': [],
                'content_emphasis': [],
                'missing_elements': [],
                'sample_rewrites': [],
                'call_to_action_suggestions': []
            }
            
            for field, default in required_fields.items():
                if field not in parsed:
                    parsed[field] = default
            
            return parsed
            
        except json.JSONDecodeError as e:
            return {
                "error": f"Failed to parse persona feedback: {e}",
                "raw_response": response,
                "persona_alignment_score": 5,
                "persona_specific_issues": ["Analysis failed - please retry"],
                "terminology_adjustments": [],
                "tone_adjustments": [],
                "content_emphasis": [],
                "missing_elements": [],
                "sample_rewrites": [],
                "call_to_action_suggestions": []
            }