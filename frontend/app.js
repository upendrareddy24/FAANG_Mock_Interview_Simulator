const API_BASE = 'http://localhost:8000';
let sessionId = null;

const configSection = document.getElementById('config-section');
const interviewSection = document.getElementById('interview-section');
const evalSection = document.getElementById('eval-section');
const messagesDiv = document.getElementById('messages');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const startBtn = document.getElementById('start-btn');
const endBtn = document.getElementById('end-btn');

startBtn.addEventListener('click', async () => {
    const data = {
        target_company: document.getElementById('company').value,
        target_role: document.getElementById('role').value,
        target_level: document.getElementById('level').value,
        years_of_experience: parseInt(document.getElementById('experience').value),
        preferred_language: document.getElementById('language').value,
        resume_text: document.getElementById('resume').value
    };

    startBtn.disabled = true;
    startBtn.innerText = 'PREPARING INTERVIEW...';

    try {
        const response = await fetch(`${API_BASE}/session/start`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const result = await response.json();
        sessionId = result.session_id;

        configSection.style.display = 'none';
        interviewSection.style.display = 'grid';

        addMessage('interviewer', result.interviewer_message);
    } catch (error) {
        alert('Failed to connect to backend. Make sure the FastAPI server is running.');
        console.error(error);
    } finally {
        startBtn.disabled = false;
        startBtn.innerText = 'ENTER THE HOT SEAT';
    }
});

sendBtn.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

async function sendMessage() {
    const content = userInput.value.trim();
    if (!content || !sessionId) return;

    addMessage('candidate', content);
    userInput.value = '';

    // Disable input while interviewer "thinks"
    userInput.disabled = true;
    sendBtn.disabled = true;

    try {
        const response = await fetch(`${API_BASE}/session/${sessionId}/respond`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(content)
        });
        const result = await response.json();
        addMessage('interviewer', result.interviewer_message);
    } catch (error) {
        addMessage('interviewer', 'Error communicating with interviewer.');
    } finally {
        userInput.disabled = false;
        sendBtn.disabled = false;
        userInput.focus();
    }
}

function addMessage(role, content) {
    const div = document.createElement('div');
    div.className = `message ${role}`;
    div.innerText = content;
    messagesDiv.appendChild(div);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

endBtn.addEventListener('click', async () => {
    if (!confirm('Are you sure you want to end the interview and see your results?')) return;

    endBtn.disabled = true;
    endBtn.innerText = 'EVALUATING...';

    try {
        const response = await fetch(`${API_BASE}/session/${sessionId}/evaluate`, {
            method: 'POST'
        });
        const result = await response.json();
        showEvaluation(result);
    } catch (error) {
        alert('Evaluation failed.');
    } finally {
        endBtn.disabled = false;
        endBtn.innerText = 'FINISH';
    }
});

function showEvaluation(evalData) {
    interviewSection.style.display = 'none';
    evalSection.style.display = 'block';

    const scorecardDiv = document.getElementById('scorecard');
    scorecardDiv.innerHTML = '';

    for (const [key, value] of Object.entries(evalData.scorecard)) {
        const item = document.createElement('div');
        item.className = 'score-item glass';
        item.innerHTML = `
            <div class="score-label" style="font-size: 0.8rem; color: var(--text-secondary);">${key}</div>
            <div class="score-value">${value}/5</div>
        `;
        scorecardDiv.appendChild(item);
    }


    const feedbackDiv = document.getElementById('detailed-feedback');
    feedbackDiv.innerHTML = `
        <h3 style="color: var(--accent-color); margin: 1rem 0;">Recommendation: ${evalData.hiring_recommendation}</h3>
        <p><strong>Detailed Feedback:</strong> ${evalData.detailed_feedback}</p>
        <div style="margin-top: 1rem;">
            <strong>Strong Signals:</strong>
            <ul>${evalData.strong_signals.map(s => `<li>${s}</li>`).join('')}</ul>
        </div>
        <div style="margin-top: 1rem;">
            <strong>Weak Signals:</strong>
            <ul>${evalData.weak_signals.map(s => `<li>${s}</li>`).join('')}</ul>
        </div>
        <div style="margin-top: 1.5rem; padding: 1rem; background: rgba(59, 130, 246, 0.1); border-radius: 8px;">
            <strong>Ideal Solution Summary:</strong>
            <p>${evalData.ideal_solution_summary}</p>
        </div>
        <div style="margin-top: 1rem; padding: 1rem; background: rgba(16, 185, 129, 0.1); border-radius: 8px;">
            <strong>14-Day Improvement Roadmap:</strong>
            <p>${evalData.improvement_plan}</p>
        </div>
    `;
}

