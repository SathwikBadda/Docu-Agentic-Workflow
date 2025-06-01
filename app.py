import streamlit as st
import json
import os
from datetime import datetime
import tempfile

# Import our custom modules
from utils.content_scraper import ContentScraper
from orchestrator.agent_orchestrator import AgentOrchestrator
from utils.pdf_generator import PDFGenerator
from config import PERSONAS

# Page configuration
st.set_page_config(
    page_title="AI Documentation Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-blue: #2E86AB;
        --secondary-blue: #A23B72;
        --accent-green: #F18F01;
        --light-bg: #F8F9FA;
        --dark-text: #2C3E50;
        --success-green: #27AE60;
        --warning-yellow: #F39C12;
        --error-red: #E74C3C;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    
    .main-header {
        text-align: center;
        padding: 2.5rem 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-header p {
        font-size: 1.2rem;
        opacity: 0.9;
        margin: 0;
    }
    
    .metric-box {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        margin: 0.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
        border: none;
    }
    
    .metric-box:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    .metric-box h4 {
        color: #2C3E50;
        font-weight: 600;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .metric-box h2 {
        color: #34495E;
        font-weight: 800;
        font-size: 2rem;
        margin: 0;
    }
    
    .improvement-item {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.75rem 0;
        border-left: 4px solid var(--success-green);
        box-shadow: 0 2px 8px rgba(39, 174, 96, 0.1);
        font-weight: 500;
    }
    
    .status-success {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1.25rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(39, 174, 96, 0.1);
    }
    
    .status-error {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1.25rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(231, 76, 60, 0.1);
    }
    
    /* Readability indicators */
    .readability-indicator {
        display: inline-block;
        width: 14px;
        height: 14px;
        border-radius: 50%;
        margin-right: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    .green { background: linear-gradient(135deg, #27AE60, #2ECC71); }
    .yellow { background: linear-gradient(135deg, #F39C12, #E67E22); }
    .red { background: linear-gradient(135deg, #E74C3C, #C0392B); }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 8px;
        color: #6c757d;
        font-weight: 500;
        padding: 0.75rem 1.5rem;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    /* Custom card styling */
    .custom-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        margin: 1rem 0;
        border: 1px solid #e9ecef;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 8px;
        font-weight: 600;
        color: #495057;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    /* Score card specific styling */
    .score-high {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        color: #155724;
        border-left: 4px solid #27AE60;
    }
    
    .score-medium {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        color: #856404;
        border-left: 4px solid #F39C12;
    }
    
    .score-low {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        color: #721c24;
        border-left: 4px solid #E74C3C;
    }
    
    /* Text visibility improvements */
    .metric-box, .improvement-item, .custom-card {
        text-shadow: none;
    }
    
    .metric-box h4, .metric-box h2 {
        text-shadow: none;
        font-weight: 700;
    }
    
    /* Paragraph analysis styling */
    .paragraph-analysis {
        background: white;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    /* Localization issue styling */
    .localization-issue {
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.75rem 0;
        border-left: 4px solid #6c757d;
    }
    
    .localization-issue strong {
        color: #495057;
        font-weight: 600;
    }
    
    /* Readability distribution cards */
    .readability-card {
        background: white;
        border: 2px solid;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    
    .readability-card:hover {
        transform: translateY(-3px);
    }
    
    .readability-card.green-card {
        border-color: #27AE60;
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
    }
    
    .readability-card.yellow-card {
        border-color: #F39C12;
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
    }
    
    .readability-card.red-card {
        border-color: #E74C3C;
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
    }
    
    .readability-card h4 {
        margin-bottom: 0.5rem;
        font-weight: 600;
        color: #2C3E50;
    }
    
    .readability-card h3 {
        margin: 0;
        font-weight: 800;
        font-size: 2rem;
        color: #34495E;
    }
    
    /* Overall layout improvements */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    
    /* Header improvements */
    h1, h2, h3 {
        color: #2C3E50;
        font-weight: 700;
    }
    
    /* Subheader styling */
    .stMarkdown h2 {
        border-bottom: 2px solid #E9ECEF;
        padding-bottom: 0.5rem;
        margin-bottom: 1.5rem;
    }
    
    /* Warning and info styling */
    .stAlert {
        border-radius: 10px;
        border: none;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    /* Progress bar styling */
    .stProgress > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    /* Table styling */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Code blocks */
    .stCodeBlock {
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    /* Download button specific styling */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);
        transition: all 0.3s ease;
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(40, 167, 69, 0.4);
    }
    
    /* Metric improvements */
    [data-testid="metric-container"] {
        background: white;
        border: 1px solid #E9ECEF;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 2px solid #E9ECEF;
        transition: border-color 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
    }
    
    /* Selectbox styling */
    .stSelectbox > div > div {
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🤖 AI Documentation Assistant</h1>
        <p>Transform your documentation with GPT-4 powered analysis and improvement</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar configuration
    st.sidebar.header("🔧 Configuration")
    
    # Check OpenAI API key
    api_key = st.sidebar.text_input("OpenAI API Key", type="password", help="Enter your OpenAI API key")
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
    
    # URL input
    st.sidebar.header("📝 Document Input")
    url = st.sidebar.text_input(
        "Documentation URL",
        placeholder="https://example.com/docs/article",
        help="Enter the URL of the documentation you want to improve"
    )
    
    # Persona selection
    persona = st.sidebar.selectbox(
        "Target Persona",
        options=list(PERSONAS.keys()),
        help="Choose the target audience for optimization"
    )
    
    # Display persona info
    if persona:
        persona_info = PERSONAS[persona]
        st.sidebar.info(f"**{persona}**: {persona_info['description']}")
    
    # Main content area
    if not api_key:
        st.warning("⚠️ Please enter your OpenAI API key in the sidebar to continue.")
        st.info("You can get your API key from [OpenAI's website](https://platform.openai.com/api-keys)")
        return
    
    if not url:
        st.info("👆 Please enter a documentation URL in the sidebar to get started.")
        
        # Show example
        st.markdown("### 📖 How it works:")
        st.markdown("""
        1. **Enter URL**: Provide a link to any documentation page
        2. **Choose Persona**: Select your target audience (Marketer, Developer, Product Manager)
        3. **Analyze**: Our AI agents will analyze and improve the content
        4. **Download**: Get a comprehensive PDF report with improvements
        """)
        
        st.markdown("### 🧠 AI Agents:")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            - **📋 Documentation Analyzer**: Assesses readability and structure
            - **✍️ Content Rewriter**: Improves clarity and flow
            - **👤 Persona Expert**: Adapts content for target audience
            """)
        
        with col2:
            st.markdown("""
            - **🌍 Localization Specialist**: Ensures international readiness
            - **💡 Example Generator**: Adds relevant examples
            - **📊 Readability Scorer**: Analyzes text complexity
            """)
        
        return
    
    # Process button
    col1, col2 = st.columns([2, 1])
    with col1:
        process_btn = st.button("🚀 Analyze & Improve Documentation", type="primary")
    with col2:
        if 'processing_results' in st.session_state:
            if st.button("📥 Download PDF Report"):
                download_pdf()
    
    # Processing
    if process_btn:
        process_documentation(url, persona)
    
    # Display results
    if 'processing_results' in st.session_state and st.session_state.processing_results is not None:
        display_results()
    elif process_btn:
        # Show a message if processing was just started
        st.info("⏳ Processing has started. Results will appear above once analysis is complete.")

def process_documentation(url: str, persona: str):
    """Process documentation through all agents"""
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Step 1: Scrape content
        status_text.text("🔍 Scraping documentation content...")
        progress_bar.progress(10)
        
        scraper = ContentScraper()
        content_data = scraper.scrape_url(url)
        
        if 'error' in content_data:
            st.error(f"❌ Failed to scrape content: {content_data['error']}")
            return
        
        # Step 2: Initialize orchestrator
        status_text.text("🤖 Initializing AI agents...")
        progress_bar.progress(20)
        
        orchestrator = AgentOrchestrator()
        
        # Step 3: Process through agents
        status_text.text("🧠 Processing with AI agents...")
        progress_bar.progress(30)
        
        # This will take a while, so we'll update progress as we go
        results = orchestrator.process_documentation(content_data, persona)
        
        # Check if processing was successful
        if not results or 'error' in results:
            st.error(f"❌ Processing failed: {results.get('error', 'Unknown error')}")
            return
        
        progress_bar.progress(100)
        status_text.text("✅ Processing complete!")
        
        # Store results in session state
        st.session_state.processing_results = results
        
        # Show success message
        st.markdown("""
        <div class="status-success">
            <strong>🎉 Success!</strong> Your documentation has been analyzed and improved by our AI agents.
        </div>
        """, unsafe_allow_html=True)
        
        # Auto-scroll to results (rerun to show results)
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Processing failed: {str(e)}")
        status_text.text("❌ Processing failed")
        progress_bar.progress(0)

def display_results():
    """Display processing results in organized tabs"""
    
    if 'processing_results' not in st.session_state or st.session_state.processing_results is None:
        st.warning("No results to display. Please run the analysis first.")
        return
    
    results = st.session_state.processing_results
    
    # Check if results have the expected structure
    if not isinstance(results, dict):
        st.error("Invalid results format. Please run the analysis again.")
        return
    
    # Create tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📊 Overview", "🧠 Analysis", "📝 Improved Content", 
        "👤 Persona Feedback", "🌍 Localization", "💡 Examples", "📈 Readability"
    ])
    
    with tab1:
        display_overview_tab(results)
    
    with tab2:
        display_analysis_tab(results)
    
    with tab3:
        display_content_tab(results)
    
    with tab4:
        display_persona_tab(results)
    
    with tab5:
        display_localization_tab(results)
    
    with tab6:
        display_examples_tab(results)
    
    with tab7:
        display_readability_tab(results)

def display_overview_tab(results):
    """Display overview and summary"""
    
    final_output = results.get('final_output') or {}
    input_data = results.get('input_data') or {}
    
    # Key metrics
    st.subheader("📊 Key Metrics")
    
    scores = final_output.get('scores') or {}
    
    # Display scores in columns
    cols = st.columns(4)
    
    metrics = [
        ("Overall Score", scores.get('overall', 5.0)),
        ("Readability", scores.get('readability', 5.0)),
        ("Persona Alignment", scores.get('persona_alignment', 5.0)),
        ("Localization Ready", scores.get('localization_readiness', 7.0))
    ]
    
    for i, (name, score) in enumerate(metrics):
        with cols[i]:
            # Determine color and styling based on score
            if score >= 7:
                color = "#27AE60"
                bg_class = "score-high"
                icon = "🟢"
            elif score >= 5:
                color = "#F39C12" 
                bg_class = "score-medium"
                icon = "🟡"
            else:
                color = "#E74C3C"
                bg_class = "score-low"
                icon = "🔴"
                
            st.markdown(f"""
            <div class="metric-box {bg_class}" style="border-left: 5px solid {color};">
                <h4>{icon} {name}</h4>
                <h2>{score:.1f}/10</h2>
            </div>
            """, unsafe_allow_html=True)
    
    # Improvement summary
    st.subheader("🔧 Improvements Made")
    improvements = final_output.get('improvement_summary') or []
    
    if improvements:
        for improvement in improvements:
            st.markdown(f"""
            <div class="improvement-item">
                ✅ {improvement}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Processing in progress... Improvements will appear here once analysis is complete.")
    
    # Word count changes
    word_count = final_output.get('word_count_change') or {}
    if word_count:
        st.subheader("📝 Content Statistics")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="custom-card">
                <h4 style="color: #6c757d; margin-bottom: 0.5rem;">Original Words</h4>
                <h2 style="color: #495057; margin: 0;">{word_count.get('original', 0):,}</h2>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="custom-card">
                <h4 style="color: #6c757d; margin-bottom: 0.5rem;">Final Words</h4>
                <h2 style="color: #495057; margin: 0;">{word_count.get('final', 0):,}</h2>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            change = word_count.get('change', 0)
            change_pct = word_count.get('percentage_change', 0)
            change_color = "#27AE60" if change >= 0 else "#E74C3C"
            change_icon = "📈" if change >= 0 else "📉"
            
            st.markdown(f"""
            <div class="custom-card" style="border-left: 4px solid {change_color};">
                <h4 style="color: #6c757d; margin-bottom: 0.5rem;">{change_icon} Change</h4>
                <h2 style="color: {change_color}; margin: 0;">{change:+,} ({change_pct:+.1f}%)</h2>
            </div>
            """, unsafe_allow_html=True)

def display_analysis_tab(results):
    """Display detailed analysis results"""
    
    agent_results = results.get('agent_results') or {}
    analysis = agent_results.get('analysis') or {}
    
    if not analysis:
        st.warning("No analysis data available. Please run the analysis first.")
        return
    
    # Overall score
    overall_score = analysis.get('overall_score', 0)
    st.metric("Overall Analysis Score", f"{overall_score}/10")
    
    # Detailed scores
    st.subheader("📋 Detailed Analysis")
    
    categories = ['readability', 'structure', 'completeness', 'style_guide_adherence']
    
    for category in categories:
        if category in analysis:
            data = analysis[category]
            score = data.get('score', 0)
            issues = data.get('issues', [])
            suggestions = data.get('suggestions', [])
            
            with st.expander(f"{category.replace('_', ' ').title()} (Score: {score}/10)"):
                if issues:
                    st.write("**Issues Found:**")
                    for issue in issues:
                        st.write(f"• {issue}")
                
                if suggestions:
                    st.write("**Suggestions:**")
                    for suggestion in suggestions:
                        st.write(f"• {suggestion}")
    
    # Priority fixes
    priority_fixes = analysis.get('priority_fixes', [])
    if priority_fixes:
        st.subheader("🔥 Priority Fixes")
        for fix in priority_fixes:
            st.error(f"⚠️ {fix}")

def display_content_tab(results):
    """Display improved content"""
    
    final_output = results.get('final_output') or {}
    input_data = results.get('input_data') or {}
    
    final_content = final_output.get('final_content', '')
    original_content = input_data.get('text', '')
    
    if not final_content and not original_content:
        st.warning("No content available. Please run the analysis first.")
        return
    
    # Toggle between original and improved
    view_mode = st.radio("View Mode", ["Improved Content", "Original Content", "Side-by-Side"])
    
    if view_mode == "Improved Content":
        st.subheader("📝 Improved Documentation")
        st.markdown(final_content)
    
    elif view_mode == "Original Content":
        st.subheader("📄 Original Documentation")
        st.text(original_content)
    
    else:  # Side-by-Side
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📄 Original")
            st.text_area("Original Content", original_content, height=400)
        
        with col2:
            st.subheader("📝 Improved")
            st.text_area("Improved Content", final_content, height=400)

def display_persona_tab(results):
    """Display persona-specific feedback"""
    
    agent_results = results.get('agent_results') or {}
    persona_data = agent_results.get('persona_feedback') or {}
    persona = results.get('persona', 'Unknown')
    
    if not persona_data:
        st.warning("No persona feedback available. Please run the analysis first.")
        return
    
    st.subheader(f"👤 {persona} Persona Analysis")
    
    # Alignment score
    alignment_score = persona_data.get('persona_alignment_score', 0)
    st.metric("Persona Alignment Score", f"{alignment_score}/10")
    
    # Issues and suggestions
    sections = [
        ('persona_specific_issues', '⚠️ Issues for this Persona'),
        ('terminology_adjustments', '📝 Terminology Adjustments'),
        ('tone_adjustments', '🎯 Tone Adjustments'),
        ('content_emphasis', '💡 Content Emphasis'),
        ('missing_elements', '❓ Missing Elements'),
        ('call_to_action_suggestions', '🚀 Call-to-Action Suggestions')
    ]
    
    for key, title in sections:
        data = persona_data.get(key, [])
        if data:
            with st.expander(title):
                if key == 'terminology_adjustments':
                    for item in data:
                        st.write(f"**{item.get('current_term', '')}** → **{item.get('suggested_term', '')}**")
                        st.write(f"*Reason: {item.get('reason', '')}*")
                        st.write("---")
                else:
                    for item in data:
                        st.write(f"• {item}")
    
    # Sample rewrites
    rewrites = persona_data.get('sample_rewrites', [])
    if rewrites:
        st.subheader("✍️ Sample Improvements")
        for rewrite in rewrites:
            with st.expander(f"Improvement Example"):
                st.write("**Original:**")
                st.write(rewrite.get('original_paragraph', ''))
                st.write("**Improved:**")
                st.write(rewrite.get('rewritten_paragraph', ''))
                st.write("**Why this works better:**")
                st.write(rewrite.get('explanation', ''))

def display_localization_tab(results):
    """Display localization analysis"""
    
    agent_results = results.get('agent_results') or {}
    localization_data = agent_results.get('localization') or {}
    
    if not localization_data:
        st.warning("No localization data available. Please run the analysis first.")
        return
    
    # Readiness score
    readiness_score = localization_data.get('localization_readiness_score', 0)
    st.metric("Localization Readiness Score", f"{readiness_score}/10")
    
    # Analysis sections
    sections = [
        ('cultural_references', '🌍 Cultural References'),
        ('idioms_and_expressions', '💬 Idioms & Expressions'),
        ('formatting_issues', '📋 Formatting Issues'),
        ('assumptions', '🤔 Assumptions'),
        ('legal_regulatory', '⚖️ Legal/Regulatory References'),
        ('hard_to_translate', '🔄 Hard to Translate'),
        ('recommended_changes', '✅ Recommended Changes')
    ]
    
    for key, title in sections:
        data = localization_data.get(key, [])
        if data:
            with st.expander(title):
                if key == 'recommended_changes':
                    for item in data:
                        st.markdown(f"""
                        <div class="localization-issue">
                            <p><strong>Original:</strong> "{item.get('original', 'N/A')}"</p>
                            <p><strong>Improved:</strong> "{item.get('improved', 'N/A')}"</p>
                            <p><strong>Reason:</strong> {item.get('reason', 'N/A')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                elif isinstance(data[0], dict) if data else False:
                    for item in data:
                        issue_text = item.get('phrase', item.get('assumption', item.get('reference', item.get('idiom', 'Unknown'))))
                        problem_text = item.get('issue', item.get('why_difficult', 'No issue description'))
                        suggestion_text = item.get('suggestion', item.get('alternative', 'No suggestion provided'))
                        
                        st.markdown(f"""
                        <div class="localization-issue">
                            <p><strong>Issue:</strong> "{issue_text}"</p>
                            <p><strong>Problem:</strong> {problem_text}</p>
                            <p><strong>Suggestion:</strong> {suggestion_text}</p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    for item in data:
                        st.markdown(f"""
                        <div class="localization-issue">
                            <p>• {item}</p>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            # Show when no issues found for that category
            with st.expander(title):
                st.success(f"✅ No {title.lower()} found - this is good for international readiness!")

def display_examples_tab(results):
    """Display generated examples"""
    
    agent_results = results.get('agent_results') or {}
    examples_data = agent_results.get('examples') or {}
    
    if not examples_data:
        st.warning("No examples data available. Please run the analysis first.")
        return
    
    # Sections needing examples
    sections_needing = examples_data.get('sections_needing_examples', [])
    if sections_needing:
        st.subheader("📋 Sections That Need Examples")
        for section in sections_needing:
            with st.expander(section.get('section_title', 'Unknown Section')):
                st.write(f"**Why needed:** {section.get('reason', '')}")
                st.write(f"**Complexity:** {section.get('complexity_level', 'Unknown')}")
    
    # Generated examples
    generated = examples_data.get('generated_examples', [])
    if generated:
        st.subheader("💡 Generated Examples")
        for example in generated:
            with st.expander(f"Example: {example.get('title', 'Untitled')}"):
                st.write(f"**Type:** {example.get('example_type', 'Unknown')}")
                st.write(f"**Section:** {example.get('section', 'General')}")
                st.write("**Content:**")
                st.markdown(example.get('content', ''))
                if example.get('explanation'):
                    st.write(f"**Explanation:** {example.get('explanation')}")
                if example.get('placement_suggestion'):
                    st.info(f"💡 Suggested placement: {example.get('placement_suggestion')}")
    
    # Code examples
    code_examples = examples_data.get('code_examples', [])
    if code_examples:
        st.subheader("💻 Code Examples")
        for code in code_examples:
            with st.expander(f"Code: {code.get('description', 'Code Example')}"):
                st.write(f"**Language:** {code.get('language', 'Unknown')}")
                st.code(code.get('code', ''), language=code.get('language', 'text'))
                if code.get('description'):
                    st.write(f"**Description:** {code.get('description')}")
    
    # Scenario examples
    scenario_examples = examples_data.get('scenario_examples', [])
    if scenario_examples:
        st.subheader("🎯 Scenario Examples")
        for scenario in scenario_examples:
            with st.expander(f"Scenario: {scenario.get('scenario', 'Example Scenario')[:50]}..."):
                st.write("**Scenario:**")
                st.write(scenario.get('scenario', ''))
                
                steps = scenario.get('step_by_step', [])
                if steps:
                    st.write("**Steps:**")
                    for i, step in enumerate(steps, 1):
                        st.write(f"{i}. {step}")
                
                if scenario.get('outcome'):
                    st.write(f"**Expected Outcome:** {scenario.get('outcome')}")

def display_readability_tab(results):
    """Display readability analysis and visualization"""
    
    agent_results = results.get('agent_results') or {}
    readability_data = agent_results.get('readability') or {}
    
    if not readability_data:
        st.warning("No readability data available. Please run the analysis first.")
        return
    
    metrics = readability_data.get('metrics') or {}
    paragraph_analysis = readability_data.get('paragraph_analysis') or []
    visualization_data = readability_data.get('visualization_data') or {}
    
    # Overall metrics
    st.subheader("📊 Readability Metrics")
    
    if metrics:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="custom-card">
                <h4 style="color: #6c757d; margin-bottom: 0.5rem;">Flesch Reading Ease</h4>
                <h2 style="color: #495057; margin-bottom: 0.5rem;">{metrics.get('flesch_reading_ease', 0):.1f}</h2>
                <p style="color: #6c757d; margin: 0;"><strong>Level:</strong> {metrics.get('readability_level', 'Unknown')}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="custom-card">
                <h4 style="color: #6c757d; margin-bottom: 0.5rem;">Grade Level</h4>
                <h2 style="color: #495057; margin-bottom: 0.5rem;">{metrics.get('flesch_kincaid_grade', 0):.1f}</h2>
                <p style="color: #6c757d; margin: 0;"><strong>Standard:</strong> {metrics.get('text_standard', 'Unknown')}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="custom-card">
                <h4 style="color: #6c757d; margin-bottom: 0.5rem;">Content Stats</h4>
                <h2 style="color: #495057; margin-bottom: 0.5rem;">{metrics.get('word_count', 0)}</h2>
                <p style="color: #6c757d; margin: 0;"><strong>Avg Sentence:</strong> {metrics.get('avg_sentence_length', 0):.1f} words</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Paragraph distribution
    if visualization_data:
        st.subheader("📈 Paragraph Readability Distribution")
        
        distribution = visualization_data.get('color_distribution') or {}
        total = sum(distribution.values()) if distribution else 0
        
        if total > 0:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                green_pct = distribution.get('green', 0) / total * 100
                st.markdown(f"""
                <div class="readability-card green-card">
                    <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 10px;">
                        <span class="readability-indicator green"></span>
                        <h4 style="margin: 0; color: #155724;">Easy to Read</h4>
                    </div>
                    <h3 style="color: #155724; margin: 0;">{distribution.get('green', 0)} ({green_pct:.1f}%)</h3>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                yellow_pct = distribution.get('yellow', 0) / total * 100
                st.markdown(f"""
                <div class="readability-card yellow-card">
                    <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 10px;">
                        <span class="readability-indicator yellow"></span>
                        <h4 style="margin: 0; color: #856404;">Moderate</h4>
                    </div>
                    <h3 style="color: #856404; margin: 0;">{distribution.get('yellow', 0)} ({yellow_pct:.1f}%)</h3>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                red_pct = distribution.get('red', 0) / total * 100
                st.markdown(f"""
                <div class="readability-card red-card">
                    <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 10px;">
                        <span class="readability-indicator red"></span>
                        <h4 style="margin: 0; color: #721c24;">Difficult</h4>
                    </div>
                    <h3 style="color: #721c24; margin: 0;">{distribution.get('red', 0)} ({red_pct:.1f}%)</h3>
                </div>
                """, unsafe_allow_html=True)
    
    # Detailed paragraph analysis
    if paragraph_analysis:
        st.subheader("📝 Paragraph-by-Paragraph Analysis")
        
        # Show only problematic paragraphs by default
        show_all = st.checkbox("Show all paragraphs", value=False)
        
        for para in paragraph_analysis:
            if 'error' in para:
                continue
            
            color = para.get('color', 'yellow')
            
            # Skip easy paragraphs unless show_all is True
            if not show_all and color == 'green':
                continue
            
            color_map = {'green': '#4CAF50', 'yellow': '#FFC107', 'red': '#F44336'}
            
            with st.expander(f"Paragraph {para.get('paragraph_number', 0)} - {para.get('readability_level', 'Unknown')} (Score: {para.get('flesch_score', 0):.1f})"):
                color_map = {'green': '#27AE60', 'yellow': '#F39C12', 'red': '#E74C3C'}
                bg_map = {'green': '#d4edda', 'yellow': '#fff3cd', 'red': '#f8d7da'}
                
                st.markdown(f"""
                <div class="paragraph-analysis" style="border-left: 4px solid {color_map.get(color, '#6c757d')}; background-color: {bg_map.get(color, '#f8f9fa')};">
                    <p><strong>Preview:</strong> {para.get('text_preview', 'No preview available')}</p>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1rem;">
                        <div>
                            <p><strong>Flesch Score:</strong> {para.get('flesch_score', 0):.1f}</p>
                            <p><strong>Grade Level:</strong> {para.get('grade_level', 0):.1f}</p>
                        </div>
                        <div>
                            <p><strong>Words:</strong> {para.get('word_count', 0)}</p>
                            <p><strong>Sentences:</strong> {para.get('sentence_count', 0)}</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # AI insights
    ai_insights = readability_data.get('ai_insights') or {}
    if ai_insights and not ai_insights.get('error'):
        st.subheader("🧠 AI Readability Insights")
        
        assessment = ai_insights.get('overall_assessment') or {}
        if assessment:
            st.markdown(f"""
            <div class="custom-card">
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem;">
                    <div>
                        <h4 style="color: #6c757d;">Reading Level</h4>
                        <p style="color: #495057; font-weight: 600; margin: 0;">{assessment.get('reading_level', 'Unknown')}</p>
                    </div>
                    <div>
                        <h4 style="color: #6c757d;">Accessibility</h4>
                        <p style="color: #495057; font-weight: 600; margin: 0;">{assessment.get('accessibility', 'Unknown')}</p>
                    </div>
                    <div>
                        <h4 style="color: #6c757d;">Target Audience</h4>
                        <p style="color: #495057; font-weight: 600; margin: 0;">{assessment.get('target_audience', 'Unknown')}</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            insights = ai_insights.get('key_insights') or []
            if insights:
                st.markdown("**💡 Key Insights:**")
                for insight in insights:
                    st.markdown(f"""
                    <div class="custom-card" style="margin: 0.5rem 0;">
                        <p style="margin: 0; color: #495057;">• {insight}</p>
                    </div>
                    """, unsafe_allow_html=True)
        
        with col2:
            recommendations = ai_insights.get('recommendations') or []
            if recommendations:
                st.markdown("**🎯 Recommendations:**")
                for rec in recommendations:
                    st.markdown(f"""
                    <div class="custom-card" style="margin: 0.5rem 0; border-left: 4px solid #F39C12;">
                        <p style="margin: 0; color: #495057;">• {rec}</p>
                    </div>
                    """, unsafe_allow_html=True)
            for insight in insights:
                st.write(f"• {insight}")
        
        recommendations = ai_insights.get('recommendations') or []
        if recommendations:
            st.write("**Recommendations:**")
            for rec in recommendations:
                st.write(f"• {rec}")

def download_pdf():
    """Generate and download PDF report"""
    
    if 'processing_results' not in st.session_state:
        st.error("No results to download")
        return
    
    try:
        # Generate PDF
        pdf_generator = PDFGenerator()
        
        with st.spinner("Generating PDF report..."):
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                pdf_path = pdf_generator.generate_pdf(
                    st.session_state.processing_results,
                    tmp_file.name
                )
                
                # Read the generated PDF
                with open(pdf_path, 'rb') as pdf_file:
                    pdf_bytes = pdf_file.read()
                
                # Create download button
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"documentation_improvement_report_{timestamp}.pdf"
                
                st.download_button(
                    label="📥 Download PDF Report",
                    data=pdf_bytes,
                    file_name=filename,
                    mime="application/pdf"
                )
                
                # Clean up temporary file
                os.unlink(pdf_path)
                
                st.success("✅ PDF report generated successfully!")
    
    except Exception as e:
        st.error(f"❌ Failed to generate PDF: {str(e)}")

# Initialize session state
if 'processing_results' not in st.session_state:
    st.session_state.processing_results = None

if __name__ == "__main__":
    main()