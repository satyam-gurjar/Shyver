import { useState } from "react";
import Message from "./Message";
import { sendMessage } from "../api/chat";

/**
 * ChatBox handles:
 * - messages state
 * - input box
 * - send button
 */
export default function ChatBox() {
  // Store all chat messages with default welcome messages
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content: "Hello! 👋 I'm your AI Assistant. How can I help you today?"
    }
  ]);

  // Store input text
  const [input, setInput] = useState("");

  // Loading state for API call
  const [isLoading, setIsLoading] = useState(false);

  // Theme state (light or dark)
  const [theme, setTheme] = useState("light");

  // Fixed session id for learning
  const sessionId = "local-llama-session";

  // Theme colors
  const colors = {
    light: {
      bg: "#ffffff",
      chatBg: "#f8fafc",
      chatGradient: "linear-gradient(to bottom, #f8fafc 0%, #f1f5f9 100%)",
      headerBg: "#ffffff",
      headerText: "#1e293b",
      headerBorder: "#e5e7eb",
      text: "#1e293b",
      textSecondary: "#64748b",
      border: "#e2e8f0",
      inputBg: "#ffffff",
      inputBorder: "#e2e8f0",
      assistantBg: "#f1f5f9",
      loadingBg: "#f1f5f9",
      shadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)"
    },
    dark: {
      bg: "#2d2d2d",
      chatBg: "#212121",
      chatGradient: "linear-gradient(to bottom, #212121 0%, #1a1a1a 100%)",
      headerBg: "#2d2d2d",
      headerText: "#ececec",
      headerBorder: "#3e3e3e",
      text: "#ececec",
      textSecondary: "#9ca3af",
      border: "#3e3e3e",
      inputBg: "#3a3a3a",
      inputBorder: "#4a4a4a",
      assistantBg: "#3a3a3a",
      loadingBg: "#3a3a3a",
      shadow: "0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -1px rgba(0, 0, 0, 0.2)"
    }
  };

  const currentColors = colors[theme];

  /**
   * Send message to backend
   */
  const handleSend = async () => {
    // Prevent empty message
    if (!input.trim() || isLoading) return;

    const userMessage = input;

    // Add user message to UI immediately
    setMessages(prev => [
      ...prev,
      { role: "user", content: userMessage }
    ]);

    // Clear input box
    setInput("");
    setIsLoading(true);

    try {
      // Call backend API
      const reply = await sendMessage(sessionId, userMessage);

      // Add assistant reply to UI
      setMessages(prev => [
        ...prev,
        { role: "assistant", content: reply }
      ]);
    } catch (error) {
      console.error("Error sending message:", error);
      setMessages(prev => [
        ...prev,
        { role: "assistant", content: "Sorry, I encountered an error. Please try again." }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div
      style={{
        width: "100%",
        maxWidth: "900px",
        height: "90vh",
        margin: "auto",
        display: "flex",
        flexDirection: "column",
        backgroundColor: currentColors.bg,
        borderRadius: "16px",
        boxShadow: currentColors.shadow,
        overflow: "hidden"
      }}
    >
      {/* Chat Header */}
      <div
        style={{
          padding: "20px 24px",
          backgroundColor: currentColors.headerBg,
          color: currentColors.headerText,
          borderBottom: `1px solid ${currentColors.headerBorder}`
        }}
      >
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
            <div
              style={{
                width: "40px",
                height: "40px",
                borderRadius: "50%",
                backgroundColor: "#10a37f",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: "20px"
              }}
            >
              🤖
            </div>
            <div>
              <h2 style={{ margin: 0, fontSize: "18px", fontWeight: "600", color: currentColors.headerText }}>AI Assistant</h2>
              <p style={{ margin: 0, fontSize: "13px", color: currentColors.textSecondary }}>Always here to help</p>
            </div>
          </div>
          <button
            onClick={() => setTheme(theme === "light" ? "dark" : "light")}
            style={{
              width: "36px",
              height: "36px",
              borderRadius: "8px",
              border: `1px solid ${currentColors.border}`,
              backgroundColor: currentColors.inputBg,
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: "18px",
              transition: "all 0.2s"
            }}
            onMouseEnter={e => e.target.style.backgroundColor = theme === "light" ? "#f3f4f6" : "#4a4a4a"}
            onMouseLeave={e => e.target.style.backgroundColor = currentColors.inputBg}
            title={theme === "light" ? "Switch to dark mode" : "Switch to light mode"}
          >
            {theme === "light" ? "🌙" : "☀️"}
          </button>
        </div>
      </div>

      {/* Chat messages area */}
      <div
        style={{
          flex: 1,
          padding: "24px",
          overflowY: "auto",
          backgroundColor: currentColors.chatBg,
          backgroundImage: currentColors.chatGradient
        }}
      >
        {messages.length === 0 ? (
          <div
            style={{
              height: "100%",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              color: currentColors.textSecondary,
              textAlign: "center"
            }}
          >
            <div style={{ fontSize: "48px", marginBottom: "16px" }}>💬</div>
            <h3 style={{ margin: "0 0 8px 0", fontSize: "18px", fontWeight: "600", color: currentColors.text }}>Start a conversation</h3>
            <p style={{ margin: 0, fontSize: "14px" }}>Send a message to begin chatting with the AI assistant</p>
          </div>
        ) : (
          messages.map((msg, index) => (
            <Message
              key={index}
              role={msg.role}
              content={msg.content}
              theme={theme}
            />
          ))
        )}
        {isLoading && (
          <div style={{ display: "flex", justifyContent: "flex-start", marginBottom: "10px" }}>
            <div
              style={{
                padding: "12px 16px",
                borderRadius: "16px",
                backgroundColor: currentColors.loadingBg,
                color: currentColors.textSecondary,
                fontSize: "14px",
                boxShadow: theme === "light" ? "0 1px 2px 0 rgba(0, 0, 0, 0.05)" : "none"
              }}
            >
              <span style={{ display: "inline-block", animation: "pulse 1.5s ease-in-out infinite" }}>●</span>
              <span style={{ display: "inline-block", animation: "pulse 1.5s ease-in-out infinite 0.2s" }}>●</span>
              <span style={{ display: "inline-block", animation: "pulse 1.5s ease-in-out infinite 0.4s" }}>●</span>
            </div>
          </div>
        )}
      </div>

      {/* Input area */}
      <div
        style={{
          padding: "16px 24px",
          backgroundColor: currentColors.bg,
          borderTop: `1px solid ${currentColors.border}`
        }}
      >
        <div style={{ display: "flex", gap: "12px", alignItems: "flex-end" }}>
          <input
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder="Type your message..."
            disabled={isLoading}
            style={{
              flex: 1,
              padding: "14px 16px",
              fontSize: "15px",
              borderRadius: "12px",
              border: `2px solid ${currentColors.inputBorder}`,
              outline: "none",
              transition: "border-color 0.2s",
              backgroundColor: isLoading ? currentColors.chatBg : currentColors.inputBg,
              color: currentColors.text
            }}
            onFocus={e => e.target.style.borderColor = "#10a37f"}
            onBlur={e => e.target.style.borderColor = currentColors.inputBorder}
            onKeyDown={e => {
              // Send message when Enter is pressed
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
          />

          <button
            onClick={handleSend}
            disabled={isLoading || !input.trim()}
            style={{
              padding: "14px 24px",
              backgroundColor: isLoading || !input.trim() ? (theme === "light" ? "#cbd5e1" : "#4a4a4a") : "#10a37f",
              color: "white",
              border: "none",
              borderRadius: "12px",
              cursor: isLoading || !input.trim() ? "not-allowed" : "pointer",
              fontSize: "15px",
              fontWeight: "600",
              transition: "all 0.2s",
              boxShadow: isLoading || !input.trim() ? "none" : "0 1px 2px 0 rgba(0, 0, 0, 0.05)"
            }}
            onMouseEnter={e => {
              if (!isLoading && input.trim()) {
                e.target.style.backgroundColor = "#0d8a6a";
                e.target.style.transform = "translateY(-1px)";
                e.target.style.boxShadow = "0 4px 6px -1px rgba(0, 0, 0, 0.1)";
              }
            }}
            onMouseLeave={e => {
              if (!isLoading && input.trim()) {
                e.target.style.backgroundColor = "#10a37f";
                e.target.style.transform = "translateY(0)";
                e.target.style.boxShadow = "0 1px 2px 0 rgba(0, 0, 0, 0.05)";
              }
            }}
          >
            {isLoading ? "Sending..." : "Send"}
          </button>
        </div>
      </div>
    </div>
  );
}
