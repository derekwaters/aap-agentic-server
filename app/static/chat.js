const form = document.getElementById("chat-form");
const input = document.getElementById("chat-input");
const responseBox = document.getElementById("response");
const finalAnswerBox = document.getElementById("final-answer");
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

    // If the text is valid JSON, we'll assume it's an event
    try {
        check_json = JSON.parse(text);
        // We've got JSON, so let's "pad" the request:

        text = "Find a job template to solve the following error: '" + text + "' If you find a solution, launch the job template with the relevant inventory. If you need an incident number, obtain one with the create_incident tool.";
    } catch (SyntaxError)
    {
        // Don't need to do anything, just use the text as is
    }

    setInputDisabled(true);
    statusText.textContent = "Sending your message...";
    responseBox.textContent = "The assistant's response will stream here...";
    finalAnswerBox.textContent = "Waiting for final answer...";

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
            responseBox.scrollTop = responseBox.scrollHeight;
        }
        if (data.chat_complete) {
            clearInterval(pollInterval);
            pollInterval = null;
            statusText.textContent = "Ready for your next question.";

            if (data.answer) {
                var parsedData = JSON.parse(data.answer);
                finalAnswerBox.textContent = parsedData.answer;
            } else {
                finalAnswerBox.textContent = "No answer received.";
            }
            input.value = "";
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

