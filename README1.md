# Multi‑Platform AI Chat Assistant

Monorepo for a **local LLaMA-based chat assistant** with:

- **Backend API** – FastAPI + LangChain + Ollama ([Server/](Server))
- **Desktop client** – Tkinter GUI with speech recognition & TTS ([app/](app))
- **Android mobile app** – Expo + React Native ([android/](android))
- **Web client** – React + Vite SPA ([Web/](Web))

All clients talk to the same `/chat` API and share **session-based chat history**.


---

## 1. High‑Level Architecture

```text
+-----------------+       HTTP        +------------------+        Local LLM
|  Web Client     |  POST /chat --->  |                  |   +------------------+
|  (React, Vite)  |                   |                  |   |  Ollama (phi3)   |
+-----------------+                   |  FastAPI Server  |   | + LangChain LLM  |
                                      |  (Server/)       |--->| [Server/app/... ]|
+-----------------+       HTTP        |                  |   +------------------+
| Android Client  |  POST /chat --->  |                  |
| (Expo RN)       |                   +------------------+
+-----------------+                    ^
                                       | in‑memory
+-----------------+       HTTP         | chat history
| Desktop Client  |  POST /chat------> |
| (Tkinter + SR)  |                    |
+-----------------+                    |
                                       v
                                [chat_sessions] (per session_id)
```


---

## 2. Project Structure

```text
Assistant/
├── app/                    # Desktop GUI client (Tkinter + Voice)
│   ├── main.py
│   ├── build.py
│   ├── requirements.txt
│   ├── README.md
│   ├── controllers/
│   │   └── chat_gui_controller.py
│   ├── models/
│   │   ├── chat_history.py
│   │   ├── llm_model.py
│   │   └── voice_service.py
│   └── views/
│       └── chat_gui_view.py
│
├── Server/                 # FastAPI backend (local LLaMA via Ollama)
│   ├── requirment.txt
│   ├── test_chat.py
│   └── app/
│       ├── main.py
│       ├── controllers/
│       │   └── chat_controller.py
│       ├── model/
│       │   ├── chat_memory.py
│       │   ├── llm_model.py
│       │   └── schemas.py
│       └── services/
│           └── chat_service.py
│
├── Web/                    # Web SPA client (React + Vite)
│   ├── package.json
│   ├── vite.config.js
│   ├── eslint.config.js
│   ├── index.html
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── index.css
│       ├── api/
│       │   └── chat.js
│       ├── pages/
│       │   └── Chat.jsx
│       └── components/
│           ├── ChatBox.jsx
│           └── Message.jsx
│
├── android/                # Android app (Expo + React Native + router)
│   ├── app.json
│   ├── package.json
│   ├── tsconfig.json
│   ├── metro.config.js
│   ├── eslint.config.js
│   ├── .expo/
│   ├── .vscode/
│   ├── hooks/
│   ├── constants/
│   ├── components/
│   └── app/
│       ├── _layout.tsx
│       ├── modal.tsx
│       └── (tabs)/
│           ├── _layout.tsx
│           ├── index.tsx
│           └── explore.tsx
│
├── .gitignore              # Root ignore rules
└── android/.gitignore      # Android‑specific ignore rules
```


---

## 3. Backend API – FastAPI (Server/)

### 3.1 Purpose

The backend provides:

- A **REST `/chat` endpoint** for all clients.
- A **WebSocket `/ws` endpoint** for potential real‑time chat.
- Integration with a **local LLaMA model (`phi3`) via Ollama** using LangChain.
- Simple **in‑memory session-based chat history**.

### 3.2 Key files

- **[Server/app/main.py](Server/app/main.py)**  
  - Creates the FastAPI app instance.
  - Adds CORS middleware (`allow_origins=["*"]`) so Web/Android/Desktop can call it in dev.
  - Includes the chat router from [`app.controllers.chat_controller`](Server/app/controllers/chat_controller.py).

- **[Server/app/controllers/chat_controller.py](Server/app/controllers/chat_controller.py)**  
  - Defines the router `router = APIRouter()`.

  - `POST /chat`  
    - Accepts a [`ChatRequest`](Server/app/model/schemas.py) body.
    - Delegates to [`process_chat`](Server/app/services/chat_service.py).
    - Returns `{ "response": "<assistant text>" }`.

  - `WebSocket /ws`  
    - Accepts JSON messages with `session_id` and `message`.
    - For each message, calls `process_chat` and sends back `{ "response": ... }`.
    - Handles `WebSocketDisconnect` gracefully.

