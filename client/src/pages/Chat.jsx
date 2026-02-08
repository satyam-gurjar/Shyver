import ChatBox from "../components/ChatBox";

/**
 * Chat Page
 * This acts like a screen/page in the app
 */
export default function Chat() {
  return (
    <div
      style={{
        height: "100vh",
        background: "#343541",
        padding: "20px",
        display: "flex",
        flexDirection: "column"
      }}
    >
      {/* Main chat component */}
      <ChatBox />
    </div>
  );
}
