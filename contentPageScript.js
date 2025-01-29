/*  
    ContentPageScript.js handles the interactive chat functionality for BookQuest.  
    It manages user input, adjusts UI elements dynamically, and communicates with the backend to fetch book recommendations.  
*/

document.addEventListener("DOMContentLoaded", () => {
    const chatLog = document.getElementById("chatLog");
    const chatForm = document.getElementById("chatForm");
    const userInput = document.getElementById("userInput");
    const promptContainer = document.querySelector(".promptContainer");

    let isFirstMessage = true;

    function autoResize() {
        /* Automatically resizes the input field based on content length */
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
                /* On first user message, adjust chat UI for conversation mode */
                promptContainer.style.display = "none";
                chatForm.classList.add("fixed");
                chatLog.style.height = "60vh";
                chatLog.style.padding = "10px";
                chatLog.style.borderColor = "#ccc";
                chatLog.style.overflowY = "auto";
                isFirstMessage = false;
            }

            /* Display user's message in the chat log */
            const userMessage = document.createElement("div");
            userMessage.classList.add("userMessage");
            userMessage.textContent = userMessageText;
            chatLog.appendChild(userMessage);

            /* Display AI's initial response before fetching results */
            const aiMessage = document.createElement("div");
            aiMessage.classList.add("aiMessage");
            aiMessage.textContent = "Searching for books...";
            chatLog.appendChild(aiMessage);

            userInput.value = "";
            autoResize();
            chatLog.scrollTop = chatLog.scrollHeight;

            /* Send user input to backend and process response */
            fetch('http://127.0.0.1:5000/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: userMessageText })
            })
            .then(response => response.json())
            .then(data => {
                console.log("Response data:", data);
                
                /* Display AI-generated response from the backend */
                const aiMessage = document.createElement("div");
                aiMessage.classList.add("aiMessage");
                aiMessage.innerHTML = data.message; // Use innerHTML to render HTML content
                chatLog.appendChild(aiMessage);
                chatLog.scrollTop = chatLog.scrollHeight; // Scroll to the bottom
            })
            .catch(error => {
                /* Log any errors that occur during the fetch request */
                console.error('Error:', error);
            });
        }
    });
});