- **[Server/app/model/schemas.py](Server/app/model/schemas.py)**  
  - Defines `ChatRequest` Pydantic model:
    - `session_id: str`
    - `message: str`

- **[Server/app/services/chat_service.py](Server/app/services/chat_service.py)**  
  - `process_chat(session_id: str, user_message: str) -> str`:
    1. Fetches previous messages from [`get_chat_history`](Server/app/model/chat_memory.py).
    2. Builds a prompt string with all `role: content` lines.
    3. Appends the new `user` message and an `assistant:` prefix.
    4. Calls [`generate_response`](Server/app/model/llm_model.py) with the prompt.
    5. Persists both user and assistant messages using [`save_message`](Server/app/model/chat_memory.py).
    6. Returns the assistant reply.

- **[Server/app/model/chat_memory.py](Server/app/model/chat_memory.py)**  
  - Simple in‑memory store:
    - `chat_sessions: dict[session_id, list[{"role","content"}]]`.
  - `get_chat_history(session_id)` returns list of messages or `[]`.
  - `save_message(session_id, role, content)` appends to `chat_sessions[session_id]`.
  - No persistence (memory only), but clean separation for future DB integration.

- **[Server/app/model/llm_model.py](Server/app/model/llm_model.py)**  
  - Integrates with **Ollama** using `langchain_community.llms.Ollama`.
  - Tries to instantiate `llm = Ollama(model="phi3:latest", base_url="http://localhost:11434", temperature=0.5)`.
    - Sets `OLLAMA_AVAILABLE = True` if successful, otherwise `False`.
  - Defines `MOCK_RESPONSES` as friendly fallback strings when Ollama is not available.
  - `generate_response(prompt: str) -> str`:
    - If `OLLAMA_AVAILABLE`, calls `llm.invoke(prompt)`.
    - Otherwise (or on error), logs and returns a random fallback from `MOCK_RESPONSES`.

- **[Server/test_chat.py](Server/test_chat.py)**  
  - Simple CLI client to test `/chat`:
    - Uses `urllib` to POST to `API_URL` (`CHAT_API_URL` env or `http://localhost:8000/chat`).
    - Prompts for `session_id` and then reads user input in a loop.
    - Prints model replies and handles HTTP/connection errors cleanly.

- **[Server/requirment.txt](Server/requirment.txt)**  
  Backend dependencies:
  - `fastapi` – web framework for building the REST and WebSocket APIs.
  - `uvicorn` – ASGI server to run FastAPI.
  - `langchain` / `langchain-community` – convenience layer to talk to Ollama models.
  - `ollama` – Python client for the local Ollama server.
  - `pydantic` – data validation/models (used by FastAPI & `ChatRequest`).

### 3.3 Backend workflow

1. Client sends `POST /chat` with:
   ```json
   { "session_id": "<id>", "message": "<user text>" }
   ```
2. FastAPI parses request into `ChatRequest`.
3. [`process_chat`](Server/app/services/chat_service.py) builds a prompt using **past messages + current user message**.
4. [`generate_response`](Server/app/model/llm_model.py) calls **Ollama phi3** or fallback.
5. Chat history for that `session_id` is updated.
6. JSON response `{ "response": "<assistant text>" }` is returned.


---

## 4. Desktop GUI Client – Tkinter (app/)

### 4.1 Purpose

A **desktop chat app with voice input and voice output**:

- Text UI built with **Tkinter**.
- Voice input via **SpeechRecognition + PyAudio + (Google / PocketSphinx)**.
- Text‑to‑speech via **pyttsx3**.
- Talks to the same FastAPI `/chat` endpoint.
- Uses a simple MVC‑ish separation: **models / views / controllers**.

### 4.2 Key files

- **[app/main.py](app/main.py)**  
  - Entry point for the GUI app.
  - Determines API URL and session ID from environment:
    - `CHAT_API_URL` (default `http://localhost:8000/chat`)
    - `SESSION_ID` (default `"desktop-session"`)
  - Creates [`ChatGUIController`](app/controllers/chat_gui_controller.py) and calls `controller.start()`.

