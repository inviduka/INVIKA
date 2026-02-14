# 🚀 INVIKA — Your AI Companion, Reimagined

> A futuristic, voice-enabled AI assistant with a real-time interactive UI, powered by FastAPI, WebSockets, and Google Gemini.

INVIKA is not just a chatbot. It’s a **product-style AI companion** designed to feel human, respond in real time, and deliver a next-generation AI interaction experience.

- 🎙️ Voice input (Speech-to-Text)  
- 🔊 Voice output (Text-to-Speech)  
- 🧠 Real-time AI reasoning via Gemini  
- 🌐 Live interactive web interface  
- ⚡ WebSocket-based low-latency communication  
- 🛸 Sci-fi inspired “Orb” UI experience  

Think of INVIKA as a **Jarvis-like assistant for the web** — built for speed, experience, and extensibility.

---

## ✨ Product Vision

INVIKA is designed as a **human-like AI companion**:
- Feels conversational, not robotic  
- Responds in real time  
- Can open apps, suggest actions, and guide users  
- Built to evolve into a full personal productivity and assistant platform  

This project serves as a **startup-style foundation** for:
- AI companions  
- Voice assistants  
- Smart dashboards  
- Productivity copilots  
- Interactive AI products  

---

## 🧠 Key Features

- 🎤 **Wake word activation** (“Hey Invika”)  
- 🗣️ **Speech-to-Text** using the browser Speech API  
- 🔊 **Text-to-Speech** responses  
- 🔁 **Real-time WebSocket communication**  
- 🌐 **FastAPI backend**  
- 🤖 **Google Gemini integration** (multi-model fallback)  
- 🧩 **Smart app opening system** (YouTube, GitHub, Google, etc.)  
- 💡 **Contextual suggestions UI**  
- 🎨 **Futuristic Orb UI with state animations**  
- 🛡️ Robust error handling and auto-reconnect  

---

## 🏗️ Tech Stack

**Backend**
- Python  
- FastAPI  
- WebSockets  
- AsyncIO  

**AI**
- Google Gemini API (2.5 Flash / Lite / 1.5 Flash fallback)  
- Custom system prompt and persona engine  

**Frontend**
- HTML, CSS, JavaScript  
- Web Speech API (STT + TTS)  
- Real-time UI state engine  
- Sci-fi animated Orb interface  

**Infrastructure**
- Environment-based configuration (`.env`)  
- Auto-reconnect WebSocket client  
- Modular AI routing logic  

---

### 2️⃣ Create a virtual environment (recommended)
```bash
python -m venv venv
```
### 3️⃣ Activate the virtual environment
```
venv\Scripts\activate - (Windows)
source venv/bin/activate - (Linux)
```

### 4️⃣ Install dependencies
```
pip install fastapi uvicorn python-dotenv requests
```

### 5️⃣ Set up environment variables 
```bash
GEMINI_API_KEY=your_api_key_here
```

### 6️⃣ Run the server
```bash
uvicorn app:app --reload
```

### 7️⃣ Open in your browser
```bash
http://localhost:8000
```

## ⚙️ How INVIKA Works (High Level)

1. User initializes the system from the web UI  
2. The browser enables microphone and audio output  
3. The user says: **“Hey Invika”**  
4. Speech is converted to text in the browser  
5. The text is sent via WebSocket to the FastAPI backend  
6. The backend calls **Google Gemini**  
7. Gemini responds in **strict JSON format**  
8. The UI:
   - Speaks the response  
   - Animates the Orb  
   - Shows suggestions or opens apps when applicable  

---

## 🧪 Example Commands

- “Hey Invika, open YouTube”  
- “Hey Invika, open GitHub”  
- “Hey Invika, what is FastAPI?”  
- “Go to sleep”  
- “Open Spotify”  

---

## 🧩 Roadmap & Future Scope

- 🧠 Memory and persistent user profiles  
- 📱 Mobile-friendly PWA version  
- 🗂️ Plugin system for apps, tools, and workflows  
- 🗣️ Improved wake-word detection  
- 🧑‍💼 Productivity mode (tasks, reminders, notes)  
- 🌍 Multi-language support  
- 🔐 Authentication and personalization  
- ☁️ Cloud deployment and scaling strategy  

---

## 🤝 Collaboration & Contributions

Contributions are **welcome and encouraged** 🚀  

You can contribute by:
- Adding new features or integrations  
- Improving UI/UX or animations  
- Enhancing AI prompts and behaviors  
- Fixing bugs or improving performance  
- Writing documentation or examples  

**How to collaborate:**
- Fork the repository  
- Create a new feature branch  
- Commit your changes with clear messages  
- Open a Pull Request with a detailed description  

All constructive ideas, improvements, and discussions are appreciated.

---

## 🏁 Why This Project Matters

INVIKA is not a demo—it is a **product foundation** for:
- AI companions  
- Voice-first interfaces  
- Real-time AI systems  
- Next-generation human–computer interaction  

It demonstrates:
- System design and real-time architecture  
- AI orchestration with modern LLMs  
- Product-grade UX thinking  
- End-to-end full stack engineering  

---

## 👤 Authors

**Jayanth & Thirupathi**  
Founder-minded Full Stack / AI Product Engineers  

---

## ⭐ Support

If you find this project valuable:

- Star ⭐ the repository  
- Fork 🍴 it  
- Contribute 🤝  
- Build on it 🚀  
- Ship something amazing  

Let’s build the future of AI interfaces—together.
