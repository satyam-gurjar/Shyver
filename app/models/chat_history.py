"""
MODEL: Chat History Storage
Handles data storage and retrieval for chat messages
"""

from typing import Dict, List


class ChatHistoryModel:
    """Model for managing chat history in memory"""
    
    def __init__(self):
        # Storage: {session_id: [{"role": "user/assistant", "content": "..."}]}
        self._history: Dict[str, List[dict]] = {}
    
    def get_history(self, session_id: str) -> List[dict]:
        """Get chat history for a session"""
        return self._history.get(session_id, [])
    
    def add_message(self, session_id: str, role: str, content: str) -> None:
        """Add a message to session history"""
        if session_id not in self._history:
            self._history[session_id] = []
        
        self._history[session_id].append({
            "role": role,
            "content": content
        })
        
        # Keep only last 50 messages
        if len(self._history[session_id]) > 50:
            self._history[session_id] = self._history[session_id][-50:]
    
    def clear_history(self, session_id: str) -> None:
        """Clear history for a session"""
        if session_id in self._history:
            del self._history[session_id]
    
    def get_all_sessions(self) -> List[str]:
        """Get list of all session IDs"""
        return list(self._history.keys())