- **[app/controllers/chat_gui_controller.py](app/controllers/chat_gui_controller.py)** – Controller layer  
  - Coordinates:
    - [`ChatHistoryModel`](app/models/chat_history.py)
    - [`LLMModel`](app/models/llm_model.py)
    - [`VoiceService`](app/models/voice_service.py)
    - [`ChatGUIView`](app/views/chat_gui_view.py)
  - Constructor:
    - Instantiates models and view.
    - Binds view callbacks:
      - `on_send` → `handle_send_message`
      - `on_clear` → `handle_clear_history`
      - `on_close` → `handle_close`
      - `on_speak` → `handle_voice_input`
    - Calls `_load_history()` to preload any existing history.

  - `handle_send_message(message: str)`:
    - Immediately displays user message.
    - Saves to history (role `"user"`).
    - Calls `self.llm_model.generate_response(...)` (network call).
    - On success:
      - Saves assistant message (role `"assistant"`).
      - Uses `view.root.after(0, ...)` to safely update TK UI from worker thread.
    - Always re‑enables input via `_reset_ui`.

  - `handle_voice_input()`:
    - Calls `self.voice_service.listen()` in background.
    - On success:
      - Shows transcribed voice message.
      - Sends to backend (same as text path).
      - Displays assistant reply.
      - Calls `voice_service.speak(response)` to read it aloud.
    - Handles errors gracefully and updates status bar.

  - `handle_clear_history()`:
    - Clears history for current session id.
    - Clears the UI and shows a system message.

  - `start()`:
    - Just `self.view.run()` (starts Tk main loop).

- **[app/views/chat_gui_view.py](app/views/chat_gui_view.py)** – View (Tkinter GUI)  
  - Encapsulates all GUI setup:
    - Window size, title, layout.
    - `ScrolledText` chat area.
    - Input entry + "Send" and "Speak" buttons.
    - "Clear Chat" and "Quit" buttons.
    - Status bar.
  - Uses text tags to style roles (`user`, `bot`, `system`, `error`).
  - Exposes callback slots: `on_send`, `on_clear`, `on_close`, `on_speak`.
  - Provides methods used by the controller:
    - `display_message(role, content)`
    - `display_history(history)`
    - `clear_chat()`
    - `set_status(text)`
    - `enable_input()`, `disable_input()`
    - `show_error()`, `show_info()`
    - `run()` – starts Tk main loop and shows a welcome message.

- **[app/models/chat_history.py](app/models/chat_history.py)** – Chat history model  
  - `ChatHistoryModel`:
    - In‑memory `Dict[str, List[{"role","content"}]]`.
    - `get_history(session_id)` / `add_message` / `clear_history` / `get_all_sessions`.
    - Keeps last 50 messages per session (drops older ones).

- **[app/models/llm_model.py](app/models/llm_model.py)** – Client for FastAPI backend  
  - `LLMModel(api_url="http://localhost:8000/chat")`:
    - `generate_response(session_id, message) -> Optional[str]`:
      - Sends `POST` to backend with `{"session_id", "message"}` using `requests`.
      - Timeout = 120s.
      - On status 200, returns `json["response"]`.
      - On error, returns an `"Error: ..."` string, so UI can display it.

- **[app/models/voice_service.py](app/models/voice_service.py)** – Voice input/output  
  - Uses `speech_recognition.Recognizer` with tuned thresholds:
    - `pause_threshold`, `phrase_threshold`, `non_speaking_duration`.
    - Dynamic energy threshold for ambient noise.
  - `listen() -> (bool, str)`:
    - Calibrates microphone with `adjust_for_ambient_noise`.
    - Listens with timeout and phrase time limit.
    - Recognizes with:
      - `recognize_google` (online, good quality).
      - Fallback `recognize_sphinx` (offline).
    - Returns `(True, text)` or `(False, error_message)`.

  - `speak(text: str) -> bool`:
    - Uses `pyttsx3` to speak text.
    - Configures rate, volume, and voice in `_configure_tts()`.

  - Additional helpers:
    - `test_microphone()`
    - `list_microphones()`
    - `set_microphone(device_index)`
    - `set_voice(voice_index)`
    - `set_rate(rate)`
    - `set_volume(volume)`

- **[app/build.py](app/build.py)** – Build desktop executable  
  - Checks/installs `PyInstaller`.
  - Runs PyInstaller with:
    - `--onefile`, `--windowed`, `--name=ChatAssistant`
    - Hidden imports for Tkinter, requests, speech recognition, TTS libraries.
  - Outputs executable into `dist/ChatAssistant`.
  - Prints platform‑specific run instructions.

