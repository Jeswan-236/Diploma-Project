(function () {
    // Inject Chatbot HTML
    const chatbotHTML = `
    <!-- AI Help Chat Widget -->
    <div id="aiHelpButton" title="Ask AI" aria-label="Ask AI"
        style="position:fixed;right:22px;bottom:22px;z-index:1200;">
        <button id="openAiHome"
            style="width:64px;height:64px;border-radius:999px;border:0;background:linear-gradient(135deg,#6366f1,#8b5cf6);color:white;box-shadow:0 12px 30px rgba(99,102,241,0.25);cursor:pointer;font-size:20px;">🤖</button>
    </div>

    <div id="aiPanelHome"
        style="position:fixed;right:22px;bottom:100px;width:360px;max-width:92vw;background:linear-gradient(180deg,#071029,#0b1222);border-radius:12px;box-shadow:0 20px 60px rgba(2,6,18,0.8);display:none;z-index:1200;overflow:hidden;font-family:Poppins, sans-serif;">
        <div
            style="display:flex;align-items:center;justify-content:space-between;padding:12px 14px;border-bottom:1px solid rgba(255,255,255,0.03);">
            <div style="display:flex;gap:10px;align-items:center;">
                <div
                    style="width:36px;height:36px;border-radius:8px;background:linear-gradient(90deg,#fff,#e6ecff);display:flex;align-items:center;justify-content:center;color:#0b0e1f;font-weight:700;">
                    AI</div>
                <div style="font-weight:700;color:#e6ecff;">Study Assistant</div>
            </div>
            <div style="display:flex;gap:8px;align-items:center;">
                <button id="aiSettingsToggleHome" title="Settings"
                    style="background:transparent;border:0;color:#9fb0ff;cursor:pointer">⚙</button>
                <button id="aiClearHome" title="Clear"
                    style="background:transparent;border:0;color:#9fb0ff;cursor:pointer">Clear</button>
                <button id="aiCloseHome" title="Close"
                    style="background:transparent;border:0;color:#9fb0ff;cursor:pointer">✕</button>
            </div>
        </div>
        <div id="aiSettingsHome"
            style="display:none;padding:10px 12px;border-bottom:1px solid rgba(255,255,255,0.02);background:rgba(255,255,255,0.01);">
            <div style="display:flex;gap:8px;align-items:center;margin-bottom:8px;">
                <label style="color:#9fb0ff;min-width:72px;">Mode</label>
                <select id="aiModeHome"
                    style="flex:1;padding:6px;border-radius:6px;background:transparent;border:1px solid rgba(255,255,255,0.04);color:blueviolet;">
                    <option value="offline">Offline (built-in)</option>
                    <option value="remote">Remote LLM (API)</option>
                    <option value="local">Local model (placeholder)</option>
                </select>
            </div>
            <div style="display:flex;gap:8px;align-items:center;margin-bottom:8px;">
                <label style="color:#9fb0ff;min-width:72px;">Endpoint</label>
                <input id="aiEndpointHome" placeholder="https://api.example.com/ai"
                    style="flex:1;padding:6px;border-radius:6px;background:transparent;border:1px solid rgba(255,255,255,0.04);color:#e6ecff;">
            </div>
            <div style="display:flex;gap:8px;align-items:center;">
                <label style="color:#9fb0ff;min-width:72px;">API Key</label>
                <input id="aiKeyHome" placeholder="Optional - Bearer token"
                    style="flex:1;padding:6px;border-radius:6px;background:transparent;border:1px solid rgba(255,255,255,0.04);color:#e6ecff;">
            </div>
            <div style="display:flex;gap:8px;justify-content:flex-end;margin-top:8px;">
                <button id="aiSaveSettingsHome"
                    style="background:transparent;border:1px solid rgba(255,255,255,0.04);color:#9fb0ff;padding:6px 8px;border-radius:8px;cursor:pointer">Save</button>
                <button id="aiResetSettingsHome"
                    style="background:transparent;border:1px solid rgba(255,255,255,0.04);color:#9fb0ff;padding:6px 8px;border-radius:8px;cursor:pointer">Reset</button>
            </div>
            <div style="margin-top:8px;color:#9fb0ff;font-size:12px;">Note: Storing API keys in localStorage is
                convenient for demos but not secure for production.</div>
        </div>
        <div id="aiMessagesHome"
            style="padding:12px;max-height:320px;overflow:auto;display:flex;flex-direction:column;gap:8px;background:linear-gradient(180deg,rgba(255,255,255,0.01),transparent);">
        </div>
        <div style="padding:10px;border-top:1px solid rgba(255,255,255,0.03);display:flex;gap:8px;align-items:center;">
            <input id="aiInputHome" placeholder="Ask a question (e.g. 'how to center div?')"
                style="flex:1;padding:10px;border-radius:8px;border:1px solid rgba(255,255,255,0.04);background:transparent;color:#e6ecff;outline:none;">
            <button id="aiSendHome" class="glow-btn" style="height:40px;padding:0 12px;cursor:pointer;">Send</button>
        </div>
        <div
            style="padding:8px 12px;border-top:1px solid rgba(255,255,255,0.02);display:flex;gap:8px;flex-wrap:wrap;background:rgba(255,255,255,0.01);">
            <button class="ai-suggest-home" data-q="center div horizontally"
                style="background:transparent;border:1px solid rgba(255,255,255,0.03);color:#9fb0ff;padding:6px 8px;border-radius:8px;cursor:pointer">Center
                div</button>
            <button class="ai-suggest-home" data-q="flexbox vs grid"
                style="background:transparent;border:1px solid rgba(255,255,255,0.03);color:#9fb0ff;padding:6px 8px;border-radius:8px;cursor:pointer">Flexbox
                vs Grid</button>
            <button class="ai-suggest-home" data-q="what is a matrix"
                style="background:transparent;border:1px solid rgba(255,255,255,0.03);color:#9fb0ff;padding:6px 8px;border-radius:8px;cursor:pointer">Matrices</button>
            <button class="ai-suggest-home" data-q="reverse string javascript"
                style="background:transparent;border:1px solid rgba(255,255,255,0.03);color:#9fb0ff;padding:6px 8px;border-radius:8px;cursor:pointer">Reverse
                string</button>
        </div>
    </div>
    `;

    document.body.insertAdjacentHTML('beforeend', chatbotHTML);

    const openBtn = document.getElementById('openAiHome');
    const panel = document.getElementById('aiPanelHome');
    const closeBtn = document.getElementById('aiCloseHome');
    const clearBtn = document.getElementById('aiClearHome');
    const sendBtn = document.getElementById('aiSendHome');
    const input = document.getElementById('aiInputHome');
    const messages = document.getElementById('aiMessagesHome');
    const suggests = Array.from(document.querySelectorAll('.ai-suggest-home'));
    const settingsToggle = document.getElementById('aiSettingsToggleHome');
    const settingsPanel = document.getElementById('aiSettingsHome');
    const modeSelect = document.getElementById('aiModeHome');
    const endpointInput = document.getElementById('aiEndpointHome');
    const keyInput = document.getElementById('aiKeyHome');
    const saveSettingsBtn = document.getElementById('aiSaveSettingsHome');
    const resetSettingsBtn = document.getElementById('aiResetSettingsHome');

    // Prevent double-initialization if the script runs more than once
    if (panel.dataset.aiInit) return;
    panel.dataset.aiInit = '1';

    // Load settings from localStorage
    const SETTINGS_KEY = 'ai_help_settings_v1';
    function loadSettings() {
        try {
            const s = JSON.parse(localStorage.getItem(SETTINGS_KEY) || '{}');
            modeSelect.value = s.mode || 'offline';
            endpointInput.value = s.endpoint || '';
            keyInput.value = s.key || '';
        } catch (e) { }
    }
    function saveSettingsToStorage() {
        const s = { mode: modeSelect.value, endpoint: endpointInput.value.trim(), key: keyInput.value.trim() };
        try { localStorage.setItem(SETTINGS_KEY, JSON.stringify(s)); } catch (e) { }
    }
    function resetSettingsToDefault() {
        try { localStorage.removeItem(SETTINGS_KEY); } catch (e) { }
        loadSettings();
    }

    function addMessage(text, who = 'ai', save = true) {
        const el = document.createElement('div');
        el.style.padding = '10px'; el.style.borderRadius = '8px'; el.style.maxWidth = '100%';
        if (who === 'user') { el.style.background = 'linear-gradient(90deg,rgba(99,102,241,0.12),rgba(99,102,241,0.06))'; el.style.color = '#e6ecff'; el.style.alignSelf = 'flex-end'; el.innerText = text; }
        else { el.style.background = 'rgba(255,255,255,0.02)'; el.style.color = '#dbe7ff'; el.style.alignSelf = 'flex-start'; el.innerText = text; }
        messages.appendChild(el); messages.scrollTop = messages.scrollHeight;
        if (!save) return;
        try { const h = JSON.parse(localStorage.getItem('ai_help_history') || '[]'); h.push({ who, text, ts: Date.now() }); localStorage.setItem('ai_help_history', JSON.stringify(h)); } catch (e) { }
    }

    function loadHistory() {
        try {
            messages.innerHTML = '';
            const h = JSON.parse(localStorage.getItem('ai_help_history') || '[]');
            h.forEach(m => addMessage(m.text, m.who, false));
        } catch (e) { }
    }

    // Expanded offline rule-based responder
    function simpleResponder(q) {
        const s = (q || '').toLowerCase();
        if (!s) return "Tell me what you want help with — e.g. 'center div' or 'reverse string JS'";
        if (/center|horizontal|vertical/.test(s)) return "To center a div: horizontal -> `margin:0 auto;` on a block with width. Both axes -> parent: `display:flex;justify-content:center;align-items:center;`.";
        if (/box model|box-model/.test(s)) return "Box model: `content` -> `padding` -> `border` -> `margin`. Use `box-sizing: border-box;` to include padding/border in width.";
        if (/flexbox|flex box/.test(s)) return "Flexbox: `display:flex;` use `justify-content` (main axis) and `align-items` (cross axis). Good for 1D layouts.";
        if (/grid|grid layout/.test(s)) return "CSS Grid: `display:grid; grid-template-columns: ...;` Great for 2D page layouts and explicit placement.";
        if (/reverse.*string|reverse string/.test(s)) return "JS: `s.split('').reverse().join('')` or for arrays use `arr.reverse()`.";
        if (/array.*map|map function/.test(s)) return "`array.map(x => x*2)` applies a transform to each element and returns a new array.";
        if (/dom select|queryselector/.test(s)) return "Use `document.querySelector('.class')` for first match or `document.querySelectorAll('.class')` for all matches. Use `element.addEventListener('click', handler)` to attach handlers.";
        if (/fetch|ajax|http request/.test(s)) return "Use `fetch(url, {method:'GET'})` then `response.json()` for JSON. Handle errors with `catch` or `try`/`await`.";
        if (/sql|select|join/.test(s)) return "SQL: `SELECT cols FROM table WHERE condition;` Use `JOIN` to combine related tables, e.g., `INNER JOIN` on matching keys.";
        if (/matrix|matrices|determinant/.test(s)) return "A matrix is a 2D array. Compute determinants for square matrices and use row reduction for solving systems.";
        if (/differentiat|derivative/.test(s)) return "Derivative: rate of change. Example: d/dx x^n = n * x^(n-1).";
        if (/integrat|integral/.test(s)) return "Integral: area under curve. Example: ∫ x^n dx = x^(n+1)/(n+1) + C (n ≠ -1).";
        if (/git|commit|push/.test(s)) return "Git basics: `git add .`, `git commit -m \"msg\"`, `git push origin main`. Use branches for features.";
        if (/python/.test(s)) return "Python basics: define with `def fn():`, use lists for arrays, `s[::-1]` reverses a string.";
        return null; // let remote fallback handle unknowns
    }

    // Call a remote AI backend (simple POST contract). Expects JSON {answer:string} or {choices:[{text}]}
    async function callRemoteAI(q) {
        const settings = JSON.parse(localStorage.getItem(SETTINGS_KEY) || '{}');
        const endpoint = settings.endpoint || endpointInput.value.trim();
        const key = settings.key || keyInput.value.trim();
        if (!endpoint) return { ok: false, text: `No endpoint configured. Please set an endpoint in Settings.` };
        try {
            const body = JSON.stringify({ query: q });
            const headers = { 'Content-Type': 'application/json' };
            if (key) headers['Authorization'] = `Bearer ${key}`;
            const resp = await fetch(endpoint, { method: 'POST', headers, body, mode: 'cors' });
            if (!resp.ok) return { ok: false, text: `Remote error: ${resp.status} ${resp.statusText}` };
            const j = await resp.json();
            if (j.answer) return { ok: true, text: j.answer };
            if (j.choices && j.choices[0] && (j.choices[0].text || j.choices[0].message)) {
                return { ok: true, text: j.choices[0].text || j.choices[0].message };
            }
            return { ok: false, text: `Unexpected response from remote endpoint.` };
        } catch (e) { return { ok: false, text: `Request failed: ${e.message}` }; }
    }

    // Apply mode-specific colors for visual feedback
    function applyModeColor(mode) {
        try {
            if (mode === 'remote') {
                openBtn.style.background = 'linear-gradient(135deg,#06b6d4,#0ea5a3)';
                openBtn.style.boxShadow = '0 12px 30px rgba(6,182,212,0.2)';
                panel.style.boxShadow = '0 20px 60px rgba(6,182,212,0.12)';
            } else if (mode === 'local') {
                openBtn.style.background = 'linear-gradient(135deg,#f59e0b,#f97316)';
                openBtn.style.boxShadow = '0 12px 30px rgba(245,158,11,0.18)';
                panel.style.boxShadow = '0 20px 60px rgba(245,158,11,0.09)';
            } else { // offline
                openBtn.style.background = 'linear-gradient(135deg,#6366f1,#8b5cf6)';
                openBtn.style.boxShadow = '0 12px 30px rgba(99,102,241,0.25)';
                panel.style.boxShadow = '0 20px 60px rgba(2,6,18,0.8)';
            }
        } catch (e) { }
    }

    modeSelect.addEventListener('change', () => { applyModeColor(modeSelect.value); });

    // UI handlers
    openBtn.addEventListener('click', () => { panel.style.display = 'block'; loadSettings(); loadHistory(); input.focus(); });
    closeBtn.addEventListener('click', () => { panel.style.display = 'none'; });
    clearBtn.addEventListener('click', () => { messages.innerHTML = ''; localStorage.removeItem('ai_help_history'); });

    settingsToggle.addEventListener('click', () => { settingsPanel.style.display = settingsPanel.style.display === 'none' ? 'block' : 'none'; });
    saveSettingsBtn.addEventListener('click', () => { saveSettingsToStorage(); loadSettings(); settingsPanel.style.display = 'none'; addMessage('Settings saved.', 'ai'); });
    resetSettingsBtn.addEventListener('click', () => { resetSettingsToDefault(); addMessage('Settings reset.', 'ai'); });

    async function handleSend() {
        const q = input.value.trim(); if (!q) return;
        addMessage(q, 'user');
        input.value = ''; input.focus();
        const offline = simpleResponder(q);
        const s = JSON.parse(localStorage.getItem(SETTINGS_KEY) || '{}');
        const mode = s.mode || modeSelect.value || 'offline';
        if (mode === 'offline') {
            if (offline) { setTimeout(() => addMessage(offline, 'ai'), 200 + Math.random() * 400); return; }
            // fallback link
            addMessage(`I don't have a full answer offline. Search: https://www.youtube.com/results?search_query=${encodeURIComponent(q)}`, 'ai');
            return;
        }

        // remote mode
        sendBtn.disabled = true; addMessage('Thinking...', 'ai', false);
        const res = await callRemoteAI(q);
        sendBtn.disabled = false;
        if (res.ok) { addMessage(res.text, 'ai'); }
        else {
            if (offline) addMessage(offline, 'ai');
            else addMessage(res.text + ' — fallback: https://www.youtube.com/results?search_query=' + encodeURIComponent(q), 'ai');
        }
    }

    sendBtn.addEventListener('click', () => { handleSend(); });
    input.addEventListener('keydown', (e) => { if (e.key === 'Enter') { e.preventDefault(); handleSend(); } });

    suggests.forEach(b => b.addEventListener('click', () => { input.value = b.dataset.q; handleSend(); }));

    // Initialize settings into UI on load
    loadSettings();

})();
