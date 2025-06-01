from .base_agent import BaseAgent
import textstat
import re
import json
from typing import Dict, Any, List

class ReadabilityVisualizerAgent(BaseAgent):
    """Agent 6: Analyzes and visualizes readability metrics"""
    
    def __init__(self):
        super().__init__(temperature=0.2)
    
    def _get_system_prompt(self) -> str:
        return """You are a readability analysis expert who provides detailed insights into text complexity and accessibility.

Your role is to analyze content using readability metrics and provide clear, actionable feedback about how to improve text accessibility and comprehension.

You understand various readability formulas and can interpret their results to provide practical recommendations."""
    
    def _get_user_prompt_template(self) -> str:
        return """Based on the readability analysis data provided, interpret the results and provide insights:

READABILITY METRICS:
{readability_metrics}

PARAGRAPH SCORES:
{paragraph_scores}

Please provide interpretation and recommendations in the following JSON format:

{{
    "overall_assessment": {{
        "reading_level": "grade level description",
        "accessibility": "how accessible is this content",
        "target_audience": "who can easily read this"
    }},
    "key_insights": [
        "Important findings about readability"
    ],
    "problem_areas": [
        {{
            "issue": "specific readability problem",
            "impact": "how it affects readers",
            "solution": "how to fix it"
        }}
    ],
    "recommendations": [
        "Specific actions to improve readability"
    ],
    "strengths": [
        "What's working well in terms of readability"
    ]
}}

Focus on practical, actionable insights that will help improve the content's accessibility."""
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute readability analysis with textstat calculations"""
        content = input_data.get('content', '')
        
        # Calculate readability metrics
        metrics = self._calculate_readability_metrics(content)
        
        # Analyze paragraphs
        paragraph_scores = self._analyze_paragraphs(content)
        
        # Get AI interpretation
        ai_input = {
            'readability_metrics': json.dumps(metrics, indent=2),
            'paragraph_scores': json.dumps(paragraph_scores, indent=2)
        }
        
        ai_analysis = super().execute(ai_input)
        
        # Combine results
        return {
            'metrics': metrics,
            'paragraph_analysis': paragraph_scores,
            'ai_insights': ai_analysis,
            'visualization_data': self._prepare_visualization_data(paragraph_scores)
        }
    
    def _calculate_readability_metrics(self, content: str) -> Dict[str, Any]:
        """Calculate various readability metrics using textstat"""
        # Clean content for analysis
        clean_content = re.sub(r'[^\w\s\.\!\?]', '', content)
        
        if not clean_content.strip():
            return {"error": "No readable content found"}
        
        try:
            metrics = {
                'flesch_reading_ease': textstat.flesch_reading_ease(clean_content),
                'flesch_kincaid_grade': textstat.flesch_kincaid_grade(clean_content),
                'gunning_fog': textstat.gunning_fog(clean_content),
                'automated_readability_index': textstat.automated_readability_index(clean_content),
                'coleman_liau_index': textstat.coleman_liau_index(clean_content),
                'linsear_write_formula': textstat.linsear_write_formula(clean_content),
                'dale_chall_readability_score': textstat.dale_chall_readability_score(clean_content),
                'text_standard': textstat.text_standard(clean_content),
                'word_count': len(clean_content.split()),
                'sentence_count': textstat.sentence_count(clean_content),
                'avg_sentence_length': textstat.avg_sentence_length(clean_content),
                'syllable_count': textstat.syllable_count(clean_content),
                'avg_syllables_per_word': textstat.avg_syllables_per_word(clean_content)
            }
            
            # Add interpretations
            metrics['readability_level'] = self._interpret_flesch_score(metrics['flesch_reading_ease'])
            metrics['grade_level'] = self._interpret_grade_level(metrics['flesch_kincaid_grade'])
            
            return metrics
            
        except Exception as e:
            return {"error": f"Readability calculation failed: {e}"}
    
    def _analyze_paragraphs(self, content: str) -> List[Dict[str, Any]]:
        """Analyze readability of individual paragraphs"""
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        paragraph_scores = []
        
        for i, paragraph in enumerate(paragraphs):
            if len(paragraph.split()) < 5:  # Skip very short paragraphs
                continue
                
            try:
                flesch_score = textstat.flesch_reading_ease(paragraph)
                grade_level = textstat.flesch_kincaid_grade(paragraph)
                
                # Determine color coding
                color = self._get_readability_color(flesch_score)
                
                paragraph_scores.append({
                    'paragraph_number': i + 1,
                    'text_preview': paragraph[:100] + "..." if len(paragraph) > 100 else paragraph,
                    'flesch_score': flesch_score,
                    'grade_level': grade_level,
                    'color': color,
                    'word_count': len(paragraph.split()),
                    'sentence_count': textstat.sentence_count(paragraph),
                    'readability_level': self._interpret_flesch_score(flesch_score)
                })
                
            except Exception as e:
                paragraph_scores.append({
                    'paragraph_number': i + 1,
                    'text_preview': paragraph[:100] + "...",
                    'error': str(e)
                })
        
        return paragraph_scores
    
    def _interpret_flesch_score(self, score: float) -> str:
        """Interpret Flesch Reading Ease score"""
        if score >= 90:
            return "Very Easy"
        elif score >= 80:
            return "Easy"
        elif score >= 70:
            return "Fairly Easy"
        elif score >= 60:
            return "Standard"
        elif score >= 50:
            return "Fairly Difficult"
        elif score >= 30:
            return "Difficult"
        else:
            return "Very Difficult"
    
    def _interpret_grade_level(self, grade: float) -> str:
        """Interpret grade level score"""
        if grade <= 6:
            return "Elementary School"
        elif grade <= 8:
            return "Middle School"
        elif grade <= 12:
            return "High School"
        elif grade <= 16:
            return "College"
        else:
            return "Graduate Level"
    
    def _get_readability_color(self, flesch_score: float) -> str:
        """Get color coding for readability score"""
        if flesch_score >= 70:
            return "green"  # Easy to read
        elif flesch_score >= 50:
            return "yellow"  # Moderate difficulty
        else:
            return "red"  # Difficult to read
    
    def _prepare_visualization_data(self, paragraph_scores: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Prepare data for visualization"""
        colors = {'green': 0, 'yellow': 0, 'red': 0}
        scores = []
        
        for para in paragraph_scores:
            if 'color' in para:
                colors[para['color']] += 1
                scores.append(para['flesch_score'])
        
        return {
            'color_distribution': colors,
            'score_range': {
                'min': min(scores) if scores else 0,
                'max': max(scores) if scores else 0,
                'avg': sum(scores) / len(scores) if scores else 0
            },
            'total_paragraphs': len(paragraph_scores)
        }