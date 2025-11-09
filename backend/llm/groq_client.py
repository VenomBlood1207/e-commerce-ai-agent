"""
Groq API client wrapper for LLM interactions
"""
from typing import Optional, List, Dict, Any
import os
from groq import Groq
from backend.config import settings

class GroqClient:
    """Wrapper for Groq API interactions"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Groq client"""
        self.api_key = api_key or settings.GROQ_API_KEY
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        self.client = Groq(api_key=self.api_key)
        self.reasoning_model = settings.REASONING_MODEL
        self.sql_model = settings.SQL_MODEL
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: int = 2048,
        stream: bool = False
    ) -> Any:
        """
        Generate chat completion
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model to use (defaults to reasoning model)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            
        Returns:
            Completion response or stream
        """
        model = model or self.reasoning_model
        temperature = temperature if temperature is not None else settings.DEFAULT_TEMPERATURE
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream
            )
            return response
        except Exception as e:
            raise Exception(f"Groq API error: {str(e)}")
    
    def generate_sql(
        self,
        question: str,
        schema_info: str,
        examples: str = ""
    ) -> str:
        """
        Generate SQL query from natural language
        
        Args:
            question: Natural language question
            schema_info: Database schema information
            examples: Example queries for few-shot learning
            
        Returns:
            Generated SQL query
        """
        system_prompt = f"""You are an expert SQL query generator for an e-commerce database.
        
Database Schema:
{schema_info}

{examples}

Generate ONLY the SQL query without any explanation or markdown formatting.
Use SQLite syntax. Ensure queries are safe and optimized."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Generate SQL for: {question}"}
        ]
        
        response = self.chat_completion(
            messages=messages,
            model=self.sql_model,
            temperature=settings.SQL_TEMPERATURE,
            max_tokens=1024
        )
        
        sql_query = response.choices[0].message.content.strip()
        
        # Clean up the response
        sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
        
        return sql_query
    
    def generate_response(
        self,
        prompt: str,
        context: Optional[str] = None,
        temperature: Optional[float] = None
    ) -> str:
        """
        Generate a general response
        
        Args:
            prompt: User prompt
            context: Additional context
            temperature: Sampling temperature
            
        Returns:
            Generated response
        """
        messages = []
        
        if context:
            messages.append({"role": "system", "content": context})
        
        messages.append({"role": "user", "content": prompt})
        
        response = self.chat_completion(
            messages=messages,
            temperature=temperature
        )
        
        return response.choices[0].message.content.strip()
    
    def stream_response(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None
    ):
        """
        Stream chat completion
        
        Args:
            messages: List of message dictionaries
            model: Model to use
            temperature: Sampling temperature
            
        Yields:
            Response chunks
        """
        response_stream = self.chat_completion(
            messages=messages,
            model=model,
            temperature=temperature,
            stream=True
        )
        
        for chunk in response_stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

# Global client instance
groq_client = GroqClient()
