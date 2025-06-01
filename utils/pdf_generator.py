import markdown
from weasyprint import HTML, CSS
from datetime import datetime
import tempfile
import os
from typing import Dict, Any

class PDFGenerator:
    """Generates PDF reports from processed documentation"""
    
    def __init__(self):
        self.css_styles = """
        @page {
            margin: 1in;
            @top-center {
                content: "Documentation Improvement Report";
                font-size: 10pt;
                color: #666;
            }
            @bottom-center {
                content: "Page " counter(page) " of " counter(pages);
                font-size: 10pt;
                color: #666;
            }
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            border-bottom: 2px solid #4CAF50;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }
        
        .header h1 {
            color: #4CAF50;
            margin-bottom: 10px;
        }
        
        .metadata {
            background-color: #f5f5f5;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 25px;
        }
        
        .section {
            margin-bottom: 30px;
            page-break-inside: avoid;
        }
        
        .section h2 {
            color: #2196F3;
            border-bottom: 1px solid #2196F3;
            padding-bottom: 5px;
        }
        
        .section h3 {
            color: #FF9800;
            margin-top: 20px;
        }
        
        .score-box {
            display: inline-block;
            background-color: #e3f2fd;
            padding: 8px 15px;
            border-radius: 20px;
            margin: 5px;
            font-weight: bold;
        }
        
        .score-high { background-color: #c8e6c9; color: #2e7d32; }
        .score-medium { background-color: #fff3e0; color: #f57c00; }
        .score-low { background-color: #ffcdd2; color: #c62828; }
        
        .improvement-list {
            background-color: #f8f9fa;
            padding: 15px;
            border-left: 4px solid #4CAF50;
            margin: 15px 0;
        }
        
        .recommendation {
            background-color: #e8f5e8;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
            border-left: 3px solid #4CAF50;
        }
        
        .content-section {
            background-color: #fafafa;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
        }
        
        .readability-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 5px;
        }
        
        .green { background-color: #4CAF50; }
        .yellow { background-color: #FFC107; }
        .red { background-color: #F44336; }
        
        pre, code {
            background-color: #f4f4f4;
            padding: 10px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }
        
        .page-break {
            page-break-before: always;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }
        
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        
        th {
            background-color: #f2f2f2;
            font-weight: bold;
        }
        """
    
    def generate_pdf(self, results: Dict[str, Any], output_path: str = None) -> str:
        """Generate PDF report from processing results"""
        
        # Generate HTML content
        html_content = self._generate_html_report(results)
        
        # Create temporary file if no output path specified
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"documentation_report_{timestamp}.pdf"
        
        try:
            # Generate PDF
            HTML(string=html_content).write_pdf(
                output_path,
                stylesheets=[CSS(string=self.css_styles)]
            )
            
            return output_path
            
        except Exception as e:
            raise Exception(f"PDF generation failed: {str(e)}")
    
    def _generate_html_report(self, results: Dict[str, Any]) -> str:
        """Generate HTML content for the report"""
        
        input_data = results.get('input_data', {})
        final_output = results.get('final_output', {})
        agent_results = results.get('agent_results', {})
        
        # Start building HTML
        html_parts = []
        
        # Header
        html_parts.append(self._generate_header(input_data, results))
        
        # Executive Summary
        html_parts.append(self._generate_executive_summary(final_output))
        
        # Scores Dashboard
        html_parts.append(self._generate_scores_dashboard(final_output.get('scores', {})))
        
        # Improvement Summary
        html_parts.append(self._generate_improvement_summary(final_output))
        
        # Final Content (page break)
        html_parts.append('<div class="page-break"></div>')
        html_parts.append(self._generate_final_content(final_output))
        
        # Detailed Analysis (page break)
        html_parts.append('<div class="page-break"></div>')
        html_parts.append(self._generate_detailed_analysis(agent_results))
        
        # Recommendations
        html_parts.append(self._generate_recommendations(final_output))
        
        # Readability Analysis
        html_parts.append(self._generate_readability_analysis(agent_results.get('readability', {})))
        
        # Combine all parts
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Documentation Improvement Report</title>
        </head>
        <body>
            {''.join(html_parts)}
        </body>
        </html>
        """
        
        return full_html
    
    def _generate_header(self, input_data: Dict[str, Any], results: Dict[str, Any]) -> str:
        """Generate report header"""
        title = input_data.get('title', 'Untitled Document')
        url = input_data.get('url', 'No URL provided')
        timestamp = results.get('timestamp', datetime.now().isoformat())
        persona = results.get('persona', 'Unknown')
        
        return f"""
        <div class="header">
            <h1>📚 Documentation Improvement Report</h1>
            <div class="metadata">
                <p><strong>Document:</strong> {title}</p>
                <p><strong>Source:</strong> {url}</p>
                <p><strong>Analysis Date:</strong> {timestamp}</p>
                <p><strong>Target Persona:</strong> {persona}</p>
            </div>
        </div>
        """
    
    def _generate_executive_summary(self, final_output: Dict[str, Any]) -> str:
        """Generate executive summary"""
        improvements = final_output.get('improvement_summary', [])
        word_count = final_output.get('word_count_change', {})
        
        return f"""
        <div class="section">
            <h2>📊 Executive Summary</h2>
            <div class="improvement-list">
                <h3>Key Improvements Made:</h3>
                <ul>
                    {chr(10).join([f'<li>{improvement}</li>' for improvement in improvements])}
                </ul>
            </div>
            
            <h3>Content Statistics:</h3>
            <ul>
                <li><strong>Original Word Count:</strong> {word_count.get('original', 0)}</li>
                <li><strong>Final Word Count:</strong> {word_count.get('final', 0)}</li>
                <li><strong>Change:</strong> {word_count.get('change', 0):+d} words ({word_count.get('percentage_change', 0):.1f}%)</li>
            </ul>
        </div>
        """
    
    def _generate_scores_dashboard(self, scores: Dict[str, float]) -> str:
        """Generate scores dashboard"""
        score_boxes = []
        
        for metric, score in scores.items():
            if isinstance(score, (int, float)):
                # Determine score class
                if score >= 8:
                    score_class = "score-high"
                elif score >= 6:
                    score_class = "score-medium"
                else:
                    score_class = "score-low"
                
                # Format metric name
                display_name = metric.replace('_', ' ').title()
                
                score_boxes.append(f"""
                <div class="score-box {score_class}">
                    {display_name}: {score:.1f}/10
                </div>
                """)
        
        return f"""
        <div class="section">
            <h2>📈 Quality Scores</h2>
            <div style="text-align: center;">
                {''.join(score_boxes)}
            </div>
        </div>
        """
    
    def _generate_improvement_summary(self, final_output: Dict[str, Any]) -> str:
        """Generate improvement summary section"""
        readability = final_output.get('readability_improvement', {})
        
        return f"""
        <div class="section">
            <h2>🔧 Improvement Analysis</h2>
            
            <h3>Readability Enhancement:</h3>
            <ul>
                <li><strong>Reading Level:</strong> {readability.get('readability_level', 'Unknown')}</li>
                <li><strong>Grade Level:</strong> {readability.get('grade_level', 'Unknown')}</li>
                <li><strong>Flesch Reading Ease:</strong> {readability.get('flesch_reading_ease', 'Unknown')}</li>
                <li><strong>Text Standard:</strong> {readability.get('text_standard', 'Unknown')}</li>
            </ul>
            
            <h3>Paragraph Readability Distribution:</h3>
            <div>
                {self._format_readability_distribution(readability.get('paragraph_distribution', {}))}
            </div>
        </div>
        """
    
    def _format_readability_distribution(self, distribution: Dict[str, int]) -> str:
        """Format readability distribution"""
        total = sum(distribution.values()) if distribution else 0
        if total == 0:
            return "<p>No readability data available</p>"
        
        return f"""
        <p>
            <span class="readability-indicator green"></span> Easy to Read: {distribution.get('green', 0)} paragraphs ({distribution.get('green', 0)/total*100:.1f}%)<br>
            <span class="readability-indicator yellow"></span> Moderate Difficulty: {distribution.get('yellow', 0)} paragraphs ({distribution.get('yellow', 0)/total*100:.1f}%)<br>
            <span class="readability-indicator red"></span> Difficult to Read: {distribution.get('red', 0)} paragraphs ({distribution.get('red', 0)/total*100:.1f}%)
        </p>
        """
    
    def _generate_final_content(self, final_output: Dict[str, Any]) -> str:
        """Generate final content section"""
        content = final_output.get('final_content', 'No content available')
        
        # Convert markdown to HTML
        html_content = markdown.markdown(content, extensions=['tables', 'fenced_code'])
        
        return f"""
        <div class="section">
            <h2>📝 Improved Documentation</h2>
            <div class="content-section">
                {html_content}
            </div>
        </div>
        """
    
    def _generate_detailed_analysis(self, agent_results: Dict[str, Any]) -> str:
        """Generate detailed analysis from all agents"""
        html_parts = ["""
        <div class="section">
            <h2>🔍 Detailed Analysis</h2>
        """]
        
        # Analysis Results
        analysis = agent_results.get('analysis', {})
        if analysis:
            html_parts.append(self._format_analysis_section(analysis))
        
        # Persona Feedback
        persona = agent_results.get('persona_feedback', {})
        if persona:
            html_parts.append(self._format_persona_section(persona))
        
        # Localization Analysis
        localization = agent_results.get('localization', {})
        if localization:
            html_parts.append(self._format_localization_section(localization))
        
        # Examples
        examples = agent_results.get('examples', {})
        if examples:
            html_parts.append(self._format_examples_section(examples))
        
        html_parts.append("</div>")
        
        return ''.join(html_parts)
    
    def _format_analysis_section(self, analysis: Dict[str, Any]) -> str:
        """Format analysis results"""
        priority_fixes = analysis.get('priority_fixes', [])
        detailed_suggestions = analysis.get('detailed_suggestions', [])
        
        suggestions_html = ""
        for suggestion in detailed_suggestions[:5]:  # Limit to top 5
            priority = suggestion.get('priority', 'medium')
            suggestions_html += f"""
            <div class="recommendation">
                <strong>{suggestion.get('section', 'General')}:</strong> {suggestion.get('suggestion', '')}
                <br><small><em>Priority: {priority}</em></small>
            </div>
            """
        
        return f"""
        <h3>📋 Analysis Findings</h3>
        <h4>Priority Fixes:</h4>
        <ul>
            {chr(10).join([f'<li>{fix}</li>' for fix in priority_fixes])}
        </ul>
        
        <h4>Detailed Suggestions:</h4>
        {suggestions_html}
        """
    
    def _format_persona_section(self, persona: Dict[str, Any]) -> str:
        """Format persona feedback"""
        issues = persona.get('persona_specific_issues', [])
        improvements = persona.get('content_emphasis', [])
        
        return f"""
        <h3>👤 Persona-Specific Analysis</h3>
        <h4>Issues Identified:</h4>
        <ul>
            {chr(10).join([f'<li>{issue}</li>' for issue in issues[:5]])}
        </ul>
        
        <h4>Content Emphasis Recommendations:</h4>
        <ul>
            {chr(10).join([f'<li>{improvement}</li>' for improvement in improvements[:5]])}
        </ul>
        """
    
    def _format_localization_section(self, localization: Dict[str, Any]) -> str:
        """Format localization analysis"""
        score = localization.get('localization_readiness_score', 0)
        issues = localization.get('cultural_references', [])
        recommendations = localization.get('overall_recommendations', [])
        
        return f"""
        <h3>🌍 Localization Analysis</h3>
        <p><strong>Readiness Score:</strong> {score}/10</p>
        
        <h4>Cultural Issues Found:</h4>
        <ul>
            {chr(10).join([f'<li>{issue.get("phrase", "")}: {issue.get("suggestion", "")}</li>' for issue in issues[:3]])}
        </ul>
        
        <h4>Recommendations:</h4>
        <ul>
            {chr(10).join([f'<li>{rec}</li>' for rec in recommendations[:3]])}
        </ul>
        """
    
    def _format_examples_section(self, examples: Dict[str, Any]) -> str:
        """Format examples analysis"""
        generated = examples.get('generated_examples', [])
        
        examples_html = ""
        for example in generated[:3]:  # Limit to 3 examples
            examples_html += f"""
            <div class="recommendation">
                <strong>{example.get('title', 'Example')}:</strong><br>
                {example.get('explanation', 'No explanation provided')}
            </div>
            """
        
        return f"""
        <h3>💡 Examples Analysis</h3>
        <p><strong>Examples Generated:</strong> {len(generated)}</p>
        {examples_html}
        """
    
    def _generate_recommendations(self, final_output: Dict[str, Any]) -> str:
        """Generate recommendations section"""
        recommendations = final_output.get('recommendations', [])
        
        return f"""
        <div class="section">
            <h2>💡 Key Recommendations</h2>
            <div class="improvement-list">
                <ol>
                    {chr(10).join([f'<li>{rec}</li>' for rec in recommendations[:10]])}
                </ol>
            </div>
        </div>
        """
    
    def _generate_readability_analysis(self, readability_data: Dict[str, Any]) -> str:
        """Generate detailed readability analysis"""
        metrics = readability_data.get('metrics', {})
        if not metrics:
            return ""
        
        return f"""
        <div class="section">
            <h2>📊 Detailed Readability Metrics</h2>
            <table>
                <tr><th>Metric</th><th>Score</th><th>Interpretation</th></tr>
                <tr><td>Flesch Reading Ease</td><td>{metrics.get('flesch_reading_ease', 'N/A')}</td><td>{metrics.get('readability_level', 'N/A')}</td></tr>
                <tr><td>Flesch-Kincaid Grade</td><td>{metrics.get('flesch_kincaid_grade', 'N/A')}</td><td>{metrics.get('grade_level', 'N/A')}</td></tr>
                <tr><td>Gunning Fog Index</td><td>{metrics.get('gunning_fog', 'N/A')}</td><td>Ideal: 7-8</td></tr>
                <tr><td>Average Sentence Length</td><td>{metrics.get('avg_sentence_length', 'N/A')} words</td><td>Ideal: 15-20 words</td></tr>
                <tr><td>Average Syllables per Word</td><td>{metrics.get('avg_syllables_per_word', 'N/A')}</td><td>Ideal: 1.4-1.6</td></tr>
                <tr><td>Word Count</td><td>{metrics.get('word_count', 'N/A')}</td><td>-</td></tr>
                <tr><td>Sentence Count</td><td>{metrics.get('sentence_count', 'N/A')}</td><td>-</td></tr>
            </table>
        </div>
        """