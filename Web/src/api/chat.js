// axios is used to send HTTP requests
import axios from "axios";

// Backend API URL
// Make sure FastAPI is running on this address
const API_URL = "http://localhost:8000/chat";

/**
 * Send user message to backend
 * @param {string} sessionId - unique chat session
 * @param {string} message - user input text
 * @returns {string} assistant response
 */
export async function sendMessage(sessionId, message) {
  // Send POST request to FastAPI controller
  const response = await axios.post(API_URL, {
    session_id: sessionId, // required by backend schema
    message: message       // user message
  });

  // Backend returns { response: "text" }
  return response.data.response;
}
