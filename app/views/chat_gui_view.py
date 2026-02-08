"""
VIEW: GUI Chat Interface using Tkinter
Handles all UI/display logic for desktop application
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from typing import List, Callable, Optional
import threading


class ChatGUIView:
    """Desktop GUI view for chat application"""
    
    def __init__(self, title: str = "Chat Assistant"):
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry("700x600")
        self.root.minsize(600, 500)
        
        # Callbacks
        self.on_send: Optional[Callable[[str], None]] = None
        self.on_clear: Optional[Callable[[], None]] = None
        self.on_close: Optional[Callable[[], None]] = None
        self.on_speak: Optional[Callable[[], None]] = None
        
        self._setup_ui()
        self._setup_protocol()
        
    def _setup_ui(self):
        """Setup the GUI layout"""
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="🤖 Chat Assistant",
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, pady=(0, 10))
        
        # Chat display area (scrollable)
        chat_frame = ttk.Frame(main_frame)
        chat_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        chat_frame.columnconfigure(0, weight=1)
        chat_frame.rowconfigure(0, weight=1)
        
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            width=60,
            height=20,
            font=("Arial", 10),
            state='disabled',
            bg="#f5f5f5",
            padx=10,
            pady=10
        )
        self.chat_display.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure text tags for styling
        self.chat_display.tag_config("user", foreground="#0066cc", font=("Arial", 10, "bold"))
        self.chat_display.tag_config("bot", foreground="#009900", font=("Arial", 10, "bold"))
        self.chat_display.tag_config("system", foreground="#666666", font=("Arial", 9, "italic"))
        self.chat_display.tag_config("error", foreground="#cc0000")
        
        # Input area
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        input_frame.columnconfigure(0, weight=1)
        
        self.message_entry = ttk.Entry(input_frame, font=("Arial", 11))
        self.message_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        self.message_entry.bind('<Return>', lambda e: self._handle_send())
        
        self.send_button = ttk.Button(
            input_frame,
            text="Send",
            command=self._handle_send,
            width=10
        )
        self.send_button.grid(row=0, column=1)
        
        self.speak_button = ttk.Button(
            input_frame,
            text="🎤 Speak",
            command=self._handle_speak,
            width=12
        )
        self.speak_button.grid(row=0, column=2, padx=(10, 0))
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, pady=(10, 0))
        
        ttk.Button(
            button_frame,
            text="Clear Chat",
            command=self._handle_clear,
            width=12
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Quit",
            command=self._handle_quit,
            width=12
        ).pack(side=tk.LEFT, padx=5)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(
            main_frame,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            font=("Arial", 9)
        )
        status_bar.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Focus on input
        self.message_entry.focus()
    
    def _setup_protocol(self):
        """Setup window close protocol"""
        self.root.protocol("WM_DELETE_WINDOW", self._handle_quit)
    
    def _handle_send(self):
        """Handle send button click"""
        message = self.message_entry.get().strip()
        if message and self.on_send:
            self.message_entry.delete(0, tk.END)
            self.set_status("Sending...")
            self.disable_input()
            # Run in thread to avoid blocking UI
            threading.Thread(target=self.on_send, args=(message,), daemon=True).start()
    
    def _handle_speak(self):
        """Handle speak button click"""
        if self.on_speak:
            self.set_status("Listening...")
            self.disable_input()
            # Run in thread to avoid blocking UI
            threading.Thread(target=self.on_speak, daemon=True).start()
    
    def _handle_clear(self):
        """Handle clear button click"""
        if messagebox.askyesno("Clear Chat", "Clear all chat history?"):
            if self.on_clear:
                self.on_clear()
    
    def _handle_quit(self):
        """Handle quit button/window close"""
        if messagebox.askyesno("Quit", "Are you sure you want to quit?"):
            if self.on_close:
                self.on_close()
            self.root.quit()
    
    def display_message(self, role: str, content: str):
        """Display a message in the chat"""
        self.chat_display.config(state='normal')
        
        if role == "user":
            self.chat_display.insert(tk.END, "You: ", "user")
            self.chat_display.insert(tk.END, f"{content}\n\n")
        elif role == "bot":
            self.chat_display.insert(tk.END, "Assistant: ", "bot")
            self.chat_display.insert(tk.END, f"{content}\n\n")
        elif role == "system":
            self.chat_display.insert(tk.END, f"ℹ️  {content}\n\n", "system")
        elif role == "error":
            self.chat_display.insert(tk.END, f"❌ {content}\n\n", "error")
        
        self.chat_display.config(state='disabled')
        self.chat_display.see(tk.END)
    
    def display_history(self, history: List[dict]):
        """Display chat history"""
        self.clear_chat()
        for msg in history:
            role = "user" if msg["role"] == "user" else "bot"
            self.display_message(role, msg["content"])
    
    def clear_chat(self):
        """Clear the chat display"""
        self.chat_display.config(state='normal')
        self.chat_display.delete(1.0, tk.END)
        self.chat_display.config(state='disabled')
    
    def set_status(self, status: str):
        """Update status bar"""
        self.status_var.set(status)
    
    def enable_input(self):
        """Enable input controls"""
        self.message_entry.config(state='normal')
        self.send_button.config(state='normal')
        self.speak_button.config(state='normal')
    
    def disable_input(self):
        """Disable input controls"""
        self.message_entry.config(state='disabled')
        self.send_button.config(state='disabled')
        self.speak_button.config(state='disabled')
    
    def show_error(self, message: str):
        """Show error dialog"""
        messagebox.showerror("Error", message)
    
    def show_info(self, message: str):
        """Show info dialog"""
        messagebox.showinfo("Information", message)
    
    def run(self):
        """Start the GUI main loop"""
        self.display_message("system", "Welcome! Type a message to start chatting.")
        self.root.mainloop()
