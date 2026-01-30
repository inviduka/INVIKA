# app.py
import os
import asyncio
import logging
import requests
from dotenv import load_dotenv

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

# -------------------- setup --------------------
load_dotenv()
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("invika")

app = FastAPI()

# -------------------- INVIKA UI HTML --------------------
HTML = """
<!doctype html>
<html>
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>INVIKA • SYSTEM ONLINE</title>
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;700&display=swap" rel="stylesheet">

<style>
:root {
  --primary: #00f3ff;
  --secondary: #0066aa;
  --bg: #050510;
  --glass: rgba(0, 243, 255, 0.1);
}

body {
  margin: 0;
  height: 100vh;
  background-color: var(--bg);
  background-image: 
    radial-gradient(circle at 50% 50%, rgba(0, 50, 100, 0.2) 0%, transparent 60%),
    linear-gradient(0deg, rgba(0, 243, 255, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 243, 255, 0.03) 1px, transparent 1px);
  background-size: 100% 100%, 40px 40px, 40px 40px;
  color: var(--primary);
  font-family: 'Orbitron', sans-serif;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.hud-container {
  width: 600px;
  max-width: 95%;
  border: 1px solid var(--primary);
  background: rgba(0, 20, 40, 0.85);
  box-shadow: 0 0 20px rgba(0, 243, 255, 0.2), inset 0 0 40px rgba(0, 243, 255, 0.1);
  border-radius: 12px;
  padding: 30px;
  position: relative;
  backdrop-filter: blur(5px);
}

/* Corner Accents */
.corner {
  position: absolute;
  width: 20px;
  height: 20px;
  border: 2px solid var(--primary);
  transition: all 0.3s ease;
}
.tl { top: -2px; left: -2px; border-bottom: none; border-right: none; }
.tr { top: -2px; right: -2px; border-bottom: none; border-left: none; }
.bl { bottom: -2px; left: -2px; border-top: none; border-right: none; }
.br { bottom: -2px; right: -2px; border-top: none; border-left: none; }

/* Arc Reactor */
.reactor-container {
  display: flex;
  justify-content: center;
  margin: 30px 0;
  position: relative;
}

.reactor {
  width: 180px;
  height: 180px;
  border-radius: 50%;
  border: 4px solid var(--secondary);
  box-shadow: 0 0 30px var(--secondary);
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.core {
  width: 90px;
  height: 90px;
  background: radial-gradient(circle, #fff, var(--primary));
  border-radius: 50%;
  box-shadow: 0 0 40px var(--primary);
  z-index: 2;
  transition: all 0.3s;
}

.ring {
  position: absolute;
  width: 160px;
  height: 160px;
  border-radius: 50%;
  border: 2px solid transparent;
  border-top: 2px solid var(--primary);
  border-bottom: 2px solid var(--primary);
  animation: spin 4s linear infinite;
}

.ring.inner {
  width: 120px;
  height: 120px;
  border: 2px solid transparent;
  border-left: 2px solid var(--primary);
  border-right: 2px solid var(--primary);
  animation: spin-rev 3s linear infinite;
}

/* States */
.reactor.listening .core { box-shadow: 0 0 70px #fff; background: #fff; }
.reactor.speaking .core { background: #ff4d6d; box-shadow: 0 0 70px #ff4d6d; animation: pulse 0.5s infinite alternate; }
.reactor.thinking .ring { animation-duration: 0.5s; border-color: #ffc107; }

/* Logs */
#log {
  height: 150px;
  overflow-y: auto;
  border-top: 1px solid var(--secondary);
  border-bottom: 1px solid var(--secondary);
  margin-top: 20px;
  padding: 10px;
  font-size: 14px;
  font-family: 'Consolas', monospace;
  background: rgba(0, 0, 0, 0.3);
  scrollbar-width: thin;
  scrollbar-color: var(--primary) transparent;
}
.msg.user { color: #aaa; text-align: right; }
.msg.ai { color: var(--primary); text-shadow: 0 0 5px var(--primary); }
.msg.system { color: #ffc107; font-size: 12px; text-transform: uppercase; }

#startBtn {
  width: 100%;
  padding: 15px;
  background: var(--primary);
  color: #000;
  font-weight: bold;
  font-size: 18px;
  border: none;
  cursor: pointer;
  text-transform: uppercase;
  clip-path: polygon(10px 0, 100% 0, 100% calc(100% - 10px), calc(100% - 10px) 100%, 0 100%, 0 10px);
  margin-bottom: 10px;
}

@keyframes spin { 100% { transform: rotate(360deg); } }
@keyframes spin-rev { 100% { transform: rotate(-360deg); } }
@keyframes pulse { 100% { transform: scale(1.1); } }
</style>
</head>

<body>

<div class="hud-container">
  <div class="corner tl"></div><div class="corner tr"></div>
  <div class="corner bl"></div><div class="corner br"></div>

  <h3 style="text-align:center; letter-spacing: 4px; margin:0 0 10px 0;">I.N.V.I.K.A. INTERFACE</h3>
  <div style="text-align:center; margin-bottom: 20px; font-size:12px; color:var(--secondary)">
    STATUS: <span id="status">STANDBY</span>
  </div>

  <div class="reactor-container">
    <div id="reactor" class="reactor">
      <div class="ring"></div>
      <div class="ring inner"></div>
      <div class="core"></div>
    </div>
  </div>

  <button id="startBtn">INITIALIZE SYSTEM</button>

  <div id="log"></div>
</div>

<script>
/* ---------------- CONSTANTS & STATE ---------------- */
const reactor = document.getElementById("reactor");
const statusEl = document.getElementById("status");
const logEl = document.getElementById("log");
const startBtn = document.getElementById("startBtn");

const ws = new WebSocket("ws://" + location.host + "/ws");
const WAKE_WORD = "invika"; 

let recognition = null;
let listening = false;
let synthSpeaking = false;
let wakeActive = false;
let audioAllowed = false;

/* ---------------- HELPERS ---------------- */
function logMsg(role, text){
  const d = document.createElement("div");
  d.className = "msg " + role;
  d.innerText = (role === 'ai' ? 'INVIKA' : role).toUpperCase() + ": " + text;
  logEl.appendChild(d);
  logEl.scrollTop = logEl.scrollHeight;
}

function setState(s){
  reactor.className = "reactor " + s;
  statusEl.innerText = s.toUpperCase() || "IDLE";
}

function openApp(url){
  logMsg("system", "Opening external module...");
  speak("Opening module.");
  window.open(url, '_blank');
}

/* ---------------- AUDIO ---------------- */
function speak(text){
  if(!text || !audioAllowed) return;

  if(listening && recognition) recognition.stop();
  
  synthSpeaking = true;
  setState("speaking");
  
  const u = new SpeechSynthesisUtterance(text);
  // Try to find a good voice
  const voices = speechSynthesis.getVoices();
  const preferred = voices.find(v => v.name.includes("Google US English") || v.name.includes("Microsoft David"));
  if(preferred) u.voice = preferred;
  
  u.onend = () => {
    synthSpeaking = false;
    if(recognition) {
        try { recognition.start(); } catch(e){} 
    }
  };
  speechSynthesis.cancel();
  speechSynthesis.speak(u);
}

/* ---------------- SPEECH RECOGNITION ---------------- */
function initRecognition(){
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if(!SR){
    logMsg("system","VOICE MODULE NOT DETECTED (USE CHROME)");
    return;
  }

  recognition = new SR();
  recognition.lang = "en-US";
  recognition.continuous = true;

  recognition.onstart = () => {
    listening = true;
    setState("listening");
  };

  recognition.onend = () => {
    listening = false;
    if(!synthSpeaking){
      setTimeout(() => { try { recognition.start(); } catch(e){} }, 300);
    }
  };

  recognition.onresult = (e) => {
    const text = e.results[e.results.length-1][0].transcript.trim().toLowerCase();

    // --- 1. PRIORITY: STOP COMMAND (Only checks if active) ---
    if(wakeActive && (text === "stop" || text === "go to sleep" || text === "exit" || text === "cancel")){
        wakeActive = false;
        logMsg("system", "SYSTEM PAUSED");
        speak("Going offline. Say hey Invika to wake me.");
        setState("idle");
        return;
    }

    // --- 2. MULTIMEDIA COMMANDS (Works anytime) ---
    
    if(text.includes("open spotify")) { openApp('https://open.spotify.com'); return; }
    if(text.includes("open google")) { openApp('https://www.google.com'); return; }
    if(text.includes("open youtube")) { openApp('https://www.youtube.com'); return; }
    if(text.includes("open linkedin")) { openApp('https://www.linkedin.com'); return; }
    if(text.includes("open gmail")) { openApp('https://mail.google.com'); return; }
    if(text.includes("open instagram")) { openApp('https://www.instagram.com'); return; }
    if(text.includes("open hurryup")) { openApp('https://hurryup-buddy.vercel.app'); return; }
    if(text.includes("open thinkare")) { openApp('https://thinkare.vercel.app'); return; }

    // --- 3. WAKE WORD LOGIC (If asleep) ---
    if(!wakeActive){
      if(text.includes(WAKE_WORD) || text.includes("hey invika")){
        wakeActive = true;
        speak("Yes? I am listening.");
      }
      return;
    }

    // --- 4. CONVERSATION (If awake) ---
    logMsg("user", text);
    ws.send(JSON.stringify({text}));
    setState("thinking");
  };
}

/* ---------------- INITIALIZATION ---------------- */
startBtn.onclick = () => {
  audioAllowed = true;
  const u = new SpeechSynthesisUtterance("System Initialized");
  speechSynthesis.speak(u);

  initRecognition();
  recognition.start();

  startBtn.style.display = 'none';
  logMsg("system","SYSTEM ONLINE. AWAITING INPUT.");
  speak("Invika interface online. Say Hey Invika to start.");
};

/* ---------------- WEBSOCKET ---------------- */
ws.onopen = () => logMsg("system","SERVER CONNECTED");
ws.onmessage = (ev) => {
  const data = JSON.parse(ev.data);
  if(data.type === "ai"){
    logMsg("ai", data.text);
    speak(data.text);
    // REMOVED: wakeActive = false; 
    // This allows Invika to stay awake until you say "Stop"
  }
};
</script>
</body>
</html>
"""

