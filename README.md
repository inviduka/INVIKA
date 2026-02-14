# 🚀 INVIKA — Your AI Companion, Reimagined

> A futuristic, voice-enabled AI assistant with a real-time interactive UI, powered by FastAPI, WebSockets, and Google Gemini.

INVIKA is not just a chatbot. It’s a **product-style AI companion** with:
- 🎙️ Voice input (Speech-to-Text)
- 🔊 Voice output (Text-to-Speech)
- 🧠 Real-time AI reasoning via Gemini
- 🌐 Live interactive web interface
- ⚡ WebSocket-based low-latency communication
- 🛸 Sci-fi inspired “Orb” UI experience

Think **Jarvis-like assistant for the web** — built for speed, experience, and extensibility.

---

## ✨ Product Vision

INVIKA is designed as a **human-like AI companion**:
- Feels conversational, not robotic  
- Responds in real time  
- Can open apps, suggest actions, and guide users  
- Built to evolve into a full personal productivity & assistant platform  

This is a **startup-style foundation** for:
- AI companions  
- Voice assistants  
- Smart dashboards  
- Productivity copilots  
- Interactive AI products  

---

## 🧠 Key Features

- 🎤 **Wake word activation** (“Hey Invika”)
- 🗣️ **Speech-to-Text** using browser Speech API
- 🔊 **Text-to-Speech** responses
- 🔁 **Real-time WebSocket communication**
- 🌐 **FastAPI backend**
- 🤖 **Google Gemini integration** (multi-model fallback)
- 🧩 **Smart app opening system** (YouTube, GitHub, Google, etc.)
- 💡 **Contextual suggestions UI**
- 🎨 **Futuristic Orb UI with state animations**
- 🛡️ Robust error handling & auto-reconnect

---

## 🏗️ Tech Stack

**Backend**
- Python
- FastAPI
- WebSockets
- AsyncIO

**AI**
- Google Gemini API (2.5 Flash / Lite / 1.5 Flash fallback)
- Custom system prompt & persona engine

**Frontend**
- HTML, CSS, JavaScript
- Web Speech API (STT + TTS)
- Real-time UI state engine
- Sci-fi animated Orb interface

**Infrastructure**
- Environment-based config (`.env`)
- Auto-reconnect WebSocket client
- Modular AI routing logic

---

## ⚙️ How It Works (High Level)

1. User clicks **INITIALIZE SYSTEM**
2. Browser enables microphone + audio
3. User says: **“Hey Invika”**
4. Voice is converted to text
5. Text is sent via WebSocket to FastAPI
6. Backend calls **Gemini**
7. Gemini responds in **strict JSON**
8. UI:
   - Speaks the response
   - Animates the Orb
   - Shows suggestions / opens apps if needed

---

## 🚀 Getting Started

### 1️⃣ Clone the repo
```bash
git clone <[INVIKA]-(https://github.com/inviduka/INVIKA)>
cd invika

2️⃣ Install dependencies

pip install fastapi uvicorn python-dotenv requests

3️⃣ Setup Environment Variables

Create a .env file:

GEMINI_API_KEY=your_api_key_here

(or GOOGLE_API_KEY)

4️⃣ Run the server

uvicorn app:app --reload

5️⃣ Open in browser

http://localhost:8000

Click INITIALIZE SYSTEM and say:

> “Hey Invika”




---

🧪 Example Commands

“Hey Invika, open YouTube”

“Hey Invika, open GitHub”

“Hey Invika, what is FastAPI?”

“Go to sleep”

“Open Spotify”



---

🧩 Extensibility Roadmap

🧠 Memory & user profiles

📱 Mobile-friendly PWA version

🗂️ Plugin system (apps, tools, workflows)

🗣️ Better wake-word detection

🧑‍💼 Productivity mode (tasks, reminders, notes)

🌍 Multi-language support

🔐 Auth & personalization



---

🏁 Why This Project Matters

This is not a demo. This is a product foundation for:

AI companions

Voice-first interfaces

Real-time AI systems

Next-gen human-computer interaction


It demonstrates:

System design

Real-time architecture

AI orchestration

Product-grade UX thinking



---

👤 Authors

Jayanth & Thirupathi
Founder-minded Full Stack / AI Product Engineers


---

⭐ Support

If you find this project interesting:

Star ⭐ the repo

Fork 🍴 it

Build on it 🚀

Ship something amazing


Let’s build the future of AI interfaces.

---

## 👀 Preview (How It Will Look on GitHub)

**Top Section:**
> 🚀 INVIKA — Your AI Companion, Reimagined  
> A futuristic, voice-enabled AI assistant with real-time UI, powered by FastAPI, WebSockets, and Gemini.

Then:
- Clean **feature list**
- Strong **product vision**
- Clear **tech stack**
- Easy **getting started**
- Impressive **roadmap**
- Startup-style **positioning**
- Strong **founder/product narrative**

It will read like:
> This is a serious AI product prototype — not a toy project.

---

## 💡 If you want, I can next:

- Rebrand this as a **startup landing README**
- Add **badges, shields, and metrics**
- Create a **pitch-style README**
- Optimize it for **investors / recruiters / GitHub profile**
- Write a **homepage README + docs structure**

Just tell me your goal: **job, startup, or open-source growth** 🚀
