let chatHistories = JSON.parse(localStorage.getItem('chatHistories')) || [];
let currentChat = JSON.parse(localStorage.getItem('currentChat')) || [];

function toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('collapsed');
}

function newChat() {
    saveCurrentChat();
    document.getElementById('chat-box').innerHTML = '';
    currentChat = [];
    saveCurrentChat(); 
}

function saveCurrentChat() {
    if (currentChat.length > 0) {
        chatHistories.push(currentChat);
        localStorage.setItem('chatHistories', JSON.stringify(chatHistories));
        localStorage.setItem('currentChat', JSON.stringify(currentChat));
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
    const userInput = document.getElementById('user-input').value;
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

    const response = await fetch('/message', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message: userInput })
    });

    const data = await response.json();

    
    document.getElementById('thinking').remove();
    document.getElementById('user-input').disabled = false;
    document.getElementById('user-input').focus();

    
    const aiMessage = document.createElement('div');
    aiMessage.className = 'message ai-message';
    aiMessage.innerHTML = data.response;
    chatBox.appendChild(aiMessage);

    
    currentChat.push({ type: 'ai-message', text: data.response });
    localStorage.setItem('currentChat', JSON.stringify(currentChat));

    
    chatBox.scrollTop = chatBox.scrollHeight;
}


displayChatHistory();