"""
Conversation memory management for maintaining chat context
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from collections import defaultdict
from backend.config import settings

class ConversationMemory:
    """Manages conversation history and context"""
    
    def __init__(self, max_history: int = None):
        """
        Initialize conversation memory
        
        Args:
            max_history: Maximum number of messages to keep in history
        """
        self.max_history = max_history or settings.MAX_CONVERSATION_HISTORY
        self.conversations: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    
    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Add a message to conversation history
        
        Args:
            session_id: Unique session identifier
            role: Message role ('user', 'assistant', 'system')
            content: Message content
            metadata: Additional metadata
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        self.conversations[session_id].append(message)
        
        # Trim history if it exceeds max_history
        if len(self.conversations[session_id]) > self.max_history * 2:  # *2 for user+assistant pairs
            self.conversations[session_id] = self.conversations[session_id][-self.max_history * 2:]
    
    def get_history(
        self,
        session_id: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get conversation history for a session
        
        Args:
            session_id: Unique session identifier
            limit: Maximum number of messages to return
            
        Returns:
            List of messages
        """
        history = self.conversations.get(session_id, [])
        
        if limit:
            return history[-limit:]
        
        return history
    
    def get_messages_for_llm(
        self,
        session_id: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, str]]:
        """
        Get conversation history formatted for LLM
        
        Args:
            session_id: Unique session identifier
            limit: Maximum number of messages to return
            
        Returns:
            List of messages with role and content only
        """
        history = self.get_history(session_id, limit)
        
        return [
            {"role": msg["role"], "content": msg["content"]}
            for msg in history
            if msg["role"] in ["user", "assistant", "system"]
        ]
    
    def get_context_summary(self, session_id: str) -> str:
        """
        Get a summary of recent conversation context
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            Context summary string
        """
        history = self.get_history(session_id, limit=6)  # Last 3 exchanges
        
        if not history:
            return "No previous conversation context."
        
        summary = "Recent conversation context:\n"
        for msg in history:
            role = msg["role"].capitalize()
            content = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
            summary += f"{role}: {content}\n"
        
        return summary
    
    def clear_session(self, session_id: str):
        """
        Clear conversation history for a session
        
        Args:
            session_id: Unique session identifier
        """
        if session_id in self.conversations:
            del self.conversations[session_id]
    
    def get_last_query_result(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the last query result from conversation history
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            Last query result metadata or None
        """
        history = self.get_history(session_id)
        
        for msg in reversed(history):
            if msg["role"] == "assistant" and "query_result" in msg.get("metadata", {}):
                return msg["metadata"]["query_result"]
        
        return None
    
    def get_session_count(self) -> int:
        """
        Get number of active sessions
        
        Returns:
            Number of sessions
        """
        return len(self.conversations)

# Global conversation memory instance
conversation_memory = ConversationMemory()
