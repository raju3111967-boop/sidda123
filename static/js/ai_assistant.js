/**
 * AI Assistant Chat Logic (Enhanced)
 * सिध्द गौतम सोसायटी AI असिस्टंट
 */

document.addEventListener('DOMContentLoaded', function () {
    const chatTrigger = document.querySelector('.ai-chat-trigger');
    const chatWindow = document.querySelector('.ai-chat-window');
    const chatClose = document.querySelector('.ai-chat-close');
    const chatInput = document.querySelector('#ai-chat-input');
    const chatSend = document.querySelector('.ai-chat-send');
    const chatBody = document.querySelector('.ai-chat-body');
    const topicButtons = document.querySelectorAll('.ai-topic-bar .btn');

    let currentTopic = 'all';

    if (!chatTrigger) return;

    // Topic Selection Logic
    topicButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            topicButtons.forEach(b => {
                b.classList.remove('active', 'btn-primary');
                b.classList.add('btn-outline-secondary');
            });
            btn.classList.add('active', 'btn-primary');
            btn.classList.remove('btn-outline-secondary');
            currentTopic = btn.dataset.topic;

            // Show Topic Confirmation in Chat
            const topics = {
                'all': 'सर्व विषय',
                'rules': 'सोसायटी नियम',
                'maintenance': 'मेंटेनन्स',
                'redevelopment': 'रिडेव्हलपमेंट',
                'legal': 'कायदेशीर'
            };
            addMessage(`तुम्ही आता <strong>"${topics[currentTopic]}"</strong> बद्दल प्रश्न विचारू शकता.`, 'ai', '', 'AI_Info');
        });
    });

    // Toggle Chat Window
    chatTrigger.addEventListener('click', () => {
        const isOpen = chatWindow.style.display === 'flex';
        chatWindow.style.display = isOpen ? 'none' : 'flex';
        if (!isOpen) {
            chatInput.focus();
            scrollToBottom();
            // Hide notification badge if any
            const badge = document.querySelector('#ai-notif');
            if (badge) badge.classList.add('d-none');
        }
    });

    chatClose.addEventListener('click', () => {
        chatWindow.style.display = 'none';
    });

    // Send Message
    const sendMessage = async () => {
        const question = chatInput.value.trim();
        if (!question) return;

        // Add Member Message
        addMessage(question, 'member', new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
        chatInput.value = '';

        // Add Typing Indicator
        const typingId = addTypingIndicator();
        scrollToBottom();

        try {
            const response = await fetch('/api/ai/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    question: question,
                    topic: currentTopic
                })
            });

            const data = await response.json();

            // Remove Typing Indicator
            const indicator = document.getElementById(typingId);
            if (indicator) indicator.remove();

            // Add AI Message
            addMessage(data.answer, 'ai', data.timestamp, data.type);
            scrollToBottom();

        } catch (error) {
            console.error('AI Chat Error:', error);
            const indicator = document.getElementById(typingId);
            if (indicator) indicator.remove();
            addMessage('क्षमस्व, सर्व्हरशी संपर्क होऊ शकला नाही.', 'ai', 'Error');
        }
    };

    chatSend.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

    function addMessage(text, role, time, type = null) {
        const div = document.createElement('div');
        div.className = `message ${role}`;

        let header = '';
        if (type) {
            let typeLabel = '';
            let typeClass = '';
            switch (type) {
                case 'Approved_DB': typeLabel = 'प्रमाणित उत्तर'; typeClass = 'tag-approved'; break;
                case 'Society_Notice':
                case 'Society_DB': typeLabel = 'सोसायटी माहिती'; typeClass = 'tag-notice'; break;
                case 'Sensitive_Alert': typeLabel = 'कायदेशीर सूचना'; typeClass = 'tag-sensitive'; break;
                case 'Not_Found': typeLabel = 'प्रलंबित'; typeClass = 'tag-notfound'; break;
                case 'AI_Info': typeLabel = 'माहिती'; typeClass = 'tag-ai'; break;
            }
            if (typeLabel) {
                header = `<span class="res-tag ${typeClass}">${typeLabel}</span><br>`;
            }
        }

        div.innerHTML = `
            ${header}
            <div class="message-content">${text.replace(/\n/g, '<br>')}</div>
            <span class="message-time">${time}</span>
        `;
        chatBody.appendChild(div);
        scrollToBottom();
    }

    function addTypingIndicator() {
        const id = 'typing-' + Date.now();
        const div = document.createElement('div');
        div.id = id;
        div.className = 'message ai typing-indicator';
        div.innerHTML = '<div class="dot"></div><div class="dot"></div><div class="dot"></div>';
        chatBody.appendChild(div);
        return id;
    }

    function scrollToBottom() {
        chatBody.scrollTop = chatBody.scrollHeight;
    }

    // Auto-Show Helper Tooltip after 5 seconds if chat is open
    setTimeout(() => {
        const helper = document.querySelector('.ai-helper-toast');
        if (helper && chatWindow.style.display === 'flex') {
            helper.style.display = 'block';
        }
    }, 5000);
});