- **[app/requirements.txt](app/requirements.txt)**  
  Desktop dependencies:
  - `requests` – HTTP client to call FastAPI.
  - `pyinstaller` – to build binary.
  - `SpeechRecognition` – speech‑to‑text.
  - `pyttsx3` – offline TTS.
  - `pyaudio` – microphone access.
  - `pocketsphinx` – offline speech recognition backend.

- **[app/README.md](app/README.md)**  
  - Quick start for desktop app.
  - Build instructions and troubleshooting tips (mic, TTS, build).


---

## 5. Android Mobile App – Expo + React Native (android/)

### 5.1 Purpose

A **mobile chat client** built with **Expo Router** and **React Native**, currently with:

- A primary chat screen under `(tabs)/index.tsx`.
- Standard Expo starter screens under `(tabs)/explore.tsx` and `modal.tsx`.
- Tailored UI for chat messages, with basic status and error handling.

### 5.2 Key files

- **[android/app.json](android/app.json)**  
  - Expo app configuration:
    - Name, slug, icons, splash screen.
    - Android package: `com.satya.voicechatbot`.
    - Network & permission settings:
      - `"usesCleartextTraffic": true` to allow HTTP calls (non‑HTTPS) to local backend.
      - `"android.permission.RECORD_AUDIO"` for future voice features.
    - iOS speech and mic usage descriptions.
    - Web output and favicon.
    - Plugins: `expo-router`, `expo-splash-screen`.
    - Experiments: `typedRoutes`, `reactCompiler`.

- **[android/package.json](android/package.json)**  
  - Scripts:
    - `npm start` / `npx expo start` – dev server.
    - `android`, `ios`, `web` – platform builds.
    - `reset-project` – runs the template reset script.
  - Important dependencies:
    - `expo`, `react`, `react-native` – core app platform.
    - `expo-router` – file‑based routing.
    - `expo-av`, `expo-speech`, `expo-haptics`, `expo-image`, etc. – media, UI utilities.
    - `@react-navigation/*` – navigation.
    - `react-native-reanimated`, `react-native-gesture-handler`, etc. – animations and gestures.

- **[android/app/_layout.tsx](android/app/_layout.tsx)**  
  - Root layout for Expo Router:
    - Wraps app in `ThemeProvider` with light/dark themes.
    - Defines stack navigator:
      - `(tabs)` as main screen.
      - `modal` as modal screen.
    - Configures status bar.

- **[android/app/(tabs)/_layout.tsx](android/app/(tabs)/_layout.tsx)**  
  - Defines bottom tab navigation:
    - `index` tab (Home).
    - `explore` tab (Explore).
  - Uses [`HapticTab`](android/components/haptic-tab.tsx) and [`IconSymbol`](android/components/ui/icon-symbol.tsx).
  - Colors depend on current color scheme (light/dark) from [`useColorScheme`](android/hooks/use-color-scheme.ts).

- **[android/app/(tabs)/index.tsx](android/app/(tabs)/index.tsx)** – Chat screen  
  - Pure React Native chat UI that:
    - Maintains `messages`, `input`, `isProcessing` state.
    - Uses `FlatList` to render messages.
    - Sends messages to the backend using `fetch`:
      - URL: `http://172.25.71.230:8000/chat` (currently hard‑coded).
      - Body: `{ session_id: <ref>, message: <text> }`.
    - On success:
      - Adds bot message to `messages`.
    - On error:
      - Logs and shows a user‑friendly error message in chat.
    - UI details:
      - Header with title and status text.
      - Input box with send button.
      - Message bubbles for user (right) and bot (left).
      - Timestamps derived from message `id` (using `Date.now()`).

- **[android/app/(tabs)/explore.tsx](android/app/(tabs)/explore.tsx)**  
  - Example screen from Expo template:
    - Shows collapsible sections explaining:
      - File-based routing.
      - Platform support.
      - Images, theming, animations.
    - Uses [`Collapsible`](android/components/ui/collapsible.tsx), [`ParallaxScrollView`](android/components/parallax-scroll-view.tsx), [`ThemedText`](android/components/themed-text.tsx), etc.

- **[android/app/modal.tsx](android/app/modal.tsx)**  
  - Simple modal screen with a link back to home.

