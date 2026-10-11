/* Electronics Assistant frontend controller */
let currentChatMode = localStorage.getItem("chatMode") || "basic";

function getChatStorageKey() {
    return "electronicsChatHistory";
}

function escapeHtml(value) {
    return String(value ?? "").replace(/[&<>'"]/g, ch => ({"&":"&amp;","<":"&lt;",">":"&gt;","'":"&#39;",'"':"&quot;"}[ch]));
}

function saveChatHistory() {
    const messages = document.getElementById("chatMessages");
    if (!messages) return;
    const history = [];
    messages.querySelectorAll(".user-message, .bot-message").forEach(message => {
        history.push({
            role: message.classList.contains("user-message") ? "user" : "assistant",
            content: message.classList.contains("bot-message") ? message.innerHTML : message.textContent
        });
    });
    localStorage.setItem(getChatStorageKey(), JSON.stringify(history.slice(-100)));
    localStorage.setItem("chatMode", currentChatMode);
}

function renderWelcomeMessage() {
    const messages = document.getElementById("chatMessages");
    if (!messages) return;
    messages.innerHTML = `
        <div class="chat-empty-state">
            <div class="empty-state-title">How can I help you today?</div>
            <p>Ask about a concept, solve an ECE problem, debug code, or troubleshoot a project.</p>
            <div class="empty-state-hints">
                <button onclick="askSuggestion('Explain Ohm’s law with a simple example.')">Learn a concept</button>
                <button onclick="askSuggestion('Give me a beginner electronics project idea.')">Find a project</button>
                <button onclick="askSuggestion('Help me debug my code.')">Debug code</button>
            </div>
        </div>`;
}

function loadChatHistory() {
    const messages = document.getElementById("chatMessages");
    if (!messages) return;
    try {
        const saved = JSON.parse(localStorage.getItem(getChatStorageKey()) || "[]");
        if (!Array.isArray(saved) || !saved.length) return;
        messages.innerHTML = "";
        saved.forEach(item => {
            const message = document.createElement("div");
            message.className = item.role === "user" ? "user-message" : "bot-message";
            if (item.role === "user") message.textContent = item.content || "";
            else message.innerHTML = item.content || "";
            messages.appendChild(message);
        });
        messages.scrollTop = messages.scrollHeight;
    } catch (error) {
        console.error("Could not restore chat history", error);
    }
}

function updateModeUI() {
    document.querySelectorAll("#basicModeBtn").forEach(button => button.classList.toggle("active", currentChatMode === "basic"));
    document.querySelectorAll("#advancedModeBtn").forEach(button => button.classList.toggle("active", currentChatMode === "advanced"));
    document.querySelectorAll("#chatModeStatus").forEach(status => {
        status.textContent = currentChatMode === "advanced"
            ? "Advanced mode · deeper AI help + knowledge context"
            : "Basic mode · quick answers from the knowledge base";
    });
}

function setChatMode(mode) {
    currentChatMode = mode === "advanced" ? "advanced" : "basic";
    localStorage.setItem("chatMode", currentChatMode);
    updateModeUI();
    const messages = document.getElementById("chatMessages");
    if (messages) {
        const notice = document.createElement("div");
        notice.className = "bot-message mode-message";
        notice.innerHTML = currentChatMode === "advanced"
            ? "<strong>Advanced Mode selected.</strong><br>Deep AI explanations, numericals, code debugging and troubleshooting are available."
            : "<strong>Basic Mode selected.</strong><br>I’ll use the built-in knowledge base for concise answers.";
        messages.appendChild(notice);
        messages.scrollTop = messages.scrollHeight;
        saveChatHistory();
    }
}

function openChat() {
    const chat = document.getElementById("chatSection");
    const launcher = document.getElementById("chatLauncher");
    if (!chat) return;
    localStorage.setItem("chatOpen", "true");
    chat.classList.add("active");
    chat.classList.remove("minimized");
    if (launcher) launcher.style.display = "none";
    setTimeout(() => document.getElementById("chatInput")?.focus(), 100);
}

function closeChat() {
    const chat = document.getElementById("chatSection");
    const launcher = document.getElementById("chatLauncher");
    localStorage.setItem("chatOpen", "false");
    if (chat) chat.classList.remove("active", "minimized", "maximized");
    if (launcher) launcher.style.display = "flex";
}

function minimizeChat() {
    const chat = document.getElementById("chatSection");
    if (chat) { chat.classList.toggle("minimized"); chat.classList.remove("maximized"); }
}

function maximizeChat() {
    const chat = document.getElementById("chatSection");
    if (!chat) return;
    chat.classList.toggle("maximized");
    chat.classList.remove("minimized");
    const button = chat.querySelector('[aria-label="Maximize"], [aria-label="Restore"]');
    if (button) {
        const expanded = chat.classList.contains("maximized");
        button.setAttribute("aria-label", expanded ? "Restore" : "Maximize");
        button.title = expanded ? "Restore size" : "Maximize";
    }
}

function newChat() {
    if (!confirm("Start a new chat? The current conversation will be cleared from the chat window.")) return;
    localStorage.removeItem(getChatStorageKey());
    renderWelcomeMessage();
    const messages = document.getElementById("chatMessages");
    if (messages) messages.scrollTop = messages.scrollHeight;
    document.getElementById("chatInput")?.focus();
}

function clearCurrentChat() {
    if (!confirm("Clear the current chat? This conversation will be removed from saved history.")) return;
    localStorage.removeItem(getChatStorageKey());
    renderWelcomeMessage();
    const messages = document.getElementById("chatMessages");
    if (messages) messages.scrollTop = messages.scrollHeight;
}

function clearAllChatHistory() {
    if (!confirm("Clear all Electronics Assistant chat history from this browser? This cannot be undone.")) return;
    Object.keys(localStorage).filter(key => key.startsWith("electronicsChat")).forEach(key => localStorage.removeItem(key));
    localStorage.removeItem("chatOpen");
    renderWelcomeMessage();
    const messages = document.getElementById("chatMessages");
    if (messages) messages.scrollTop = messages.scrollHeight;
}

// Backward compatibility for older pages/bookmarks that may call the old function.
function clearChatHistory() {
    clearAllChatHistory();
}

function askBuildingBlock(topic, prompt) {
    openChat();
    const input = document.getElementById("chatInput");
    if (!input) return;
    input.value = prompt || `Explain ${topic} in a student-friendly way, including its working, important formulas, types and practical applications.`;
    setTimeout(() => sendMessage(), 120);
}

function askSuggestion(text) {
    const input = document.getElementById("chatInput");
    if (!input) return;
    input.value = text;
    sendMessage();
}

function handleEnter(event) {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

function getPageContext() {
    const title = document.title || "Electronics Assistant";
    const heading = document.querySelector("h1")?.textContent?.trim() || "";
    return `${title}; current topic: ${heading}`;
}

function getRecentHistoryForAdvanced() {
    try {
        const saved = JSON.parse(localStorage.getItem(getChatStorageKey()) || "[]");
        return Array.isArray(saved) ? saved.slice(-8).map(item => ({role: item.role, content: String(item.content || "").replace(/<[^>]*>/g, "").slice(0, 2500)})) : [];
    } catch (_) { return []; }
}

function appendRelatedSuggestions(container, suggestions) {
    if (!Array.isArray(suggestions) || !suggestions.length) return;
    const wrap = document.createElement("div");
    wrap.className = "related-actions";
    suggestions.slice(0, 4).forEach(text => {
        const button = document.createElement("button");
        button.textContent = text;
        button.onclick = () => askSuggestion(text);
        wrap.appendChild(button);
    });
    container.appendChild(wrap);
}

async function sendMessage() {
    const input = document.getElementById("chatInput");
    const messages = document.getElementById("chatMessages");
    if (!input || !messages) return;
    const question = input.value.trim();
    if (!question) return;

    const userMessage = document.createElement("div");
    userMessage.className = "user-message";
    userMessage.textContent = question;
    messages.appendChild(userMessage);
    input.value = "";

    const botMessage = document.createElement("div");
    botMessage.className = "bot-message typing-message";
    botMessage.textContent = "Thinking...";
    messages.appendChild(botMessage);
    messages.scrollTop = messages.scrollHeight;

    try {
        const endpoint = currentChatMode === "advanced" ? "/advanced_chat" : "/get";
        const payload = currentChatMode === "advanced"
            ? {message: question, page_context: getPageContext(), history: getRecentHistoryForAdvanced()}
            : {msg: question};
        const response = await fetch(endpoint, {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(payload)});
        const data = await response.json();
        if (!response.ok) throw new Error(data.answer || "Server error");
        botMessage.classList.remove("typing-message");
        botMessage.innerHTML = data.answer || data.reply || "I couldn't find an answer.";
    } catch (error) {
        console.error("Chat error", error);
        botMessage.classList.remove("typing-message");
        botMessage.textContent = currentChatMode === "advanced"
            ? "Advanced AI could not connect. Please check the server API configuration or switch to Basic Mode."
            : "Sorry, I could not connect to the Basic chatbot.";
    }
    messages.scrollTop = messages.scrollHeight;
    saveChatHistory();
}

document.addEventListener("DOMContentLoaded", () => {
    updateModeUI();
    loadChatHistory();
    if (localStorage.getItem("chatOpen") === "true") openChat();
});