# -------------------- Gemini Logic --------------------
def call_gemini_sync(prompt: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return "API credentials missing."

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    
    # INVIKA Persona
    system_instruction = "You are INVIKA, a helpful AI assistant. Respond efficiently and precisely. Keep answers short for voice synthesis."
    
    final_prompt = f"{system_instruction}\n\nUser: {prompt}\nINVIKA:"

    payload = {
        "contents":[{"role":"user","parts":[{"text":final_prompt}]}]
    }

    try:
        r = requests.post(url, params={"key": api_key}, json=payload, timeout=30)
        r.raise_for_status()
        return r.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        return "Processing error."

# -------------------- routes --------------------
@app.get("/")
async def index():
    return HTMLResponse(HTML)

@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            msg = await ws.receive_json()
            text = msg.get("text","").strip()
            if not text: continue

            reply = await asyncio.to_thread(call_gemini_sync, text)
            await ws.send_json({"type":"ai","text":reply})
    except WebSocketDisconnect:
        pass

# # app.py
# import os
# import asyncio
# import logging
# import requests
# from dotenv import load_dotenv

# from fastapi import FastAPI, WebSocket, WebSocketDisconnect
# from fastapi.responses import HTMLResponse

# # -------------------- setup --------------------
# load_dotenv()
# logging.basicConfig(level=logging.INFO)
# log = logging.getLogger("invika")

# app = FastAPI()

# # -------------------- INVIKA UI HTML --------------------
# HTML = """
# <!doctype html>
# <html>
# <head>
# <meta charset="utf-8"/>
# <meta name="viewport" content="width=device-width,initial-scale=1"/>
# <title>INVIKA • SYSTEM ONLINE</title>
# <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;700&display=swap" rel="stylesheet">

# <style>
# :root {
#   --primary: #00f3ff;
#   --secondary: #0066aa;
#   --bg: #050510;
#   --glass: rgba(0, 243, 255, 0.1);
# }

# body {
#   margin: 0;
#   height: 100vh;
#   background-color: var(--bg);
#   background-image: 
#     radial-gradient(circle at 50% 50%, rgba(0, 50, 100, 0.2) 0%, transparent 60%),
#     linear-gradient(0deg, rgba(0, 243, 255, 0.03) 1px, transparent 1px),
#     linear-gradient(90deg, rgba(0, 243, 255, 0.03) 1px, transparent 1px);
#   background-size: 100% 100%, 40px 40px, 40px 40px;
#   color: var(--primary);
#   font-family: 'Orbitron', sans-serif;
#   display: flex;
#   align-items: center;
#   justify-content: center;
#   overflow: hidden;
# }

# .hud-container {
#   width: 600px;
#   max-width: 95%;
#   border: 1px solid var(--primary);
#   background: rgba(0, 20, 40, 0.85);
#   box-shadow: 0 0 20px rgba(0, 243, 255, 0.2), inset 0 0 40px rgba(0, 243, 255, 0.1);
#   border-radius: 12px;
#   padding: 30px;
#   position: relative;
#   backdrop-filter: blur(5px);
# }

# /* Corner Accents */
# .corner {
#   position: absolute;
#   width: 20px;
#   height: 20px;
#   border: 2px solid var(--primary);
#   transition: all 0.3s ease;
# }
# .tl { top: -2px; left: -2px; border-bottom: none; border-right: none; }
# .tr { top: -2px; right: -2px; border-bottom: none; border-left: none; }
# .bl { bottom: -2px; left: -2px; border-top: none; border-right: none; }
# .br { bottom: -2px; right: -2px; border-top: none; border-left: none; }

# /* Arc Reactor */
# .reactor-container {
#   display: flex;
#   justify-content: center;
#   margin: 30px 0;
#   position: relative;
# }

# .reactor {
#   width: 180px;
#   height: 180px;
#   border-radius: 50%;
#   border: 4px solid var(--secondary);
#   box-shadow: 0 0 30px var(--secondary);
#   position: relative;
#   display: flex;
#   align-items: center;
#   justify-content: center;
# }

# .core {
#   width: 90px;
#   height: 90px;
#   background: radial-gradient(circle, #fff, var(--primary));
#   border-radius: 50%;
#   box-shadow: 0 0 40px var(--primary);
#   z-index: 2;
#   transition: all 0.3s;
# }

# .ring {
#   position: absolute;
#   width: 160px;
#   height: 160px;
#   border-radius: 50%;
#   border: 2px solid transparent;
#   border-top: 2px solid var(--primary);
#   border-bottom: 2px solid var(--primary);
#   animation: spin 4s linear infinite;
# }

# .ring.inner {
#   width: 120px;
#   height: 120px;
#   border: 2px solid transparent;
#   border-left: 2px solid var(--primary);
#   border-right: 2px solid var(--primary);
#   animation: spin-rev 3s linear infinite;
# }

# /* States */
# .reactor.listening .core { box-shadow: 0 0 70px #fff; background: #fff; }
# .reactor.speaking .core { background: #ff4d6d; box-shadow: 0 0 70px #ff4d6d; animation: pulse 0.5s infinite alternate; }
# .reactor.thinking .ring { animation-duration: 0.5s; border-color: #ffc107; }

# /* Logs */
# #log {
#   height: 150px;
#   overflow-y: auto;
#   border-top: 1px solid var(--secondary);
#   border-bottom: 1px solid var(--secondary);
#   margin-top: 20px;
#   padding: 10px;
#   font-size: 14px;
#   font-family: 'Consolas', monospace;
#   background: rgba(0, 0, 0, 0.3);
#   scrollbar-width: thin;
#   scrollbar-color: var(--primary) transparent;
# }
# .msg.user { color: #aaa; text-align: right; }
# .msg.ai { color: var(--primary); text-shadow: 0 0 5px var(--primary); }
# .msg.system { color: #ffc107; font-size: 12px; text-transform: uppercase; }

# #startBtn {
#   width: 100%;
#   padding: 15px;
#   background: var(--primary);
#   color: #000;
#   font-weight: bold;
#   font-size: 18px;
#   border: none;
#   cursor: pointer;
#   text-transform: uppercase;
#   clip-path: polygon(10px 0, 100% 0, 100% calc(100% - 10px), calc(100% - 10px) 100%, 0 100%, 0 10px);
#   margin-bottom: 10px;
# }

# @keyframes spin { 100% { transform: rotate(360deg); } }
# @keyframes spin-rev { 100% { transform: rotate(-360deg); } }
# @keyframes pulse { 100% { transform: scale(1.1); } }
# </style>
# </head>

# <body>

# <div class="hud-container">
#   <div class="corner tl"></div><div class="corner tr"></div>
#   <div class="corner bl"></div><div class="corner br"></div>

#   <h3 style="text-align:center; letter-spacing: 4px; margin:0 0 10px 0;">I.N.V.I.K.A. INTERFACE</h3>
#   <div style="text-align:center; margin-bottom: 20px; font-size:12px; color:var(--secondary)">
#     STATUS: <span id="status">STANDBY</span>
#   </div>

#   <div class="reactor-container">
#     <div id="reactor" class="reactor">
#       <div class="ring"></div>
#       <div class="ring inner"></div>
#       <div class="core"></div>
#     </div>
#   </div>

#   <button id="startBtn">INITIALIZE SYSTEM</button>

#   <div id="log"></div>
# </div>

# <script>
# /* ---------------- CONSTANTS & STATE ---------------- */
# const reactor = document.getElementById("reactor");
# const statusEl = document.getElementById("status");
# const logEl = document.getElementById("log");
# const startBtn = document.getElementById("startBtn");

# const ws = new WebSocket("ws://" + location.host + "/ws");
# const WAKE_WORD = "invika"; 

# let recognition = null;
# let listening = false;
# let synthSpeaking = false;
# let wakeActive = false;
# let audioAllowed = false;

# /* ---------------- HELPERS ---------------- */
# function logMsg(role, text){
#   const d = document.createElement("div");
#   d.className = "msg " + role;
#   d.innerText = (role === 'ai' ? 'INVIKA' : role).toUpperCase() + ": " + text;
#   logEl.appendChild(d);
#   logEl.scrollTop = logEl.scrollHeight;
# }

# function setState(s){
#   reactor.className = "reactor " + s;
#   statusEl.innerText = s.toUpperCase() || "IDLE";
# }

# function openApp(url){
#   logMsg("system", "Accessing external module...");
#   speak("Accessing module.");
#   window.open(url, '_blank');
# }

# /* ---------------- AUDIO ---------------- */
# function speak(text){
#   if(!text || !audioAllowed) return;

#   if(listening && recognition) recognition.stop();
  
#   synthSpeaking = true;
#   setState("speaking");
  
#   const u = new SpeechSynthesisUtterance(text);
#   // Try to find a good voice
#   const voices = speechSynthesis.getVoices();
#   const preferred = voices.find(v => v.name.includes("Google US English") || v.name.includes("Microsoft David"));
#   if(preferred) u.voice = preferred;
  
#   u.onend = () => {
#     synthSpeaking = false;
#     if(recognition) {
#         try { recognition.start(); } catch(e){} 
#     }
#   };
#   speechSynthesis.cancel();
#   speechSynthesis.speak(u);
# }

# /* ---------------- SPEECH RECOGNITION ---------------- */
# function initRecognition(){
#   const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
#   if(!SR){
#     logMsg("system","VOICE MODULE NOT DETECTED (USE CHROME)");
#     return;
#   }

#   recognition = new SR();
#   recognition.lang = "en-US";
#   recognition.continuous = true;

#   recognition.onstart = () => {
#     listening = true;
#     setState("listening");
#   };

#   recognition.onend = () => {
#     listening = false;
#     if(!synthSpeaking){
#       setTimeout(() => { try { recognition.start(); } catch(e){} }, 300);
#     }
#   };

#   recognition.onresult = (e) => {
#     const text = e.results[e.results.length-1][0].transcript.trim().toLowerCase();

#     // --- HIDDEN COMMANDS ---
#     if(text.includes("open spotify")) { openApp('https://open.spotify.com'); return; }
#     if(text.includes("open linkedin")) { openApp('https://www.linkedin.com'); return; }
#     if(text.includes("open gmail")) { openApp('https://mail.google.com'); return; }
#     if(text.includes("open instagram")) { openApp('https://www.instagram.com'); return; }

#     // Wake Word Logic
#     if(!wakeActive){
#       if(text.includes(WAKE_WORD) || text.includes("hey invika")){
#         wakeActive = true;
#         speak("Online.");
#       }
#       return;
#     }

#     logMsg("user", text);
#     ws.send(JSON.stringify({text}));
#     setState("thinking");
#   };
# }

# /* ---------------- INITIALIZATION ---------------- */
# startBtn.onclick = () => {
#   audioAllowed = true;
#   const u = new SpeechSynthesisUtterance("System Initialized");
#   speechSynthesis.speak(u);

#   initRecognition();
#   recognition.start();

#   startBtn.style.display = 'none';
#   logMsg("system","SYSTEM ONLINE. AWAITING INPUT.");
#   speak("Invika interface online. Ready.");
# };

# /* ---------------- WEBSOCKET ---------------- */
# ws.onopen = () => logMsg("system","SERVER CONNECTED");
# ws.onmessage = (ev) => {
#   const data = JSON.parse(ev.data);
#   if(data.type === "ai"){
#     logMsg("ai", data.text);
#     speak(data.text);
#     wakeActive = false; 
#   }
# };
# </script>
# </body>
# </html>
# """

# # -------------------- Gemini Logic --------------------
# def call_gemini_sync(prompt: str) -> str:
#     api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
#     if not api_key:
#         return "API credentials missing."

#     url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    
#     # INVIKA Persona
#     system_instruction = "You are INVIKA. Respond efficiently. Be precise."
    
#     final_prompt = f"{system_instruction}\n\nUser: {prompt}\nINVIKA:"

#     payload = {
#         "contents":[{"role":"user","parts":[{"text":final_prompt}]}]
#     }

#     try:
#         r = requests.post(url, params={"key": api_key}, json=payload, timeout=30)
#         r.raise_for_status()
#         return r.json()["candidates"][0]["content"]["parts"][0]["text"]
#     except Exception as e:
#         return "Processing error."

# # -------------------- routes --------------------
# @app.get("/")
# async def index():
#     return HTMLResponse(HTML)

# @app.websocket("/ws")
# async def ws_endpoint(ws: WebSocket):
#     await ws.accept()
#     try:
#         while True:
#             msg = await ws.receive_json()
#             text = msg.get("text","").strip()
#             if not text: continue

#             reply = await asyncio.to_thread(call_gemini_sync, text)
#             await ws.send_json({"type":"ai","text":reply})
#     except WebSocketDisconnect:
#         pass