document.addEventListener("DOMContentLoaded", () => {
    const sendBtn = document.getElementById("send-btn");
    const inputField = document.getElementById("user-input");
    const chatBox = document.getElementById("chat-box");

    function appendMessage(sender, message) {
        const msg = document.createElement("p");
        msg.innerHTML = `<strong>${sender}:</strong> ${message}`;
        chatBox.appendChild(msg);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    async function sendMessage() {
        const userMessage = inputField.value.trim();
        if (!userMessage) return;

        appendMessage("You", userMessage);
        inputField.value = "";

        try {
            const response = await fetch("/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: userMessage })
            });

            const data = await response.json();
            appendMessage("AI", data.reply);
        } catch (error) {
            appendMessage("Error", "Failed to connect to server.");
        }
    }

    sendBtn.addEventListener("click", sendMessage);

    inputField.addEventListener("keypress", function (event) {
        if (event.key === "Enter") {
            sendMessage();
        }
    });
});
