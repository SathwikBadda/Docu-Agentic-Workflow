from typing import Dict, Any, List
import json
from datetime import datetime

# Import agents directly to avoid circular imports
from agents.documentation_analyzer import DocumentationAnalyzerAgent
from agents.documentation_rewriter import DocumentationRewriterAgent
from agents.persona_feedback_agent import PersonaFeedbackAgent
from agents.localization_agent import LocalizationReadinessAgent
from agents.example_generator_agent import ExampleGeneratorAgent
from agents.readability_visualizer import ReadabilityVisualizerAgent
from config import PERSONAS

class AgentOrchestrator:
    """Orchestrates the execution of all documentation improvement agents"""
    
    def __init__(self):
        self.agents = {
            'analyzer': DocumentationAnalyzerAgent(),
            'rewriter': DocumentationRewriterAgent(),
            'persona': PersonaFeedbackAgent(),
            'localization': LocalizationReadinessAgent(),
            'example_generator': ExampleGeneratorAgent(),
            'readability': ReadabilityVisualizerAgent()
        }
        
        self.execution_log = []
    
    def process_documentation(self, content_data: Dict[str, Any], persona: str = "Marketer") -> Dict[str, Any]:
        """
        Process documentation through all agents in the correct sequence
        
        Args:
            content_data: Dictionary containing title, content, url, etc.
            persona: Target persona for analysis
            
        Returns:
            Dictionary with all agent results
        """
        results = {
            'input_data': content_data,
            'persona': persona,
            'timestamp': datetime.now().isoformat(),
            'agent_results': {},
            'execution_log': [],
            'final_output': {}
        }
        
        try:
            # Validate input data
            if not content_data or not content_data.get('text'):
                results['error'] = "No content provided for analysis"
                return results
            # Step 1: Analyze documentation
            self._log_step(results, "Starting documentation analysis...")
            analyzer_input = {
                'title': content_data.get('title', ''),
                'content': content_data.get('text', '')
            }
            
            analysis_result = self.agents['analyzer'].execute(analyzer_input)
            results['agent_results']['analysis'] = analysis_result
            self._log_step(results, "✓ Documentation analysis completed")
            
            # Check if analysis failed
            if 'error' in analysis_result:
                results['error'] = f"Analysis failed: {analysis_result['error']}"
                return results
            
            # Step 2: Generate readability analysis
            self._log_step(results, "Analyzing readability metrics...")
            readability_input = {
                'content': content_data.get('text', '')
            }
            
            readability_result = self.agents['readability'].execute(readability_input)
            results['agent_results']['readability'] = readability_result
            self._log_step(results, "✓ Readability analysis completed")
            
            # Step 3: Rewrite documentation with improvements
            self._log_step(results, "Rewriting documentation with improvements...")
            rewriter_input = {
                'title': content_data.get('title', ''),
                'content': content_data.get('text', ''),
                'suggestions': json.dumps(analysis_result, indent=2)
            }
            
            rewrite_result = self.agents['rewriter'].execute(rewriter_input)
            results['agent_results']['rewrite'] = rewrite_result
            self._log_step(results, "✓ Documentation rewrite completed")
            
            # Step 4: Generate persona-specific feedback
            self._log_step(results, f"Generating {persona}-specific feedback...")
            persona_config = PERSONAS.get(persona, PERSONAS['Marketer'])
            persona_input = {
                'content': rewrite_result.get('rewritten_content', content_data.get('text', '')),
                'persona': persona,
                'persona_description': persona_config['description'],
                'persona_priorities': ', '.join(persona_config['priorities'])
            }
            
            persona_result = self.agents['persona'].execute(persona_input)
            results['agent_results']['persona_feedback'] = persona_result
            self._log_step(results, f"✓ {persona} persona analysis completed")
            
            # Step 5: Check localization readiness
            self._log_step(results, "Analyzing localization readiness...")
            localization_input = {
                'content': rewrite_result.get('rewritten_content', content_data.get('text', ''))
            }
            
            localization_result = self.agents['localization'].execute(localization_input)
            results['agent_results']['localization'] = localization_result
            self._log_step(results, "✓ Localization analysis completed")
            
            # Step 6: Generate intelligent examples
            self._log_step(results, "Generating intelligent examples...")
            example_input = {
                'content': rewrite_result.get('rewritten_content', content_data.get('text', '')),
                'title': content_data.get('title', '')
            }
            
            example_result = self.agents['example_generator'].execute(example_input)
            results['agent_results']['examples'] = example_result
            self._log_step(results, "✓ Example generation completed")
            
            # Step 7: Prepare final output
            self._log_step(results, "Preparing final output...")
            try:
                results['final_output'] = self._prepare_final_output(results)
                self._log_step(results, "✓ All processing completed successfully!")
            except Exception as e:
                self._log_step(results, f"⚠️ Final output preparation had issues: {e}")
                # Ensure final_output exists even if preparation fails
                results['final_output'] = {
                    'final_content': results.get('agent_results', {}).get('rewrite', {}).get('rewritten_content', ''),
                    'improvement_summary': ['Analysis completed with some processing issues'],
                    'scores': {'overall': 5.0},
                    'recommendations': ['Review the analysis results in the detailed tabs'],
                    'word_count_change': {'original': 0, 'final': 0, 'change': 0}
                }
            
            return results
            
        except Exception as e:
            error_msg = f"Error during processing: {str(e)}"
            self._log_step(results, f"❌ {error_msg}")
            results['error'] = error_msg
            return results
    
    def _log_step(self, results: Dict[str, Any], message: str):
        """Log a processing step"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'message': message
        }
        results['execution_log'].append(log_entry)
        self.execution_log.append(log_entry)
    
    def _prepare_final_output(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare the final consolidated output"""
        agent_results = results.get('agent_results', {})
        
        # Get the main rewritten content
        rewritten_content = agent_results.get('rewrite', {}).get('rewritten_content', '')
        
        # Integrate examples into content
        final_content = self._integrate_examples(
            rewritten_content,
            agent_results.get('examples', {})
        )
        
        # Apply persona-specific improvements
        final_content = self._apply_persona_improvements(
            final_content,
            agent_results.get('persona_feedback', {})
        )
        
        return {
            'final_content': final_content,
            'improvement_summary': self._create_improvement_summary(agent_results),
            'scores': self._extract_scores(agent_results),
            'recommendations': self._consolidate_recommendations(agent_results),
            'word_count_change': self._calculate_word_count_change(results),
            'readability_improvement': self._assess_readability_improvement(agent_results)
        }
    
    def _integrate_examples(self, content: str, examples_data: Dict[str, Any]) -> str:
        """Integrate generated examples into the content"""
        if not examples_data or 'generated_examples' not in examples_data:
            return content
        
        # For now, append examples at the end of relevant sections
        # In a more sophisticated version, this would insert examples inline
        examples = examples_data.get('generated_examples', [])
        
        for example in examples:
            if example.get('content'):
                content += f"\n\n### Example: {example.get('title', 'Untitled')}\n\n"
                content += example.get('content', '')
                if example.get('explanation'):
                    content += f"\n\n*{example.get('explanation')}*"
        
        return content
    
    def _apply_persona_improvements(self, content: str, persona_data: Dict[str, Any]) -> str:
        """Apply persona-specific improvements to content"""
        if not persona_data or 'sample_rewrites' not in persona_data:
            return content
        
        # Apply sample rewrites
        rewrites = persona_data.get('sample_rewrites', [])
        for rewrite in rewrites:
            original = rewrite.get('original_paragraph', '')
            improved = rewrite.get('rewritten_paragraph', '')
            if original and improved and original in content:
                content = content.replace(original, improved)
        
        return content
    
    def _create_improvement_summary(self, agent_results: Dict[str, Any]) -> List[str]:
        """Create a summary of improvements made"""
        summary = []
        
        # Analysis improvements
        analysis = agent_results.get('analysis', {})
        if analysis.get('priority_fixes'):
            summary.extend([f"Fixed: {fix}" for fix in analysis.get('priority_fixes', [])])
        
        # Persona improvements
        persona = agent_results.get('persona_feedback', {})
        if persona.get('persona_specific_issues'):
            summary.append(f"Addressed {len(persona.get('persona_specific_issues', []))} persona-specific issues")
        
        # Localization improvements
        localization = agent_results.get('localization', {})
        if localization.get('recommended_changes'):
            summary.append(f"Applied {len(localization.get('recommended_changes', []))} localization improvements")
        
        # Examples added
        examples = agent_results.get('examples', {})
        if examples.get('generated_examples'):
            summary.append(f"Added {len(examples.get('generated_examples', []))} helpful examples")
        
        return summary if summary else ["Content improved for clarity and readability"]
    
    def _extract_scores(self, agent_results: Dict[str, Any]) -> Dict[str, float]:
        """Extract numerical scores from all agents"""
        scores = {}
        
        # Analysis scores
        analysis = agent_results.get('analysis', {})
        scores['overall'] = analysis.get('overall_score', 5.0)
        scores['readability'] = analysis.get('readability', {}).get('score', 5.0)
        scores['structure'] = analysis.get('structure', {}).get('score', 5.0)
        scores['completeness'] = analysis.get('completeness', {}).get('score', 5.0)
        
        # Persona alignment
        persona = agent_results.get('persona_feedback', {})
        scores['persona_alignment'] = persona.get('persona_alignment_score', 5.0)
        
        # Localization readiness
        localization = agent_results.get('localization', {})
        scores['localization_readiness'] = localization.get('localization_readiness_score', 7.0)
        
        # Readability metrics
        readability = agent_results.get('readability', {})
        if readability.get('metrics'):
            scores['flesch_reading_ease'] = readability['metrics'].get('flesch_reading_ease', 50.0)
            scores['grade_level'] = readability['metrics'].get('flesch_kincaid_grade', 10.0)
        
        return scores
    
    def _consolidate_recommendations(self, agent_results: Dict[str, Any]) -> List[str]:
        """Consolidate recommendations from all agents"""
        recommendations = []
        
        # From analysis
        analysis = agent_results.get('analysis', {})
        if analysis.get('detailed_suggestions'):
            for suggestion in analysis.get('detailed_suggestions', []):
                if suggestion.get('priority') == 'high':
                    recommendations.append(suggestion.get('suggestion', ''))
        
        # From persona feedback
        persona = agent_results.get('persona_feedback', {})
        recommendations.extend(persona.get('call_to_action_suggestions', []))
        
        # From localization
        localization = agent_results.get('localization', {})
        recommendations.extend(localization.get('overall_recommendations', []))
        
        # From readability
        readability = agent_results.get('readability', {})
        if readability.get('ai_insights', {}).get('recommendations'):
            recommendations.extend(readability['ai_insights'].get('recommendations', []))
        
        return list(set(recommendations))  # Remove duplicates
    
    def _calculate_word_count_change(self, results: Dict[str, Any]) -> Dict[str, int]:
        """Calculate word count changes"""
        original_count = results.get('input_data', {}).get('word_count', 0)
        
        rewrite_result = results.get('agent_results', {}).get('rewrite', {})
        new_count = rewrite_result.get('word_count', original_count)
        
        return {
            'original': original_count,
            'final': new_count,
            'change': new_count - original_count,
            'percentage_change': ((new_count - original_count) / original_count * 100) if original_count > 0 else 0
        }
    
    def _assess_readability_improvement(self, agent_results: Dict[str, Any]) -> Dict[str, Any]:
        """Assess readability improvements"""
        readability = agent_results.get('readability', {})
        
        if not readability.get('metrics'):
            return {"status": "No readability analysis available"}
        
        metrics = readability['metrics']
        
        return {
            'flesch_reading_ease': metrics.get('flesch_reading_ease', 50),
            'grade_level': metrics.get('flesch_kincaid_grade', 10),
            'readability_level': metrics.get('readability_level', 'Standard'),
            'text_standard': metrics.get('text_standard', 'Unknown'),
            'paragraph_distribution': readability.get('visualization_data', {}).get('color_distribution', {})
        }