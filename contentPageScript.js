document.addEventListener("DOMContentLoaded", () => {
    const chatLog = document.getElementById("chatLog");
    const chatForm = document.getElementById("chatForm");
    const userInput = document.getElementById("userInput");
    const promptContainer = document.querySelector(".promptContainer");

    let isFirstMessage = true;

    // Function to auto-resize the textarea
    function autoResize() {
        // Reset the height to auto to calculate the scrollHeight
        userInput.style.height = 'auto';
        
        // Set the height to match the scrollHeight but cap it to max-height
        userInput.style.height = Math.min(userInput.scrollHeight, 150) + 'px';
    }

    // Listen for input event to auto-resize
    userInput.addEventListener('input', autoResize);

    // Initial call to set the height correctly
    autoResize();

    chatForm.addEventListener("submit", (event) => {
        event.preventDefault();

        const userMessageText = userInput.value.trim();
        if (userMessageText) {
            // Hide promptContainer on first message
            if (isFirstMessage) {
                promptContainer.style.display = "none";
                chatForm.classList.add("fixed");
                chatLog.style.height = "60vh"; // Expand chat log height
                chatLog.style.padding = "10px";
                chatLog.style.borderColor = "#ccc";
                chatLog.style.overflowY = "auto";
                isFirstMessage = false;
            }

            // Add user message
            const userMessage = document.createElement("div");
            userMessage.classList.add("userMessage");
            userMessage.textContent = userMessageText;
            chatLog.appendChild(userMessage);

            // Add AI response (sample placeholder)
            const aiMessage = document.createElement("div");
            aiMessage.classList.add("aiMessage");
            aiMessage.textContent = "Lorem ipsum dolor sit amet.";
            chatLog.appendChild(aiMessage);

            // Clear input and scroll to bottom
            userInput.value = "";
            autoResize(); // Resize the textarea back to the single line after clearing
            chatLog.scrollTop = chatLog.scrollHeight;
        }
    });
});
