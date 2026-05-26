document.addEventListener("DOMContentLoaded", function () {
    const bubble = document.getElementById("chatBubble");
    const window_ = document.getElementById("chatWindow");
    const closeBtn = document.getElementById("chatClose");
    const sendBtn = document.getElementById("chatSend");
    const input = document.getElementById("chatInput");
    const messages = document.getElementById("chatMessages");

    if (!bubble || !window_) return;

    bubble.addEventListener("click", () => {
        const isOpen = window_.classList.toggle("chat-window--open");
        bubble.classList.toggle("chat-bubble--open", isOpen);
        if (isOpen) input.focus();
    });

    closeBtn.addEventListener("click", () => {
        window_.classList.remove("chat-window--open");
        bubble.classList.remove("chat-bubble--open");
    });

    function send() {
        const msg = input.value.trim();
        if (!msg) return;

        appendMessage(msg, "user");
        input.value = "";
        input.disabled = true;
        sendBtn.disabled = true;

        const typing = appendTyping();

        fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: msg }),
        })
        .then(res => res.json())
        .then(data => {
            typing.remove();
            const html = typeof marked !== "undefined" ? marked.parse(data.answer) : data.answer;
            appendMessage(html, "bot", true);
        })
        .catch(() => {
            typing.remove();
            appendMessage("Зв'язок перервано... Магія закінчилася.", "bot");
        })
        .finally(() => {
            input.disabled = false;
            sendBtn.disabled = false;
            input.focus();
        });
    }

    sendBtn.addEventListener("click", send);
    input.addEventListener("keypress", (e) => { if (e.key === "Enter") send(); });

    function appendMessage(content, who, raw) {
        const div = document.createElement("div");
        div.className = `chat-msg chat-msg--${who}`;
        const bbl = document.createElement("div");
        bbl.className = "chat-msg__bubble";
        if (raw) bbl.innerHTML = content;
        else bbl.textContent = content;
        div.appendChild(bbl);
        messages.appendChild(div);
        messages.scrollTop = messages.scrollHeight;
        return div;
    }

    function appendTyping() {
        const div = document.createElement("div");
        div.className = "chat-msg chat-msg--bot";
        div.innerHTML = '<div class="chat-msg__bubble chat-msg__typing"><span></span><span></span><span></span></div>';
        messages.appendChild(div);
        messages.scrollTop = messages.scrollHeight;
        return div;
    }
});