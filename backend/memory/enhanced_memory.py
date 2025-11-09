"""
Enhanced conversation memory with personalization and context awareness
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from collections import defaultdict
import json
from backend.config import settings
from backend.llm.groq_client import groq_client

class EnhancedConversationMemory:
    """Enhanced memory with personalization and smart context management"""
    
    def __init__(self, max_history: int = None):
        """Initialize enhanced conversation memory"""
        self.max_history = max_history or settings.MAX_CONVERSATION_HISTORY
        self.conversations: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.user_profiles: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.conversation_summaries: Dict[str, str] = {}
        
    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Add a message and update user profile"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        self.conversations[session_id].append(message)
        
        # Update user profile based on interactions
        if role == "user":
            self._update_user_profile(session_id, content, metadata)
        
        # Trim history if needed
        if len(self.conversations[session_id]) > self.max_history * 2:
            # Create summary before trimming
            self._create_conversation_summary(session_id)
            self.conversations[session_id] = self.conversations[session_id][-self.max_history * 2:]
    
    def _update_user_profile(self, session_id: str, content: str, metadata: Optional[Dict] = None):
        """Update user profile based on interactions"""
        profile = self.user_profiles[session_id]
        
        # Track interaction count
        profile['total_interactions'] = profile.get('total_interactions', 0) + 1
        profile['last_interaction'] = datetime.now().isoformat()
        
        # Track query types
        if metadata and 'query_type' in metadata:
            query_types = profile.get('query_types', {})
            query_type = metadata['query_type']
            query_types[query_type] = query_types.get(query_type, 0) + 1
            profile['query_types'] = query_types
        
        # Track topics of interest (simple keyword extraction)
        topics = profile.get('topics_of_interest', {})
        keywords = self._extract_keywords(content)
        for keyword in keywords:
            topics[keyword] = topics.get(keyword, 0) + 1
        profile['topics_of_interest'] = topics
        
        # Track preferred language (if translation queries)
        if 'translate' in content.lower() or 'traduz' in content.lower():
            profile['uses_translation'] = True
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Simple keyword extraction"""
        # Common e-commerce keywords
        keywords = [
            'product', 'order', 'delivery', 'customer', 'review', 'payment',
            'category', 'seller', 'price', 'revenue', 'sales', 'shipping'
        ]
        
        text_lower = text.lower()
        return [kw for kw in keywords if kw in text_lower]
    
    def _create_conversation_summary(self, session_id: str):
        """Create a summary of the conversation before trimming"""
        history = self.conversations[session_id]
        
        if len(history) < 4:
            return
        
        # Get messages to summarize
        messages_to_summarize = history[:-self.max_history * 2]
        
        # Create summary prompt
        conversation_text = "\n".join([
            f"{msg['role']}: {msg['content'][:200]}"
            for msg in messages_to_summarize
        ])
        
        prompt = f"""Summarize this conversation in 2-3 sentences, focusing on key topics discussed and important information:

{conversation_text}

Summary:"""
        
        try:
            summary = groq_client.generate_response(prompt, temperature=0.3, max_tokens=150)
            
            # Append to existing summary
            existing = self.conversation_summaries.get(session_id, "")
            self.conversation_summaries[session_id] = f"{existing}\n{summary}".strip()
        except Exception as e:
            print(f"Summary generation error: {e}")
    
    def get_personalized_context(self, session_id: str) -> str:
        """Get personalized context including user profile and history"""
        profile = self.user_profiles.get(session_id, {})
        history = self.get_history(session_id, limit=6)
        summary = self.conversation_summaries.get(session_id, "")
        
        context = []
        
        # Add conversation summary if exists
        if summary:
            context.append(f"Previous conversation summary: {summary}")
        
        # Add user profile insights
        if profile.get('total_interactions', 0) > 5:
            context.append(f"User has had {profile['total_interactions']} interactions.")
            
            # Add preferred topics
            topics = profile.get('topics_of_interest', {})
            if topics:
                top_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)[:3]
                topic_names = [t[0] for t in top_topics]
                context.append(f"User is interested in: {', '.join(topic_names)}")
        
        # Add recent conversation
        if history:
            context.append("\nRecent conversation:")
            for msg in history[-4:]:
                role = msg["role"].capitalize()
                content = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
                context.append(f"{role}: {content}")
        
        return "\n".join(context) if context else "No previous context."
    
    def get_user_preferences(self, session_id: str) -> Dict[str, Any]:
        """Get user preferences and profile"""
        return self.user_profiles.get(session_id, {})
    
    def get_history(self, session_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get conversation history"""
        history = self.conversations.get(session_id, [])
        if limit:
            return history[-limit:]
        return history
    
    def get_messages_for_llm(self, session_id: str, limit: Optional[int] = None) -> List[Dict[str, str]]:
        """Get conversation history formatted for LLM"""
        history = self.get_history(session_id, limit)
        return [
            {"role": msg["role"], "content": msg["content"]}
            for msg in history
            if msg["role"] in ["user", "assistant", "system"]
        ]
    
    def clear_session(self, session_id: str):
        """Clear conversation history and profile"""
        if session_id in self.conversations:
            del self.conversations[session_id]
        if session_id in self.user_profiles:
            del self.user_profiles[session_id]
        if session_id in self.conversation_summaries:
            del self.conversation_summaries[session_id]
    
    def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """Get statistics for a session"""
        profile = self.user_profiles.get(session_id, {})
        history = self.conversations.get(session_id, [])
        
        return {
            "total_messages": len(history),
            "total_interactions": profile.get('total_interactions', 0),
            "query_types": profile.get('query_types', {}),
            "topics_of_interest": profile.get('topics_of_interest', {}),
            "last_interaction": profile.get('last_interaction'),
            "has_summary": session_id in self.conversation_summaries
        }

# Global enhanced memory instance
enhanced_memory = EnhancedConversationMemory()
