#!/usr/bin/env python3
"""
Quick build script - builds executable for current platform
"""

import subprocess
import sys
import os

def main():
    print("=" * 60)
    print("  Building Chat Assistant Executable")
    print("=" * 60)
    print()
    
    # Check if pyinstaller is installed
    try:
        import PyInstaller
        print("✓ PyInstaller is installed")
    except ImportError:
        print("✗ PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✓ PyInstaller installed")
    
    print()
    print("Building executable...")
    print()
    
    # Run PyInstaller
    result = subprocess.run([
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--onefile",
        "--windowed",
        "--name=ChatAssistant",
        "--hidden-import=tkinter",
        "--hidden-import=tkinter.ttk", 
        "--hidden-import=tkinter.scrolledtext",
        "--hidden-import=requests",
        "--hidden-import=speech_recognition",
        "--hidden-import=pyttsx3",
        "--hidden-import=pyaudio",
        "main_gui.py"
    ])
    
    if result.returncode == 0:
        print()
        print("=" * 60)
        print("✅ Build Successful!")
        print("=" * 60)
        print()
        print(f"Executable location: {os.path.join('dist', 'ChatAssistant')}")
        print()
        
        if sys.platform.startswith('linux'):
            print("To run:")
            print("  ./dist/ChatAssistant")
        elif sys.platform.startswith('darwin'):
            print("To run:")
            print("  ./dist/ChatAssistant")
        elif sys.platform.startswith('win'):
            print("To run:")
            print("  dist\\ChatAssistant.exe")
        
        print()
    else:
        print()
        print("❌ Build failed!")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
