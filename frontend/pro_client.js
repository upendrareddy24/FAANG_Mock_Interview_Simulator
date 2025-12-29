// FAANG Simulator 2.0 Client Logic

// --- Constants ---
const WS_URL = `ws://${window.location.host}/ws/interview`; // Future WebSocket endpoint
const API_BASE = window.location.origin;

// --- State ---
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
    // Auto-connect simulates "joining lobby"
    connectWebSocket();
});

function connectWebSocket() {
    // Basic Stub for Phase 1 - Backend Support comes in Phase 3
    console.log("Connecting to Interview Engine...");
    connectionText.textContent = "Connecting...";
    statusIndicator.className = "w-2 h-2 rounded-full bg-yellow-500";

    // Simulate connection for UI check since backend WS endpoint isn't ready
    setTimeout(() => {
        isConnected = true;
        connectionText.textContent = "Connected (Mock)";
        statusIndicator.className = "w-2 h-2 rounded-full bg-green-500";
        addMessage('system', "Connected to FAANG Expert Agent (Simulated Mode).");
        addMessage('interviewer', "Hello. I'm your interviewer for this session. Let's start with a coding problem. Please explain your approach as you type.");
    }, 1000);
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
micBtn.addEventListener('click', () => {
    isRecording = !isRecording;
    micBtn.innerHTML = isRecording ? "🔴" : "🎤";
    micBtn.classList.toggle('bg-red-600', isRecording);
    if (isRecording) {
        addMessage('system', "Microphone activated (Visual Only - Backend Integration Pending).");
    }
});
