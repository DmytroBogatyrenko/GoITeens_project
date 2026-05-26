document.addEventListener("DOMContentLoaded", () => {
    const trigger = document.getElementById("oracle-fly-trigger");
    const chatWindow = document.getElementById("oracle-chat-window");
    const closeBtn = document.getElementById("close-oracle");
    const inputField = document.getElementById("oracle-input-field");
    const responseArea = document.getElementById("oracle-response-area");

    trigger.addEventListener("click", () => {
        chatWindow.classList.add("open");
        trigger.classList.add("active");
        inputField.focus();
    });

    closeBtn.addEventListener("click", () => {
        chatWindow.classList.remove("open");
        trigger.classList.remove("active");
    });

    inputField.addEventListener("keypress", async (e) => {
        if (e.key === "Enter" && inputField.value.trim() !== "") {
            const userMessage = inputField.value.trim();
            inputField.value = ""; 
            inputField.disabled = true; 

            responseArea.innerHTML += `
                <div style="margin-top: 15px; color: #fff; text-align: right;">
                    <span style="background: rgba(212, 175, 55, 0.2); padding: 5px 10px; border-radius: 10px;">
                        ${userMessage}
                    </span>
                </div>`;

            const spiritMsgId = "spirit-msg-" + Date.now();
            responseArea.innerHTML += `
                <div style="margin-top: 10px; color: #d4af37; text-align: left;">
                    <strong>Дух:</strong> <span id="${spiritMsgId}">...</span>
                </div>`;
            
            responseArea.scrollTop = responseArea.scrollHeight;
            const spiritSpan = document.getElementById(spiritMsgId);

            try {
                const response = await fetch('/ask_oracle', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: userMessage })
                });

                if (!response.ok) throw new Error('Network response was not ok');

                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                let fullReply = "";
                let buffer = ""; 

                while (true) {
                    const { done, value } = await reader.read();
                    
                    if (value) {
                        buffer += decoder.decode(value, { stream: true });
                    }

                    let lines = buffer.split('\n');

                    buffer = lines.pop();

                    for (const line of lines) {
                        processLine(line);
                    }

                    if (done) {

                        if (buffer.trim()) {
                            processLine(buffer);
                        }
                        break;
                    }
                }

                function processLine(lineText) {
                    const trimmed = lineText.trim();
                    if (!trimmed || !trimmed.startsWith('data: ')) return;

                    try {
                        const jsonStr = trimmed.substring(6);
                        const data = JSON.parse(jsonStr);
                        if (data.chunk) {
                            fullReply += data.chunk;
                            spiritSpan.innerText = fullReply;
                            responseArea.scrollTop = responseArea.scrollHeight;
                        }
                    } catch (e) {
                        console.warn("Неповний JSON шматок, пропускаємо...");
                    }

                }

            } catch (error) {
                console.error("Fetch Помилка:", error);
                spiritSpan.innerHTML = "<span style='color: #ff4d4d;'>Зв'язок із потойбіччям втрачено...</span>";
            } finally {
                inputField.disabled = false;
                inputField.focus();
            }
        }
    });
});