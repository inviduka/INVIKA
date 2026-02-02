# app.py
import os
import asyncio
import logging
import json
import requests
import re
from dotenv import load_dotenv

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

# -------------------- setup --------------------
load_dotenv()
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("invika")

app = FastAPI()

# -------------------- PURE ORB UI HTML --------------------
HTML = """
<!doctype html>
<html>
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>INVIKA • SYSTEM ONLINE</title>
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap" rel="stylesheet">

<style>
:root {
  --primary: #00f3ff;
  --secondary: #0066aa;
  --bg: #020205;
  --pink-glow: #ffb6c1;
  --error: #ff3333;
}

body {
  margin: 0; padding: 0;
  height: 100vh; width: 100vw;
  background-color: var(--bg);
  background-image: 
    linear-gradient(rgba(0, 243, 255, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 243, 255, 0.05) 1px, transparent 1px);
  background-size: 50px 50px;
  color: var(--primary);
  font-family: 'Orbitron', sans-serif;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  overflow: hidden;
}

/* The Core Orb */
.orb-container {
  position: relative;
  width: 300px; height: 300px;
  display: flex; align-items: center; justify-content: center;
}

.orb {
  width: 140px; height: 140px;
  border-radius: 50%;
  background: radial-gradient(circle at 30% 30%, #fff, var(--primary));
  box-shadow: 0 0 60px var(--primary);
  transition: all 0.4s ease;
}

.orb-ring {
  position: absolute;
  width: 200px; height: 200px;
  border-radius: 50%;
  border: 2px solid var(--secondary);
  border-top-color: var(--primary);
  animation: rotate 3s linear infinite;
}

/* State Styles */
.listening .orb { transform: scale(1.1); box-shadow: 0 0 100px #fff; background: #fff; }
.thinking .orb-ring { animation-duration: 0.8s; border-color: #ffc107; }
.speaking .orb { 
  background: radial-gradient(circle, #fff, var(--pink-glow));
  box-shadow: 0 0 100px var(--pink-glow);
  animation: pulse 0.6s infinite alternate; 
}
.error .orb { background: var(--error); box-shadow: 0 0 80px var(--error); }

/* Floating Response Text */
#response-text {
  margin-top: 40px;
  max-width: 80%;
  text-align: center;
  font-size: 18px;
  height: 60px;
  text-shadow: 0 0 10px var(--primary);
}

#status-log {
  position: absolute;
  bottom: 10px;
  font-size: 10px;
  color: #555;
}

#suggestions {
  margin-top: 20px;
  display: flex; gap: 10px;
  opacity: 0; transition: 0.5s;
}

.suggest-btn {
  padding: 10px 20px;
  background: rgba(0, 243, 255, 0.1);
  border: 1px solid var(--primary);
  color: #fff; border-radius: 30px;
  cursor: pointer; text-decoration: none; font-size: 12px;
}

#startBtn {
  position: absolute;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  padding: 20px 40px;
  background: var(--primary); color: #000;
  border: none; font-family: 'Orbitron'; font-weight: 900;
  font-size: 20px;
  cursor: pointer; z-index: 100;
  box-shadow: 0 0 50px var(--primary);
}

@keyframes rotate { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
@keyframes pulse { from { transform: scale(1); } to { transform: scale(1.1); } }
</style>
</head>

<body>
<button id="startBtn">INITIALIZE SYSTEM</button>

<div id="orb-container" class="orb-container">
  <div class="orb-ring"></div>
  <div id="orb" class="orb"></div>
</div>

<div id="response-text">AWAITING INITIALIZATION...</div>
<div id="suggestions"></div>
<div id="status-log"></div>

<script>
const orbCont = document.getElementById("orb-container");
const responseEl = document.getElementById("response-text");
const startBtn = document.getElementById("startBtn");
const suggestBox = document.getElementById("suggestions");
const statusLog = document.getElementById("status-log");

let ws = null;
let recognition = null;
let wakeActive = false;
let audioAllowed = false;
let isSpeaking = false;

// --- UTILS ---
function logStatus(msg) {
    console.log(msg);
    statusLog.innerText = msg;
}

function setState(s){ orbCont.className = "orb-container " + s; }

// --- WEBSOCKET CONNECTION & RECONNECT ---
function connectWS() {
    ws = new WebSocket("ws://" + location.host + "/ws");
    
    ws.onopen = () => {
        logStatus("Connected to Server");
        if(audioAllowed) responseEl.innerText = "ONLINE";
    };

    ws.onclose = () => {
        logStatus("Disconnected. Reconnecting...");
        setState("error");
        setTimeout(connectWS, 2000); // Retry after 2s
    };

    ws.onmessage = (ev) => {
        try {
            const data = JSON.parse(ev.data);
            responseEl.innerText = data.text || "";
            
            if(data.type === "open") {
                speak("Opening " + (data.name || "application"));
                if(data.url) window.open(data.url, "_blank");
            } else {
                speak(data.text);
            }
            
            // --- FIX: SAFE SUGGESTION HANDLING ---
            if(data.suggestions && Array.isArray(data.suggestions)) {
                showSuggestions(data.suggestions);
            }
        } catch(e) {
            console.error("WS Error:", e);
        }
    };
}

// --- AUDIO OUTPUT (TTS) ---
function speak(text){
    if(!audioAllowed || !text) return;
    
    if(recognition) recognition.stop();
    isSpeaking = true;
    setState("speaking");
    
    const u = new SpeechSynthesisUtterance(text);
    const voices = speechSynthesis.getVoices();
    // Try to find a good voice
    const bestVoice = voices.find(v => v.name.includes("Google US English") || v.name.includes("Microsoft David"));
    if(bestVoice) u.voice = bestVoice;
    
    u.onend = () => { 
        isSpeaking = false;
        // Restart recognition
        if(wakeActive) setState("listening");
        else setState("idle");
        
        try { recognition.start(); } catch(e){}
    };
    
    speechSynthesis.cancel();
    speechSynthesis.speak(u);
}

// --- FIX: ROBUST SUGGESTIONS ---
function showSuggestions(apps){
    suggestBox.innerHTML = "";
    apps.forEach(app => {
        if(!app) return;
        const name = app.name || "Link"; // Fallback if name is missing
        const url = app.url || "#";
        
        const a = document.createElement("a");
        a.className = "suggest-btn";
        a.innerText = "OPEN " + name.toUpperCase();
        a.href = url; a.target = "_blank";
        suggestBox.appendChild(a);
    });
    suggestBox.style.opacity = "1";
}

// --- VOICE INPUT (STT) ---
function initRecognition(){
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if(!SR) {
        responseEl.innerText = "ERROR: Browser does not support Speech API.";
        return;
    }

    recognition = new SR();
    recognition.continuous = true; 
    recognition.interimResults = false;
    recognition.lang = "en-US";

    recognition.onstart = () => { 
        logStatus("Microphone Active");
        if(wakeActive) setState("listening");
    };
    
    recognition.onend = () => {
        logStatus("Mic Stopped. Restarting...");
        if(audioAllowed && !isSpeaking) {
            setTimeout(() => { try{ recognition.start(); }catch(e){} }, 200);
        }
    };

    recognition.onresult = (e) => {
        const transcript = e.results[e.results.length-1][0].transcript.trim().toLowerCase();
        logStatus("Heard: " + transcript);

        if(!wakeActive) {
            if(transcript.includes("invika") || transcript.includes("hey invika")) {
                wakeActive = true;
                speak("I am online.");
            }
            return;
        }

        if(transcript.includes("stop") || transcript.includes("go to sleep")) {
            wakeActive = false;
            suggestBox.style.opacity = "0";
            speak("Going to sleep.");
            setState("idle");
            return;
        }

        setState("thinking");
        // Only send if WS is open
        if(ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({text: transcript}));
        } else {
            speak("Connection lost. Reconnecting.");
        }
    };
}

// --- STARTUP ---
startBtn.onclick = () => {
    audioAllowed = true;
    startBtn.style.display = 'none';
    responseEl.innerText = "SYSTEM ONLINE. Say 'Hey Invika'";
    speechSynthesis.speak(new SpeechSynthesisUtterance("")); // Unlock audio
    
    connectWS();
    initRecognition();
    try { recognition.start(); } catch(e) { console.error(e); }
    
    speak("Welcome to Invika world.");
};
</script>
</body>
</html>
"""

