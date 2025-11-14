const form = document.getElementById("chat-form");
const input = document.getElementById("chat-input");
const responseBox = document.getElementById("response");
const statusText = document.getElementById("status");
const sendBtn = document.getElementById("send-btn");

let pollInterval = null;

const setInputDisabled = (disabled) => {
    input.disabled = disabled;
    sendBtn.disabled = disabled;
};

form?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const text = input.value.trim();
    if (!text) {
        return;
    }

    setInputDisabled(true);
    statusText.textContent = "Sending your message...";
    responseBox.textContent = "";

    try {
        const res = await fetch("/api/send_chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text })
        });

        if (!res.ok) {
            throw new Error("Failed to send message");
        }

        const data = await res.json();
        statusText.textContent = "Waiting for the assistant...";
        input.value = "";
        startPolling(data.session_id);
    } catch (err) {
        console.error(err);
        statusText.textContent = "Something went wrong. Please try again.";
        setInputDisabled(false);
    }
});

const startPolling = (sessionId) => {
    if (pollInterval) {
        clearInterval(pollInterval);
    }
    pollInterval = setInterval(() => pollSession(sessionId), 1000);
};

const pollSession = async (sessionId) => {
    try {
        const res = await fetch("/api/get_chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ session_id: sessionId })
        });

        if (!res.ok) {
            throw new Error("Polling failed");
        }

        const data = await res.json();
        if (data.response) {
            responseBox.textContent = data.response;
        }
        if (data.chat_complete) {
            clearInterval(pollInterval);
            pollInterval = null;
            statusText.textContent = "Ready for your next question.";
            setInputDisabled(false);
        }
    } catch (err) {
        console.error(err);
        clearInterval(pollInterval);
        pollInterval = null;
        statusText.textContent = "Error while receiving response.";
        setInputDisabled(false);
    }
};