- **Hooks & UI Components**
  - [`android/hooks/use-color-scheme.ts`](android/hooks/use-color-scheme.ts) and `.web.ts` – abstraction for color scheme.
  - [`android/hooks/use-theme-color.ts`](android/hooks/use-theme-color.ts) – maps theme names to palette in [`android/constants/theme.ts`](android/constants/theme.ts).
  - [`android/components/themed-view.tsx`](android/components/themed-view.tsx) and [`themed-text.tsx`](android/components/themed-text.tsx) – theme-aware wrappers.
  - [`android/components/parallax-scroll-view.tsx`](android/components/parallax-scroll-view.tsx) – header parallax effect using `react-native-reanimated`.
  - [`android/components/hello-wave.tsx`](android/components/hello-wave.tsx) – simple animated text example.
  - [`android/components/haptic-tab.tsx`](android/components/haptic-tab.tsx) – tab button with haptic feedback on iOS.
  - [`android/components/external-link.tsx`](android/components/external-link.tsx) – link wrapper that opens in-app browser on native.

- **Tooling & meta**
  - [`android/tsconfig.json`](android/tsconfig.json) – TypeScript config (extends Expo base).
  - [`android/eslint.config.js`](android/eslint.config.js) – ESLint configuration.
  - [`android/metro.config.js`](android/metro.config.js) – Metro bundler config using `expo/metro-config`.
  - [`android/.gitignore`](android/.gitignore) – ignore node_modules, build, native artifacts, app-example, etc.
  - [`android/scripts/reset-project.js`](android/scripts/reset-project.js) – helper to reset template structure.

### 5.3 Android chat flow

1. User types a message in the input box.
2. `sendMessageToBot` creates a user message object and appends it to `messages`.
3. It sends `POST` to `http://172.25.71.230:8000/chat` with `session_id` and `message`.
4. On success, appends a bot message to the list.
5. On error, appends an error bubble.


---

## 6. Web Client – React + Vite (Web/)

### 6.1 Purpose

A **single‑page web chat UI** built with:

- React functional components.
- Vite bundler.
- A minimal design (no routing yet).
- Light/dark theme toggle.

### 6.2 Key files

- **[Web/index.html](Web/index.html)**  
  - Standard Vite entry HTML:
    - Root `<div id="root">`.
    - Loads [`src/main.jsx`](Web/src/main.jsx).

- **[Web/src/main.jsx](Web/src/main.jsx)**  
  - Uses `createRoot` from `react-dom/client` to mount `<App />` into `#root`.
  - Imports global styles from [`src/index.css`](Web/src/index.css).

- **[Web/src/App.jsx](Web/src/App.jsx)**  
  - Root React component.
  - Currently only renders `<Chat />` from [`src/pages/Chat.jsx`](Web/src/pages/Chat.jsx).
  - Ready for extension to multiple pages/routes later.

- **[Web/src/pages/Chat.jsx](Web/src/pages/Chat.jsx)**  
  - Page component that:
    - Sets full‑height layout with a background.
    - Renders [`ChatBox`](Web/src/components/ChatBox.jsx) as the main content.

- **[Web/src/components/ChatBox.jsx](Web/src/components/ChatBox.jsx)**  
  - Core web chat logic:
    - State:
      - `messages` – array of role/content objects (starts with a welcome assistant message).
      - `input` – current text input.
      - `isLoading` – API call status.
      - `theme` – `"light"` or `"dark"`.
    - Fixed `sessionId = "local-llama-session"`.
    - `handleSend`:
      1. Guard against empty input or loading.
      2. Append user message to `messages`.
      3. Clear input, set `isLoading = true`.
      4. Call [`sendMessage`](Web/src/api/chat.js) with `sessionId` and user message.
      5. Append assistant reply or error message.
      6. Reset `isLoading`.

    - UI:
      - Header with bot avatar, subtitle, and a theme toggle button.
      - Scrollable messages area:
        - Renders each message via [`Message`](Web/src/components/Message.jsx).
        - Shows a simple loading indicator (three pulsing dots).
      - Input area:
        - Text input with `Enter` to send (without Shift).
        - Send button with loading/disabled states.

- **[Web/src/components/Message.jsx](Web/src/components/Message.jsx)**  
  - Generic message bubble component.
  - Props: `role` (`"user"` or `"assistant"`), `content`, `theme`.
  - Adjusts:
    - Alignment (user right, assistant left).
    - Background, text color, avatar color based on theme.
  - Uses inline styles and a small slide‑in animation.

- **[Web/src/api/chat.js](Web/src/api/chat.js)**  
  - Defines `API_URL = "http://localhost:8000/chat"`.
  - `sendMessage(sessionId, message)`:
    - Uses `axios.post` to FastAPI.
    - Sends `{ session_id, message }` as JSON.
    - Returns `response.data.response`.

