from abc import ABC, abstractmethod
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import json
from typing import Any, Dict

class BaseAgent(ABC):
    """Base class for all documentation agents"""
    
    def __init__(self, temperature: float = 0.5):
        self.llm = ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=temperature
        )
        self._setup_agent()
    
    @abstractmethod
    def _get_system_prompt(self) -> str:
        """Return the system prompt for this agent"""
        pass
    
    @abstractmethod
    def _get_user_prompt_template(self) -> str:
        """Return the user prompt template for this agent"""
        pass
    
    def _setup_agent(self):
        """Setup the LangChain agent"""
        system_prompt = self._get_system_prompt()
        user_template = self._get_user_prompt_template()
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", user_template)
        ])
        
        self.prompt = prompt
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent with input data"""
        try:
            # Format the prompt with input data
            formatted_prompt = self.prompt.format(**input_data)
            
            # Get response from LLM
            response = self.llm.invoke(formatted_prompt)
            
            # Parse response
            return self._parse_response(response.content, input_data)
            
        except Exception as e:
            return {
                "error": str(e),
                "agent": self.__class__.__name__
            }
    
    def _parse_response(self, response: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse the LLM response. Override in subclasses if needed."""
        try:
            # Try to parse as JSON first
            if response.strip().startswith('{') or response.strip().startswith('['):
                return json.loads(response)
            else:
                return {"result": response}
        except json.JSONDecodeError:
            return {"result": response}


class JSONOutputParser:
    """Custom parser for JSON outputs"""
    
    def parse(self, text: str) -> Dict[str, Any]:
        try:
            # Extract JSON from text if it's wrapped in markdown
            if "```json" in text:
                start = text.find("```json") + 7
                end = text.find("```", start)
                text = text[start:end]
            
            return json.loads(text.strip())
        except json.JSONDecodeError:
            return {"raw_output": text}