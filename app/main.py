#!/usr/bin/env python3
"""
MAIN: Desktop GUI Chat Application
Run this to start the GUI chat application
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from controllers.chat_gui_controller import ChatGUIController


def main():
    """Main entry point for GUI app"""
    try:
        # Get API URL from environment or use default
        api_url = os.getenv("CHAT_API_URL", "http://localhost:8000/chat")
        session_id = os.getenv("SESSION_ID", "desktop-session")
        
        # Create controller and start GUI
        controller = ChatGUIController(api_url=api_url, session_id=session_id)
        controller.start()
        
        return 0
    
    except KeyboardInterrupt:
        return 0
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