- **[Web/src/index.css](Web/src/index.css)**  
  - Imports Tailwind via `@import "tailwindcss";` (Vite + Tailwind v4 style).
  - Tailwind classes are currently not used heavily, but ready for future.

- **[Web/package.json](Web/package.json)**  
  - Scripts: `dev`, `build`, `preview`, `lint`.
  - Dependencies:
    - `react`, `react-dom` – core React.
    - `axios` – HTTP client.
    - `tailwindcss`, `@tailwindcss/vite` – styling (utility-first).
  - Dev dependencies: Vite, ESLint, React hooks/refresh plugins, etc.

- **[Web/vite.config.js](Web/vite.config.js)**  
  - Configures Vite with React plugin and Tailwind plugin.

- **[Web/eslint.config.js](Web/eslint.config.js)**  
  - Flat ESLint config for JS/JSX with React hooks and Fast Refresh rules.


---

## 7. Cross‑Cutting Concepts & Dependencies

### 7.1 Session‑based chat history

- All clients send a `session_id` to backend.
- Backend stores history per session using [`chat_sessions`](Server/app/model/chat_memory.py).
- Prompt building in [`process_chat`](Server/app/services/chat_service.py) uses:
  ```text
  user: ...
  assistant: ...
  user: ...
  assistant:
  ```
- This gives the model conversational context.

### 7.2 Voice support (Desktop)

- Microphone access and STT:
  - `speech_recognition` + `pyaudio` + (Google API / PocketSphinx).
- TTS:
  - `pyttsx3` (offline, OS‑native voices).
- Controller integrates these so voice input flows into the same `/chat` pipeline as text.

### 7.3 Local LLM (Ollama + LangChain)

- `Ollama` server must be running (default `http://localhost:11434`).
- `phi3:latest` model is used (configurable when changing `llm = Ollama(...)`).
- LangChain’s `Ollama` wrapper exposes `.invoke(prompt)`.

### 7.4 CORS & networking

- FastAPI app enables permissive CORS during development to allow:
  - Android app (device/emulator).
  - Web app (browser).
  - Desktop client.
- Mobile app currently calls a specific IP (`http://172.25.71.230:8000/chat`), which should match the server host accessible from the device.


---

## 8. How to Run Each Part

### 8.1 Backend (FastAPI server)

```bash
cd Server
python3 -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
pip install -r requirment.txt

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Test with:

```bash
python3 test_chat.py
```

### 8.2 Desktop GUI (Tkinter + voice)

```bash
cd app
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export CHAT_API_URL="http://localhost:8000/chat"
export SESSION_ID="desktop-session"

python main.py
```

To build an executable:

```bash
python build.py
# Output: dist/ChatAssistant (or ChatAssistant.exe on Windows)
```

### 8.3 Web client (React + Vite)

```bash
cd Web
npm install
npm run dev
```

Open the printed URL (usually `http://localhost:5173`) in a browser.  
Ensure the backend is running on `http://localhost:8000`.

### 8.4 Android app (Expo React Native)

```bash
cd android
npm install
npx expo start
```

- Press `a` for Android emulator, `w` for web, or scan QR in Expo Go.
- Ensure the backend is reachable from the device at the URL hard‑coded in [`android/app/(tabs)/index.tsx`](android/app/(tabs)/index.tsx) (currently `http://172.25.71.230:8000/chat`).  
  - Adjust to your machine IP if needed.


---

## 9. Interview‑Style Questions and Answers

### 9.1 Architecture & Design

**Q1. Describe the overall architecture of this project.**  
**A.** It is a **multi‑client, single‑backend** architecture. A FastAPI server exposes `/chat` (HTTP) and `/ws` (WebSocket) endpoints. Multiple clients (desktop Tkinter app, Android Expo app, and React web app) all send `session_id` and `message` to `/chat`. The backend keeps in‑memory chat history per session and forwards a history‑aware prompt to a local LLaMA model (via Ollama + LangChain). The response is returned to each client and optionally spoken aloud on the desktop.

---

**Q2. Why did you separate the backend into controllers, services, and models?**  
**A.** This follows an **MVC‑like separation of concerns**:
- Controllers (e.g. [`chat_controller`](Server/app/controllers/chat_controller.py)) handle HTTP/WebSocket protocol and request/response.
- Services (e.g. [`chat_service`](Server/app/services/chat_service.py)) implement business logic combining memory and LLM.
- Models (e.g. [`schemas`](Server/app/model/schemas.py), [`chat_memory`](Server/app/model/chat_memory.py), [`llm_model`](Server/app/model/llm_model.py)) encapsulate data shapes and integration with external systems.  
This separation makes it easier to test and evolve each part independently.

