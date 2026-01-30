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

# -------------------- HTML UI --------------------
HTML = """
<!doctype html>
<html>
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>INVIKA — Live Companion</title>

<style>
html,body{
  height:100%;margin:0;font-family:system-ui;
  background:linear-gradient(180deg,#0f0c29,#302b63);
  color:#fff;display:flex;align-items:center;justify-content:center
}
.container{
  width:520px;max-width:90%;
  background:rgba(255,255,255,0.04);
  border-radius:18px;padding:22px;
  box-shadow:0 20px 60px rgba(0,0,0,0.6)
}
.orb{
  width:180px;height:180px;border-radius:50%;
  margin:16px auto;
  background:radial-gradient(circle at 30% 30%, #6fbfff, #06335a);
  display:flex;align-items:center;justify-content:center;
  font-weight:800;letter-spacing:1px;
  transition:all .3s
}
.orb.listening{box-shadow:0 0 80px #00d2ff}
.orb.thinking{background:#ffc107}
.orb.speaking{
  background:#ff4d6d;
  animation:pulse .8s infinite alternate
}
@keyframes pulse{
  from{transform:scale(1)}
  to{transform:scale(1.08)}
}
#log{
  height:180px;overflow:auto;
  background:rgba(0,0,0,0.2);
  border-radius:10px;padding:10px;
  font-size:14px
}
.msg{margin-bottom:8px}
.system{opacity:.7}
.user{color:#00d2ff}
.ai{color:#ffd166}
button{
  margin-top:12px;
  padding:12px 18px;
  font-size:16px;
  border:none;border-radius:10px;
  cursor:pointer;
  background:#00d2ff;color:#032
}
</style>
</head>

<body>
<div class="container">
  <h2>INVIKA • Live Companion</h2>

  <div id="orb" class="orb">INVIKA</div>
  <div id="status">Idle</div>

  <button id="startBtn">▶ Start Invika</button>

  <div id="log"></div>
</div>

<script>
/* ---------------- state ---------------- */
const orb = document.getElementById("orb");
const statusEl = document.getElementById("status");
const logEl = document.getElementById("log");
const startBtn = document.getElementById("startBtn");

// Connect WS globally
const ws = new WebSocket("ws://" + location.host + "/ws");

let recognition = null;
let listening = false;
let synthSpeaking = false;
let wakeActive = false;
let audioAllowed = false; 

const WAKE_WORD = "hey invika";

/* ---------------- helpers ---------------- */
function logMsg(role, text){
  const d = document.createElement("div");
  d.className = "msg " + role;
  d.innerText = role + ": " + text;
  logEl.appendChild(d);
  logEl.scrollTop = logEl.scrollHeight;
}

function setState(s){
  orb.className = "orb " + s;
  statusEl.innerText = s || "idle";
}

function speak(text){
  if(!text || !audioAllowed) return;

  // Stop listening while speaking to avoid hearing ourselves
  if(listening && recognition) {
    recognition.stop();
  }
  
  synthSpeaking = true;
  setState("speaking");
  
  const u = new SpeechSynthesisUtterance(text);
  u.onend = () => {
    synthSpeaking = false;
    // Restart listening after speaking finishes
    if(recognition) {
        try { recognition.start(); } catch(e){} 
    }
  };
  speechSynthesis.cancel();
  speechSynthesis.speak(u);
}

/* ---------------- speech recognition ---------------- */
function initRecognition(){
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if(!SR){
    logMsg("system","SpeechRecognition not supported (Use Chrome/Edge)");
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
    // Only auto-restart if we aren't currently speaking
    if(!synthSpeaking){
      setTimeout(() => {
        try { recognition.start(); } catch(e){}
      }, 300);
    }
  };

  recognition.onresult = (e) => {
    const text = e.results[e.results.length-1][0].transcript
      .trim().toLowerCase();

    // Wake word logic
    if(!wakeActive){
      if(text.includes(WAKE_WORD)){
        wakeActive = true;
        speak("Yes?");
      }
      return;
    }

    logMsg("user", text);
    ws.send(JSON.stringify({text}));
    setState("thinking");
  };
}

/* ---------------- START BUTTON ---------------- */
startBtn.onclick = () => {
  audioAllowed = true;
  
  // Unlock audio engine
  const u = new SpeechSynthesisUtterance("");
  speechSynthesis.speak(u);

  initRecognition();
  recognition.start();

  startBtn.remove();
  
  // Manual greeting so the user hears it immediately
  logMsg("system","Invika online.");
  speak("Invika is online. Say Hey Invika to wake me.");
};

/* ---------------- websocket ---------------- */
ws.onopen = () => logMsg("system","Connected");

ws.onmessage = (ev) => {
  const data = JSON.parse(ev.data);

  // Ignore initial server greeting (since we do it manually on click)
  if(data.type === "greeting"){
    // optional: just log it, don't speak it to avoid double talk
    logMsg("ai", data.text); 
  }

  if(data.type === "ai"){
    logMsg("ai", data.text);
    speak(data.text);
    wakeActive = false; // Go back to sleep after answering
  }
};

ws.onclose = () => logMsg("system","Disconnected");
</script>
<script>
# /* ---------------- state ---------------- */
# const orb = document.getElementById("orb");
# const statusEl = document.getElementById("status");
# const logEl = document.getElementById("log");
# const startBtn = document.getElementById("startBtn");

# const ws = new WebSocket("ws://" + location.host + "/ws");

# let recognition = null;
# let listening = false;
# let synthSpeaking = false;
# let wakeActive = false;
# let audioAllowed = false; // <--- FIX: Track if audio is permitted

# const WAKE_WORD = "hey invika";

# /* ---------------- helpers ---------------- */
# function logMsg(role, text){
#   const d = document.createElement("div");
#   d.className = "msg " + role;
#   d.innerText = role + ": " + text;
#   logEl.appendChild(d);
#   logEl.scrollTop = logEl.scrollHeight;
# }

# function setState(s){
#   orb.className = "orb " + s;
#   statusEl.innerText = s || "idle";
# }

# function speak(text){
#   if(!text) return;
#   if(!audioAllowed) return; // <--- FIX: Block audio before user interaction
  
#   synthSpeaking = true;
#   setState("speaking");
#   const u = new SpeechSynthesisUtterance(text);
#   u.onend = () => {
#     synthSpeaking = false;
#     setState("listening");
#   };
#   speechSynthesis.cancel();
#   speechSynthesis.speak(u);
# }

# /* ---------------- speech recognition ---------------- */
# function initRecognition(){
#   const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
#   if(!SR){
#     logMsg("system","SpeechRecognition not supported");
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
#       setTimeout(()=>recognition.start(),300);
#     }
#   };

#   recognition.onresult = (e) => {
#     const text = e.results[e.results.length-1][0].transcript
#       .trim().toLowerCase();

#     if(!wakeActive){
#       if(text.includes(WAKE_WORD)){
#         wakeActive = true;
#         speak("Yes. How can I help?");
#       }
#       return;
#     }

#     logMsg("user", text);
#     ws.send(JSON.stringify({text}));
#     setState("thinking");
#   };
# }

# /* ---------------- START BUTTON (CRITICAL) ---------------- */
# startBtn.onclick = () => {
#   audioAllowed = true; // <--- FIX: Enable audio on click

#   // unlock browser audio (MANDATORY)
#   const u = new SpeechSynthesisUtterance("");
#   speechSynthesis.speak(u);
#   speechSynthesis.cancel();

#   initRecognition();
#   recognition.start();

#   startBtn.remove();
#   logMsg("system","Invika online. Say 'Hey Invika'");
# };

# /* ---------------- websocket ---------------- */
# ws.onopen = () => logMsg("system","Connected");

# ws.onmessage = (ev) => {
#   const data = JSON.parse(ev.data);

#   if(data.type === "greeting"){
#     logMsg("ai", data.text);
#     speak(data.text);
#   }

#   if(data.type === "ai"){
#     logMsg("ai", data.text);
#     speak(data.text);
#     wakeActive = false;
#   }
# };

# ws.onclose = () => logMsg("system","Disconnected");
# </script>
</body>
</html>
"""

# -------------------- Gemini helper --------------------
def call_gemini_sync(prompt: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return "Gemini API key not configured."

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    payload = {
        "contents":[{"role":"user","parts":[{"text":prompt}]}]
    }

    r = requests.post(url, params={"key": api_key}, json=payload, timeout=30)
    r.raise_for_status()
    return r.json()["candidates"][0]["content"]["parts"][0]["text"]

# -------------------- routes --------------------
@app.get("/")
async def index():
    return HTMLResponse(HTML)

@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await ws.accept()
    log.info("Client connected")

    await ws.send_json({
        "type":"greeting",
        "text":"Hello. I am Invika. Say 'Hey Invika' to wake me."
    })

    try:
        while True:
            msg = await ws.receive_json()
            text = msg.get("text","").strip()
            if not text:
                continue

            reply = await asyncio.to_thread(call_gemini_sync, text)
            await ws.send_json({"type":"ai","text":reply})

    except WebSocketDisconnect:
        log.info("Client disconnected")
