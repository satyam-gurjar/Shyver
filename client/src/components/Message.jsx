/**
 * Message component
 * Used for both user and assistant messages
 */

export default function Message({ role, content, theme = "light" }) {
  // Decide message alignment based on role
  const isUser = role === "user";

  // Theme colors for messages
  const colors = {
    light: {
      assistantBg: "#f1f5f9",
      assistantText: "#1e293b",
      userBg: "#10a37f",
      userText: "#ffffff",
      avatarBg: "#10a37f",
      userAvatarBg: "#8b5cf6",
      shadow: "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
      userShadow: "0 2px 4px rgba(16, 163, 127, 0.2)"
    },
    dark: {
      assistantBg: "#3a3a3a",
      assistantText: "#ececec",
      userBg: "#10a37f",
      userText: "#ffffff",
      avatarBg: "#10a37f",
      userAvatarBg: "#8b5cf6",
      shadow: "0 1px 2px 0 rgba(0, 0, 0, 0.3)",
      userShadow: "0 2px 4px rgba(16, 163, 127, 0.3)"
    }
  };

  const currentColors = colors[theme];

  return (
    <div
      style={{
        display: "flex",
        justifyContent: isUser ? "flex-end" : "flex-start",
        marginBottom: "16px",
        animation: "slideIn 0.3s ease-out"
      }}
    >
      <div
        style={{
          display: "flex",
          gap: "10px",
          maxWidth: "75%",
          alignItems: "flex-start"
        }}
      >
        {!isUser && (
          <div
            style={{
              width: "32px",
              height: "32px",
              borderRadius: "50%",
              backgroundColor: currentColors.avatarBg,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: "16px",
              flexShrink: 0
            }}
          >
            🤖
          </div>
        )}
        <div
          style={{
            padding: "12px 16px",
            borderRadius: isUser ? "16px 16px 4px 16px" : "16px 16px 16px 4px",
            backgroundColor: isUser ? currentColors.userBg : currentColors.assistantBg,
            color: isUser ? currentColors.userText : currentColors.assistantText,
            fontSize: "15px",
            lineHeight: "1.6",
            boxShadow: isUser ? currentColors.userShadow : currentColors.shadow,
            wordWrap: "break-word",
            whiteSpace: "pre-wrap"
          }}
        >
          {content}
        </div>
        {isUser && (
          <div
            style={{
              width: "32px",
              height: "32px",
              borderRadius: "50%",
              backgroundColor: currentColors.userAvatarBg,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: "16px",
              flexShrink: 0
            }}
          >
            👤
          </div>
        )}
      </div>
    </div>
  );
}