---

**Q3. How is chat history handled, and why is `session_id` important?**  
**A.** Chat history is stored in a simple in‑memory dictionary `chat_sessions` keyed by `session_id` (see [`chat_memory.py`](Server/app/model/chat_memory.py)). For each request, the backend:
1. Loads previous messages for that session.
2. Builds a full prompt with alternating `user` and `assistant` messages.
3. Appends the latest user input and an `assistant:` cue.  
`session_id` lets multiple concurrent sessions exist (e.g., one per user or device) and allows the model to answer contextually instead of statelessly.

---

**Q4. What are the trade‑offs of using in‑memory storage for chat history?**  
**A.** Pros:
- Simple to implement.
- Very fast, no DB latency.
- Good for local or prototype setups.  
Cons:
- Data is lost when the process restarts.
- Not horizontally scalable (each instance has its own memory).
- Difficult to share history across machines.  
For production, this could be replaced with a database or key‑value store while preserving the `chat_memory` interface.

---

**Q5. How does the desktop app avoid blocking the Tkinter UI when calling the backend or microphone?**  
**A.** Tkinter is single‑threaded. To avoid freezing, the controller:
- Runs long‑running tasks (network calls, voice recognition) in background threads using `threading.Thread`.
- Uses `view.root.after(0, callback)` to safely schedule GUI updates on the main thread.  
This pattern keeps the UI responsive while performing I/O.

---

**Q6. What libraries are used for speech recognition and TTS on the desktop, and why?**  
**A.** For speech recognition:
- `SpeechRecognition` + `pyaudio` for microphone access and capturing audio.
- It uses Google’s free STT service when online and `pocketsphinx` for offline fallback.  
For TTS:
- `pyttsx3` provides offline text‑to‑speech that works across platforms.  
These choices enable **voice input and output** without relying on cloud services.

---

**Q7. How does the Android app ensure it can talk to the local backend over HTTP?**  
**A.** In [`app.json`](android/app.json), `"usesCleartextTraffic": true` allows non‑HTTPS HTTP connections, which is necessary for local development on `http://<LAN-IP>:8000`. The chat screen uses `fetch` to that IP in [`index.tsx`](android/app/(tabs)/index.tsx). For real devices, that IP must be reachable from the device (same Wi‑Fi, firewall open).

---

**Q8. Why are there separate web and Android clients instead of a single web view?**  
**A.** Each client is optimized for its platform:
- **Web**: Pure React + Vite, can be deployed independently with rich browser integrations.
- **Android**: React Native for native performance, access to device APIs (e.g., sensors, haptics).
- **Desktop**: Tkinter for a lightweight native desktop feel and easy voice integration.  
They all share a common backend API, which keeps the core logic centralized while tailoring UX per platform.

---

**Q9. How does the web client handle errors from the backend?**  
**A.** In [`ChatBox.jsx`](Web/src/components/ChatBox.jsx), `handleSend` wraps the API call in a `try/catch`. On failure, it appends an assistant message: `"Sorry, I encountered an error. Please try again."` and logs the error to console. The desktop and Android clients follow a similar pattern, showing user‑friendly text inside the chat instead of exposing raw exceptions.

---

**Q10. What is the role of CORS in this project?**  
**A.** The FastAPI app configures CORS via `CORSMiddleware` in [`main.py`](Server/app/main.py) with `allow_origins=["*"]`. This allows browser‑based clients (the React SPA, and potentially the Expo web target) to call `http://localhost:8000` without CORS errors in development. For production, allowed origins would typically be restricted.

---

### 9.2 Implementation Details

**Q11. How would you persist chat history if you wanted durability beyond memory?**  
**A.** I would:
1. Abstract the memory operations (`get_chat_history`, `save_message`) behind an interface.
2. Implement a new backend using a DB (e.g., PostgreSQL table with `session_id`, `role`, `content`, `timestamp`).
3. Replace or wrap the current in‑memory store with the DB implementation.  
The rest of the code (controllers, services) would remain unchanged because they already depend on these functions.

---

