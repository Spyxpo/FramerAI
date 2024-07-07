let chatHistories = JSON.parse(localStorage.getItem('chatHistories')) || [];
let currentChat = JSON.parse(localStorage.getItem('currentChat')) || [];
let aiThinking = false;
let abortController = null;

function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.toggle('open');
    if (sidebar.classList.contains('open')) {
        setTimeout(() => {
            sidebar.style.visibility = 'visible';
        }, 300); 
    } else {
        setTimeout(() => {
            sidebar.style.visibility = 'hidden';
        }, 300); 
    }
}

function newChat() {
    saveCurrentChat();
    document.getElementById('chat-box').innerHTML = '';
    currentChat = [];
    localStorage.setItem('currentChat', JSON.stringify(currentChat)); 
}

function saveCurrentChat() {
    if (currentChat.length > 0) {
        chatHistories.push(currentChat);
        localStorage.setItem('chatHistories', JSON.stringify(chatHistories));
        displayChatHistory();
    }
}

function displayChatHistory() {
    const chatHistoryDiv = document.getElementById('chat-history');
    chatHistoryDiv.innerHTML = '';
    chatHistories.forEach((chat, index) => {
        const historyDiv = document.createElement('div');
        historyDiv.className = 'history-message';
        historyDiv.innerHTML = `
            Chat ${index + 1}
            <div class="dropdown">
                <button class="dropbtn">⋮</button>
                <div class="dropdown-content">
                    <button onclick="deleteChat(${index})">Delete</button>
                </div>
            </div>
        `;
        historyDiv.onclick = () => loadChat(index);
        chatHistoryDiv.appendChild(historyDiv);
    });
}

function loadChat(index) {
    const chatBox = document.getElementById('chat-box');
    chatBox.innerHTML = '';
    const chat = chatHistories[index];
    chat.forEach(message => {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${message.type}`;
        messageDiv.textContent = message.text;
        chatBox.appendChild(messageDiv);
    });
    currentChat = chat;
    localStorage.setItem('currentChat', JSON.stringify(currentChat));

    const historyMessages = document.querySelectorAll('.history-message');
    historyMessages.forEach((msg, i) => {
        if (i === index) {
            msg.classList.add('active');
        } else {
            msg.classList.remove('active');
        }
    });
}

function deleteChat(index) {
    chatHistories.splice(index, 1);
    localStorage.setItem('chatHistories', JSON.stringify(chatHistories));
    displayChatHistory();
}

async function sendMessage() {
    const userInput = document.getElementById('user-input').value.trim();
    if (userInput === '') {
        alert('Please enter a valid message.');
        return;
    }
    document.getElementById('user-input').value = '';

    const chatBox = document.getElementById('chat-box');
    const userMessage = document.createElement('div');
    userMessage.className = 'message user-message';
    userMessage.textContent = userInput;
    chatBox.appendChild(userMessage);

    currentChat.push({ type: 'user-message', text: userInput });
    localStorage.setItem('currentChat', JSON.stringify(currentChat));

    document.getElementById('user-input').disabled = true;
    const thinkingMessage = document.createElement('div');
    thinkingMessage.className = 'message thinking shimmer';
    thinkingMessage.id = 'thinking';
    chatBox.appendChild(thinkingMessage);
    chatBox.scrollTop = chatBox.scrollHeight;

    const actionButton = document.getElementById('action-button');
    actionButton.innerHTML = '<i class="fa-solid fa-square"></i>';
    actionButton.onclick = stopAI;

    abortController = new AbortController();
    aiThinking = true;

    try {
        const response = await fetch('/message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: userInput }),
            signal: abortController.signal
        });

        const data = await response.json();

        document.getElementById('thinking').remove();
        document.getElementById('user-input').disabled = false;
        document.getElementById('user-input').focus();

        actionButton.innerHTML = '<i class="fa-solid fa-arrow-up"></i>';
        actionButton.onclick = sendMessage;

        const aiMessage = document.createElement('div');
        aiMessage.className = 'message ai-message';
        aiMessage.innerHTML = data.response;
        chatBox.appendChild(aiMessage);

        currentChat.push({ type: 'ai-message', text: data.response });
        localStorage.setItem('currentChat', JSON.stringify(currentChat));

        chatBox.scrollTop = chatBox.scrollHeight;
        aiThinking = false;
    } catch (error) {
        if (error.name === 'AbortError') {
            console.log('AI thinking stopped by user.');
            document.getElementById('thinking').remove();
            document.getElementById('user-input').disabled = false;
            document.getElementById('user-input').focus();

            actionButton.innerHTML = '<i class="fa-solid fa-arrow-up"></i>';
            actionButton.onclick = sendMessage;

            aiThinking = false;
        } else {
            console.error('An error occurred:', error);
        }
    }
}

async function stopAI() {
    if (aiThinking && abortController) {
        abortController.abort();
    }

    try {
        await fetch('/stop', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        console.log('AI process stopped.');
    } catch (error) {
        console.error('Failed to stop AI process:', error);
    }
}

displayChatHistory();