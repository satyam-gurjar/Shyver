"""
MODEL: LLM Integration
Handles communication with the language model
"""

import requests
from typing import Optional


class LLMModel:
    """Model for interacting with LLM (connects to your FastAPI server)"""
    
    def __init__(self, api_url: str = "http://localhost:8000/chat"):
        self.api_url = api_url
    
    def generate_response(self, session_id: str, message: str) -> Optional[str]:
        """
        Send message to LLM server and get response
        """
        try:
            payload = {
                "session_id": session_id,
                "message": message
            }
            
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("response", "")
            else:
                return f"Error: Server returned {response.status_code}"
                
        except requests.exceptions.ConnectionError:
            return "Error: Cannot connect to server. Make sure the server is running."
        except requests.exceptions.Timeout:
            return "Error: Request timed out."
        except Exception as e:
            return f"Error: {str(e)}"
