# Chat Assistant Desktop App

Desktop chat application with **voice input/output** that connects to your FastAPI backend.

## 🚀 Quick Start

```bash
cd /home/satya/Desktop/Assistant/app
/home/satya/Desktop/Assistant/app/.venv/bin/python main_gui.py
```

## 📦 Build Executable

```bash
/home/satya/Desktop/Assistant/app/.venv/bin/python build.py
```

Executable will be in `dist/ChatAssistant`

## 💬 Features

- Text chat interface
- 🎤 Voice input (click "Speak", talk, wait 2 seconds)
- 🔊 Voice output (bot speaks responses)
- Chat history management

## ⚙️ Configuration

```bash
export CHAT_API_URL="http://localhost:8000/chat"
export SESSION_ID="my-session"
```

## 📋 Requirements

- Python 3.8+
- FastAPI server at http://localhost:8000
- Microphone & speakers
- Linux: `sudo apt-get install portaudio19-dev espeak`

## 🔧 Troubleshooting

**Microphone issues:** Check with `arecord -l` and `pavucontrol`

**TTS not working:** Test with `espeak "test"`

**Build fails:** Run `pip install -r requirements.txt`

