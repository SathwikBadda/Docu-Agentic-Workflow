import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4-turbo-preview"

# Temperature settings for different agents
AGENT_TEMPERATURES = {
    "analyzer": 0.3,
    "rewriter": 0.7,
    "persona": 0.6,
    "localization": 0.4,
    "example_generator": 0.8,
    "readability": 0.2
}

# Persona configurations
PERSONAS = {
    "Marketer": {
        "description": "Focus on clear value propositions, ROI, and business impact",
        "tone": "persuasive and benefit-focused",
        "priorities": ["clarity", "business_value", "actionable_insights"]
    },
    "Developer": {
        "description": "Emphasize technical accuracy, code examples, and implementation details",
        "tone": "technical and precise",
        "priorities": ["accuracy", "code_examples", "implementation_steps"]
    },
    "Product Manager": {
        "description": "Balance technical and business aspects, focus on user experience",
        "tone": "strategic and user-centric",
        "priorities": ["user_experience", "feature_benefits", "strategic_context"]
    }
}

# Readability thresholds
READABILITY_THRESHOLDS = {
    "flesch_reading_ease": {
        "green": 70,
        "yellow": 50,
        "red": 0
    },
    "flesch_kincaid_grade": {
        "green": 8,
        "yellow": 12,
        "red": float('inf')
    }
}

# Microsoft Style Guide principles
STYLE_GUIDE_PRINCIPLES = [
    "Use active voice",
    "Write concisely",
    "Use parallel structure",
    "Write for your audience",
    "Use simple words",
    "Be inclusive",
    "Use positive tone"
]