from .base_agent import BaseAgent
import json
from typing import Dict, Any

class DocumentationAnalyzerAgent(BaseAgent):
    """Agent 1: Analyzes documentation for improvement opportunities"""
    
    def __init__(self):
        super().__init__(temperature=0.3)
    
    def _get_system_prompt(self) -> str:
        return """You are an expert documentation analyst with deep knowledge of technical writing, Microsoft style guide, and user experience principles.

Your role is to analyze documentation content and provide structured suggestions for improvement from a marketer's perspective while maintaining technical accuracy.

Focus on:
1. READABILITY: Assess sentence structure, word choice, and flow
2. STRUCTURE: Evaluate headings, organization, and navigation
3. COMPLETENESS: Identify missing explanations or context
4. MICROSOFT STYLE GUIDE: Check adherence to voice, tone, clarity, and conciseness
5. MARKETER'S PERSPECTIVE: Ensure value propositions are clear and benefits are highlighted

You must return a valid JSON response with specific, actionable suggestions."""
    
    def _get_user_prompt_template(self) -> str:
        return """Please analyze the following documentation content and provide structured improvement suggestions:

TITLE: {title}
CONTENT: {content}

Analyze this content and return a JSON response with the following structure:

{{
    "overall_score": <1-10 rating>,
    "readability": {{
        "score": <1-10>,
        "issues": ["list of readability issues"],
        "suggestions": ["specific improvements"]
    }},
    "structure": {{
        "score": <1-10>,
        "issues": ["structural problems"],
        "suggestions": ["structural improvements"]
    }},
    "completeness": {{
        "score": <1-10>,
        "missing_elements": ["what's missing"],
        "suggestions": ["what to add"]
    }},
    "style_guide_adherence": {{
        "score": <1-10>,
        "violations": ["style guide violations"],
        "improvements": ["how to fix them"]
    }},
    "marketing_perspective": {{
        "score": <1-10>,
        "value_clarity": ["are benefits clear?"],
        "call_to_action": ["are next steps obvious?"]
    }},
    "priority_fixes": ["top 3 most important improvements"],
    "detailed_suggestions": [
        {{
            "section": "section name",
            "issue": "specific problem",
            "suggestion": "detailed fix",
            "priority": "high/medium/low"
        }}
    ]
}}

Be specific and actionable in your suggestions. Focus on improvements that will make the documentation more valuable for marketers while maintaining technical accuracy."""
    
    def _parse_response(self, response: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse JSON response from the analyzer"""
        try:
            # Clean the response
            response = response.strip()
            
            # Extract JSON if wrapped in markdown
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                response = response[start:end].strip()
            
            parsed = json.loads(response)
            
            # Validate required fields
            required_fields = ['overall_score', 'readability', 'structure', 'completeness']
            for field in required_fields:
                if field not in parsed:
                    parsed[field] = {"score": 5, "issues": [], "suggestions": []}
            
            return parsed
            
        except json.JSONDecodeError as e:
            return {
                "error": f"Failed to parse JSON response: {e}",
                "raw_response": response,
                "overall_score": 5,
                "readability": {"score": 5, "issues": ["Analysis failed"], "suggestions": []},
                "structure": {"score": 5, "issues": ["Analysis failed"], "suggestions": []},
                "completeness": {"score": 5, "issues": ["Analysis failed"], "suggestions": []},
                "priority_fixes": ["Re-run analysis"]
            }