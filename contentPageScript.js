
document.addEventListener("DOMContentLoaded", () => {
    const chatLog = document.getElementById("chatLog");
    const chatForm = document.getElementById("chatForm");
    const userInput = document.getElementById("userInput");
    const promptContainer = document.querySelector(".promptContainer");

    let isFirstMessage = true;

    function autoResize() {
        userInput.style.height = 'auto';
        
        userInput.style.height = Math.min(userInput.scrollHeight, 150) + 'px';
    }

    userInput.addEventListener('input', autoResize);
    autoResize();

    chatForm.addEventListener("submit", (event) => {
        event.preventDefault();

        const userMessageText = userInput.value.trim();
        if (userMessageText) {
            if (isFirstMessage) {
                promptContainer.style.display = "none";
                chatForm.classList.add("fixed");
                chatLog.style.height = "60vh";
                chatLog.style.padding = "10px";
                chatLog.style.borderColor = "#ccc";
                chatLog.style.overflowY = "auto";
                isFirstMessage = false;
            }


            const userMessage = document.createElement("div");
            userMessage.classList.add("userMessage");
            userMessage.textContent = userMessageText;
            chatLog.appendChild(userMessage);

            const aiMessage = document.createElement("div");
            aiMessage.classList.add("aiMessage");
            aiMessage.textContent = "Searching for books...";
            chatLog.appendChild(aiMessage);

            userInput.value = "";
            autoResize();
            chatLog.scrollTop = chatLog.scrollHeight;

            fetch('http://127.0.0.1:5000/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: userMessageText })
            })
            .then(response => response.json()) // Ensure you parse the response to JSON
            .then(data => {
                console.log("Response data:", data); // Debugging output
                const aiMessage = document.createElement("div");
                aiMessage.classList.add("aiMessage");
                aiMessage.innerHTML = data.message; // Use innerHTML to render HTML content correctly
                chatLog.appendChild(aiMessage);
            })
            .catch(error => {
                console.error('Error:', error);
            });
                    }
                });
            });
