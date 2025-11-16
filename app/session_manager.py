"""Session manager for tracking agent sessions and their status."""
import uuid
from typing import Dict, Optional
from threading import Lock


class SessionManager:
    """Manages agent sessions and their state."""
    
    def __init__(self):
        self._sessions: Dict[str, 'SessionState'] = {}
        self._lock = Lock()
    
    def create_session(self) -> str:
        """Create a new session and return its ID."""
        session_id = str(uuid.uuid4())
        with self._lock:
            self._sessions[session_id] = SessionState(session_id)
        return session_id
    
    def get_session(self, session_id: str) -> Optional['SessionState']:
        """Get a session by ID."""
        with self._lock:
            return self._sessions.get(session_id)
    
    def update_session(self, session_id: str, response: str, answer: str, complete: bool):
        """Update session with new response and completion status."""
        with self._lock:
            if session_id in self._sessions:
                self._sessions[session_id].response = response
                self._sessions[session_id].complete = complete
                self._sessions[session_id].answer = answer


class SessionState:
    """Represents the state of an agent session."""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.response: str = ""
        self.answer: str = ""
        self.complete: bool = False