# -------------------- Gemini Logic (FIXED & VALIDATED) --------------------
def call_gemini_smart(prompt: str) -> dict:
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("[ERROR] No API Key Found")
        return {"type": "chat", "text": "Error: API Key missing."}

    # Model IDs from your specific screenshot
    # models = ["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-1.5-flash"]
    # Model IDs verified from your dashboard screenshots
    models = ["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-1.5-flash"]
        
    system_prompt = """
    You are INVIKA. 
    INSTRUCTIONS:
    1. Respond ONLY in valid JSON. Do not add markdown like ```json.
    2. Structure: {"type": "chat" or "open", "text": "your reply", "url": "link", "name": "app name", "suggestions": [{"name": "App Name", "url": "URL"}]}
    
    APP DICTIONARY:
    - Thinkare: [https://thinkare.vercel.app](https://thinkare.vercel.app)
    - Hurryup: [https://hurryup-buddy.vercel.app](https://hurryup-buddy.vercel.app)
    - YouTube: [https://youtube.com](https://youtube.com)
    - Google: [https://google.com](https://google.com)
    - ChatGPT: [https://chatgpt.com](https://chatgpt.com)
    - GitHub: [https://github.com](https://github.com)
 	  - Spotify: [https://spotify.com](https://spotify.com)
    - Instagram: [https://instagram.com](https://instagram.com)
    
    If user mentions ThinKare or Hurryup, YOU MUST include them in the 'suggestions' list.
    If user says "Open [App]", return type="open".
    """

    for model in models:
        # NOTE: Clean URL string, no brackets!
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        
        payload = {
            "contents": [{"role": "user", "parts": [{"text": f"{system_prompt}\nUser: {prompt}"}]}]
        }

        try:
            r = requests.post(url, params={"key": api_key}, json=payload, timeout=10)
            
            if r.status_code != 200:
                print(f"[API Error] {model} returned {r.status_code}: {r.text}")
                continue 

            raw = r.json()["candidates"][0]["content"]["parts"][0]["text"]
            clean = re.sub(r'```json|```', '', raw).strip()
            
            data = json.loads(clean)
            
            # --- VALIDATE SUGGESTIONS ---
            # Ensure suggestions have 'name' and 'url' to prevent frontend crash
            if "suggestions" in data and isinstance(data["suggestions"], list):
                valid_suggestions = []
                for s in data["suggestions"]:
                    if isinstance(s, dict) and "name" in s and "url" in s:
                        valid_suggestions.append(s)
                data["suggestions"] = valid_suggestions
            
            return data

        except json.JSONDecodeError:
            return {"type": "chat", "text": clean}
            
        except Exception as e:
            print(f"[Connection Error] {model}: {e}")
            continue

    return {"type": "chat", "text": "Systems busy. Please try again."}

# -------------------- routes --------------------
@app.get("/")
async def index(): return HTMLResponse(HTML)

@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            # Inner Try-Catch keeps the server running even if one message fails
            try:
                msg = await ws.receive_json()
                text = msg.get("text","").strip()
                if not text: continue
                
                response = await asyncio.to_thread(call_gemini_smart, text)
                await ws.send_json(response)
            except WebSocketDisconnect:
                print("Client disconnected")
                break
            except Exception as e:
                print(f"Message Processing Error: {e}")
                # Don't break loop, just log
    except Exception as e:
        print(f"Critical WebSocket Error: {e}")

