"""
CONTROLLER: GUI Chat Logic
Handles business logic and coordinates between Model and GUI View
"""

from models.chat_history import ChatHistoryModel
from models.llm_model import LLMModel
from models.voice_service import VoiceService
from views.chat_gui_view import ChatGUIView
import time


class ChatGUIController:
    """Controller for managing GUI chat application logic"""
    
    def __init__(self, api_url: str = "http://localhost:8000/chat", session_id: str = "default-session"):
        self.history_model = ChatHistoryModel()
        self.llm_model = LLMModel(api_url)
        self.voice_service = VoiceService(pause_threshold=2.0, timeout=10)
        self.view = ChatGUIView("Chat Assistant")
        self.current_session = session_id
        
        # Connect view callbacks
        self.view.on_send = self.handle_send_message
        self.view.on_clear = self.handle_clear_history
        self.view.on_close = self.handle_close
        self.view.on_speak = self.handle_voice_input
        
        # Load existing history
        self._load_history()
    
    def _load_history(self):
        """Load existing chat history"""
        history = self.history_model.get_history(self.current_session)
        if history:
            self.view.display_history(history)
            self.view.set_status(f"Session: {self.current_session} ({len(history)} messages)")
        else:
            self.view.set_status(f"Session: {self.current_session}")
    
    def handle_send_message(self, message: str):
        """Handle sending a message"""
        try:
            # Display user message immediately
            self.view.display_message("user", message)
            
            # Add to history
            self.history_model.add_message(self.current_session, "user", message)
            
            # Get response from LLM (this may take time)
            self.view.set_status("Thinking...")
            response = self.llm_model.generate_response(self.current_session, message)
            
            if response:
                # Add assistant response to history
                self.history_model.add_message(self.current_session, "assistant", response)
                
                # Display response (use after() to ensure thread safety)
                self.view.root.after(0, lambda: self._display_bot_response(response))
            else:
                self.view.root.after(0, lambda: self._display_error("Failed to get response from server"))
        
        except Exception as e:
            self.view.root.after(0, lambda: self._display_error(f"Error: {str(e)}"))
        
        finally:
            # Re-enable input
            self.view.root.after(0, self._reset_ui)
    
    def _display_bot_response(self, response: str):
        """Thread-safe bot response display"""
        self.view.display_message("bot", response)
        history = self.history_model.get_history(self.current_session)
        self.view.set_status(f"Session: {self.current_session} ({len(history)} messages)")
    
    def _display_error(self, error_msg: str):
        """Thread-safe error display"""
        self.view.display_message("error", error_msg)
        self.view.set_status("Error occurred")
    
    def _reset_ui(self):
        """Reset UI to ready state"""
        self.view.enable_input()
        self.view.set_status(f"Session: {self.current_session}")
        self.view.message_entry.focus()
    
    def handle_voice_input(self):
        """Handle voice input"""
        try:
            # Listen for voice input
            success, message = self.voice_service.listen()
            
            if success:
                # Display and process the transcribed message
                self.view.root.after(0, lambda: self.view.display_message("user", f"🎤 {message}"))
                
                # Add to history
                self.history_model.add_message(self.current_session, "user", message)
                
                # Get response from LLM
                self.view.root.after(0, lambda: self.view.set_status("Thinking..."))
                response = self.llm_model.generate_response(self.current_session, message)
                
                if response:
                    # Add response to history
                    self.history_model.add_message(self.current_session, "assistant", response)
                    
                    # Display response
                    self.view.root.after(0, lambda: self.view.display_message("bot", response))
                    
                    # Speak the response
                    self.view.root.after(0, lambda: self.view.set_status("Speaking..."))
                    self.voice_service.speak(response)
                    
                    # Update status
                    history = self.history_model.get_history(self.current_session)
                    self.view.root.after(0, lambda: self.view.set_status(f"Session: {self.current_session} ({len(history)} messages)"))
                else:
                    self.view.root.after(0, lambda: self._display_error("Failed to get response from server"))
            else:
                # Display error
                self.view.root.after(0, lambda: self.view.display_message("error", message))
        
        except Exception as e:
            self.view.root.after(0, lambda: self._display_error(f"Voice error: {str(e)}"))
        
        finally:
            # Re-enable input
            self.view.root.after(0, self._reset_ui)
    
    def handle_clear_history(self):
        """Handle clearing chat history"""
        self.history_model.clear_history(self.current_session)
        self.view.clear_chat()
        self.view.display_message("system", "Chat history cleared!")
        self.view.set_status(f"Session: {self.current_session} (0 messages)")
    
    def handle_close(self):
        """Handle application close"""
        # Save state or cleanup if needed
        pass
    
    def start(self):
        """Start the GUI application"""
        self.view.run()
