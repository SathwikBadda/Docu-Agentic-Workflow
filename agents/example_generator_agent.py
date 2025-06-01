from .base_agent import BaseAgent
import json
from typing import Dict, Any

class ExampleGeneratorAgent(BaseAgent):
    """Agent 5: Generates intelligent, contextual examples for documentation"""
    
    def __init__(self):
        super().__init__(temperature=0.8)
    
    def _get_system_prompt(self) -> str:
        return """You are a technical writing expert who specializes in creating relevant, realistic examples that enhance understanding.

Your role is to:
1. Identify sections that would benefit from examples
2. Generate contextually appropriate examples
3. Create examples that are realistic and relatable
4. Ensure examples align with the documentation's purpose
5. Make examples that clarify complex concepts

Your examples should be:
- Realistic and practical
- Easy to understand
- Directly related to the concept being explained
- Properly formatted for the documentation context
- Helpful for the target audience"""
    
    def _get_user_prompt_template(self) -> str:
        return """Analyze the following content and generate relevant examples where they would enhance understanding:

CONTENT TO ANALYZE:
{content}

DOCUMENT CONTEXT: {title}

Please identify sections that need examples and generate appropriate ones in the following JSON format:

{{
    "sections_needing_examples": [
        {{
            "section_title": "name of section",
            "reason": "why an example would help",
            "complexity_level": "beginner/intermediate/advanced"
        }}
    ],
    "generated_examples": [
        {{
            "section": "section where this example belongs",
            "example_type": "code/scenario/use_case/walkthrough",
            "title": "example title",
            "content": "the actual example content",
            "explanation": "brief explanation of the example",
            "placement_suggestion": "where in the section to insert this"
        }}
    ],
    "code_examples": [
        {{
            "section": "relevant section",
            "language": "programming language if applicable",
            "code": "actual code example",
            "description": "what this code does",
            "comments": "inline comments for clarity"
        }}
    ],
    "scenario_examples": [
        {{
            "section": "relevant section",
            "scenario": "realistic scenario description",
            "step_by_step": ["step 1", "step 2", "step 3"],
            "outcome": "expected result"
        }}
    ],
    "integration_notes": [
        "Notes on how to best integrate these examples into the content"
    ]
}}

Focus on creating examples that make abstract concepts concrete and help readers understand practical applications."""
    
    def _parse_response(self, response: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse JSON response from example generation"""
        try:
            response = response.strip()
            
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                response = response[start:end].strip()
            
            parsed = json.loads(response)
            
            # Ensure required fields exist
            required_fields = {
                'sections_needing_examples': [],
                'generated_examples': [],
                'code_examples': [],
                'scenario_examples': [],
                'integration_notes': []
            }
            
            for field, default in required_fields.items():
                if field not in parsed:
                    parsed[field] = default
            
            return parsed
            
        except json.JSONDecodeError as e:
            return {
                "error": f"Failed to parse example generation: {e}",
                "raw_response": response,
                "sections_needing_examples": [],
                "generated_examples": [],
                "code_examples": [],
                "scenario_examples": [],
                "integration_notes": ["Analysis failed - please retry"]
            }