**Q12. How is the Ollama LLM integration made robust against server unavailability?**  
**A.** On import, [`llm_model.py`](Server/app/model/llm_model.py) attempts to instantiate `Ollama`. If it fails, `OLLAMA_AVAILABLE` is set to `False`. In `generate_response`, if Ollama is unavailable or raises an exception, the function logs the error and returns a random string from `MOCK_RESPONSES`. This guarantees that the API always returns a string, never crashes, and surfaces a friendly message to the user.

---

**Q13. How does the React Native chat UI manage scrolling to the latest message?**  
**A.** The chat screen keeps a `ref` to the `FlatList` (`flatListRef`) and a `useEffect` watching `messages`. Whenever `messages` changes, it schedules a `scrollToEnd({ animated: true })` call after a small timeout. This ensures the latest message is visible even when the keyboard toggles.

---

**Q14. How do you toggle light/dark mode in the web client?**  
**A.** The web client maintains a `theme` state (`"light"` or `"dark"`) in [`ChatBox.jsx`](Web/src/components/ChatBox.jsx). Clicking the toggle button switches the state, and the component re‑computes `currentColors` based on `theme`. Those colors control background, text, borders, and shadows. Messages receive `theme` as a prop and adjust their styling accordingly.

---

**Q15. How does the desktop build script ensure PyInstaller is available?**  
**A.** [`build.py`](app/build.py) tries to `import PyInstaller`. If that fails, it automatically runs `pip install pyinstaller` using `subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])`. Once installed, it executes the PyInstaller command to build the executable. This simplifies the build process for users.

---

**Q16. Why are `requests`, `axios`, and `fetch` all used in different parts of the project? Would you unify them?**  
**A.** Each client is written in a language or platform that has its own idiomatic HTTP library:
- Desktop (Python): `requests`.
- Web (JS): `axios` for convenience (interceptors, JSON handling).
- Android RN: built‑in `fetch`.  
Unifying is not necessary because they live in different runtimes, but within each runtime I would standardize on one library (e.g., `axios` for both Web and React Native if I refactor Android to use it).

---

**Q17. How would you add authentication to this system?**  
**A.** High‑level steps:
1. Add auth endpoints in FastAPI (e.g., login, token issuance).
2. Protect `/chat` and `/ws` using dependency injection for authentication (JWT, sessions).
3. Modify clients to:
   - Authenticate and store token locally.
   - Attach `Authorization: Bearer <token>` header to chat requests.
4. Optionally tie `session_id` to user identity on the backend for per‑user history.  
The core chat service (`process_chat`) would not need major changes.

---

**Q18. How would you scale this beyond one machine?**  
**A.** Main concerns:
- Chat history: move from in‑memory to a shared datastore (DB/Redis).
- LLM: run Ollama behind a load balancer or use a hosted LLM service.
- API: deploy multiple FastAPI instances behind a reverse proxy (e.g., Nginx) or use container orchestrators (Kubernetes).  
Because the chat service is stateless aside from memory, swapping in a shared store is the primary change needed.

---

**Q19. How would you test the system end‑to‑end?**  
**A.**  
- **Unit tests**:  
  - Test `process_chat` with a fake `generate_response` and in‑memory `chat_memory`.  
- **Integration tests**:  
  - Use `TestClient` from FastAPI to exercise `/chat` with different `session_id` values and check responses and history.  
- **Manual / UI tests**:  
  - Use [`test_chat.py`](Server/test_chat.py) to verify backend independently.  
  - Run each client (Web, Android, Desktop) and ensure they all produce consistent responses and preserve context per session.

---

**Q20. If the Ollama model is slow, how would you improve responsiveness for users?**  
**A.** Options:
- Introduce **streaming responses** over WebSocket or server‑sent events.
- Add a **loading indicator** (already present in Web/Android/desktop status bar).
- Implement **caching** for repeated prompts.
- Tune `temperature`, prompt length, or model size.
- Offload heavy operations to a separate worker process or queue if needed.

---

## 10. Summary

This project demonstrates a **full multi‑platform AI assistant** architecture:

- A **FastAPI backend** integrating **LangChain + Ollama** for local LLaMA inference and providing clean REST/WebSocket interfaces.
- A **desktop Tkinter app** with speech recognition and TTS.
- A **mobile Expo React Native client** and a **React/Vite web client** that share the same `/chat` contract.
- A simple, extensible **chat history and session model** that can be upgraded to persistent storage.

The codebase is structured to be **interview‑ready**, with clean separations of controller, service, and model layers, and platform‑specific frontends that all exercise the same core backend.