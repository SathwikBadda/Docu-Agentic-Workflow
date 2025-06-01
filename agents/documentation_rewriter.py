from .base_agent import BaseAgent
from typing import Dict, Any

class DocumentationRewriterAgent(BaseAgent):
    """Agent 2: Rewrites documentation with improvements integrated"""
    
    def __init__(self):
        super().__init__(temperature=0.7)
    
    def _get_system_prompt(self) -> str:
        return """You are an expert technical writer specializing in creating clear, engaging, and effective documentation.

Your role is to rewrite documentation content by integrating all improvement suggestions while preserving the original structure and ensuring natural readability.

Key principles:
1. PRESERVE STRUCTURE: Maintain headings, bullet points, and overall organization
2. NATURAL FLOW: Make improvements feel seamless and natural
3. CLARITY: Simplify complex concepts without losing technical accuracy
4. ENGAGEMENT: Make content more engaging for the target audience
5. COMPLETENESS: Fill in gaps identified in the analysis

Always maintain the technical accuracy while making the content more accessible and valuable."""
    
    def _get_user_prompt_template(self) -> str:
        return """Please rewrite the following documentation content by integrating the provided improvement suggestions:

ORIGINAL TITLE: {title}

ORIGINAL CONTENT:
{content}

IMPROVEMENT SUGGESTIONS:
{suggestions}

Please rewrite the documentation with the following requirements:

1. INTEGRATE ALL SUGGESTIONS: Apply the improvement suggestions naturally
2. PRESERVE STRUCTURE: Keep the same heading hierarchy and organization
3. MAINTAIN ACCURACY: Don't change technical facts or specifications
4. IMPROVE READABILITY: Use clearer language and better flow
5. ADD VALUE: Make benefits and value propositions more apparent
6. FILL GAPS: Address completeness issues identified in the analysis

Return the rewritten content in clean markdown format. Include:
- All original headings (improved if needed)
- All technical information (clarified if needed)
- Better explanations for complex concepts
- Clearer value propositions
- Improved transitions between sections

Focus on making this documentation significantly more valuable and easier to understand while keeping it technically accurate and complete."""
    
    def _parse_response(self, response: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse the rewritten content"""
        # Clean up the response
        response = response.strip()
        
        # Remove markdown code blocks if present
        if response.startswith("```markdown"):
            response = response[11:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        
        return {
            "rewritten_content": response.strip(),
            "word_count": len(response.split()),
            "improvement_applied": True
        }