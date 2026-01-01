// FAANG Simulator 2.0 Client Logic

// --- Constants ---
const WS_URL = `ws://${window.location.host}/ws/interview`; // Future WebSocket endpoint
const API_BASE = window.location.origin;

// --- State ---
let sessionId = null;
let isConnected = false;
let isRecording = false;
let audioContext = null;
let ws = null;

// --- UI Elements ---
const statusIndicator = document.getElementById('ws-status');
const connectionText = document.getElementById('connection-text');
const chatContainer = document.getElementById('chat-container');
const micBtn = document.getElementById('mic-toggle');

// --- Initialization ---
document.addEventListener('DOMContentLoaded', () => {
    initWhiteboard();
    // Show Modal instead of auto-start
});

// --- Modal Logic ---
function selectRound(type) {
    document.getElementById('modal-backdrop').style.display = 'none';
    startRealSession(type);
}

window.selectRound = selectRound;

async function startRealSession(roundType = "coding") {
    connectionText.textContent = `Connecting to ${roundType === 'coding' ? 'Coding' : 'SysDesign'} Round...`;
    statusIndicator.className = "w-2 h-2 rounded-full bg-yellow-500";
    addMessage('system', `Initializing Secure Environment... Mode: ${roundType.toUpperCase()}`);

    try {
        const response = await fetch(`${API_BASE}/session/start`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                target_company: "Google",
                target_role: "Software Engineer",
                target_level: "L4",
                years_of_experience: 5,
                preferred_language: "Python",
                round_type: roundType,
                resume_text: "Experienced in Python and Distributed Systems."
            })
        });

        if (!response.ok) throw new Error("Failed to start session");

        const data = await response.json();
        sessionId = data.session_id;

        isConnected = true;
        connectionText.textContent = `Live (${roundType})`;
        statusIndicator.className = "w-2 h-2 rounded-full bg-green-500 animate-pulse";

        addMessage('system', "Session Established. AI Agent Active.");
        addMessage('interviewer', data.interviewer_message);

    } catch (e) {
        console.error(e);
        connectionText.textContent = "Connection Failed";
        statusIndicator.className = "w-2 h-2 rounded-full bg-red-500";
        addMessage('system', `Error: Could not connect to AI Engine. ${e.message}`);
    }
}

function addMessage(role, text) {
    const div = document.createElement('div');
    div.className = `chat-message ${role}`;
    div.textContent = text;
    chatContainer.appendChild(div);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// --- Whiteboard Logic ---
let isDrawing = false;
let lastX = 0;
let lastY = 0;
const canvas = document.getElementById('whiteboard');
const ctx = canvas.getContext('2d');

function initWhiteboard() {
    // Resize canvas to match container
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    canvas.addEventListener('mousedown', startDrawing);
    canvas.addEventListener('mousemove', draw);
    canvas.addEventListener('mouseup', stopDrawing);
    canvas.addEventListener('mouseout', stopDrawing);
}

function resizeCanvas() {
    const parent = canvas.parentElement;
    canvas.width = parent.clientWidth;
    canvas.height = parent.clientHeight;
}

function startDrawing(e) {
    isDrawing = true;
    [lastX, lastY] = [e.offsetX, e.offsetY];
}

function draw(e) {
    if (!isDrawing) return;
    ctx.beginPath();
    ctx.moveTo(lastX, lastY);
    ctx.lineTo(e.offsetX, e.offsetY);
    ctx.strokeStyle = '#000';
    ctx.lineWidth = 2;
    ctx.lineCap = 'round';
    ctx.stroke();
    [lastX, lastY] = [e.offsetX, e.offsetY];
}

function stopDrawing() {
    isDrawing = false;
}

function clearWhiteboard() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
}

// --- Mic Logic ---
// Browser support check
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition = null;

if (SpeechRecognition) {
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.lang = 'en-US';
    recognition.interimResults = false;

    recognition.onstart = function () {
        console.log("Voice recognition active.");
    };

    recognition.onresult = async function (event) {
        const transcript = event.results[0][0].transcript;
        console.log("Heard:", transcript);
        addMessage('candidate', transcript);

        // Stop recording UI
        isRecording = false;
        micBtn.innerHTML = "🎤";
        micBtn.classList.remove('bg-red-600');

        // Send to Backend
        await sendCandidateResponse(transcript);
    };

    recognition.onerror = function (event) {
        console.error("Speech recognition error", event.error);
        isRecording = false;
        micBtn.innerHTML = "🎤";
        micBtn.classList.remove('bg-red-600');
        addMessage('system', "Voice input failed or stopped.");
    };
}

micBtn.addEventListener('click', () => {
    if (!SpeechRecognition) {
        alert("Your browser does not support Web Speech API. Use Chrome.");
        return;
    }

    if (!isRecording) {
        // Start Recording
        isRecording = true;
        micBtn.innerHTML = "🔴";
        micBtn.classList.add('bg-red-600');
        try {
            recognition.start();
        } catch (e) {
            console.warn("Recognition already started");
        }
    } else {
        // Stop Recording
        isRecording = false;
        micBtn.innerHTML = "🎤";
        micBtn.classList.remove('bg-red-600');
        try {
            recognition.stop();
        } catch (e) { }
    }
});

// --- Chat Input Logic ---
document.getElementById('chat-input').addEventListener('keypress', async (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        const text = e.target.value.trim();
        if (text) {
            addMessage('candidate', text);
            e.target.value = '';
            await sendCandidateResponse(text);
        }
    }
});

async function sendCandidateResponse(text) {
    if (!sessionId) return;

    try {
        const response = await fetch(`${API_BASE}/session/${sessionId}/respond`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ candidate_message: text })
        });
        const data = await response.json();
        addMessage('interviewer', data.interviewer_message);
    } catch (e) {
        addMessage('system', "Error sending message: " + e.message);
    }
}

// --- Code Execution ---
async function runCode() {
    if (!sessionId) {
        alert("Session not active. Wait for connection.");
        return;
    }

    const code = window.editor.getValue();
    const terminal = document.getElementById('terminal-output');
    terminal.innerHTML += `<div>> Running...</div>`;

    try {
        const response = await fetch(`${API_BASE}/session/${sessionId}/execute`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code: code })
        });

        const data = await response.json();

        // Show Output
        terminal.innerHTML += `<div class="text-white whitespace-pre-wrap">${data.output}</div>`;
        terminal.scrollTop = terminal.scrollHeight;

        // Show AI Feedback
        if (data.ai_feedback) {
            addMessage('interviewer', data.ai_feedback);
        }

    } catch (e) {
        terminal.innerHTML += `<div class="text-red-500">Execution Failed: ${e.message}</div>`;
    }
}
// Expose to window for HTML onclick
window.runCode = runCode;
