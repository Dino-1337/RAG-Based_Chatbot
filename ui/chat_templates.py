# ui/chat_templates.py

css = """
<style>
    :root {
        --base-bg: #1e1e1e;
        --user-gradient-start: #3a3a3a;
        --user-gradient-end: #5a5a5a;
        --bot-gradient-start: #2a2a2a;
        --bot-gradient-end: #4a4a4a;
        --message-bg: #333333;
        --text-color: #f0f0f0;
        --accent-color: #7f8c8d;
        --shadow-color: rgba(0, 0, 0, 0.5);
        --highlight-color: rgba(255, 255, 255, 0.1);
        --neon-glow: #a8ff78;
        --avatar-size: 50px;
    }

    body {
        font-family: 'Roboto', sans-serif;
        background-color: var(--base-bg);
        color: var(--text-color);
        margin: 0;
        height: 100vh;
        display: flex;
        flex-direction: column;
    }

    .chat-container {
        flex: 1 1 auto;
        overflow-y: auto;
        padding: 1rem;
        border-radius: 1rem;
        background: var(--base-bg);
        box-shadow: inset 0 0 10px var(--shadow-color);
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }

    .chat-message {
        padding: 1rem;
        border-radius: 1rem;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        position: relative;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }

    .chat-message.user {
        justify-content: flex-end;
        background: linear-gradient(135deg, var(--user-gradient-start), var(--user-gradient-end));
    }

    .chat-message.bot {
        justify-content: flex-start;
        background: linear-gradient(135deg, var(--bot-gradient-start), var(--bot-gradient-end));
    }

    .chat-message .avatar {
        width: var(--avatar-size);
        height: var(--avatar-size);
        margin: 0 1rem;
    }

    .chat-message .avatar img {
        max-width: 100%;
        border-radius: 50%;
        object-fit: cover;
        border: 2px solid var(--accent-color);
        transition: border-color 0.3s ease;
    }

    .chat-message .message {
        max-width: 70%;
        padding: 1rem;
        color: var(--text-color);
        border-radius: 0.8rem;
        background: var(--message-bg);
        box-shadow: 2px 2px 6px var(--shadow-color), -2px -2px 6px var(--highlight-color);
        white-space: pre-wrap;
        word-wrap: break-word;
    }

    /* Glow hover effect */
    .chat-message:hover {
        box-shadow: 0 4px 15px var(--neon-glow);
    }

    /* Loading indicator */
    .loading {
        font-style: italic;
        color: var(--accent-color);
        animation: blink 1.2s infinite;
    }

    @keyframes blink {
        0% { opacity: 0.2; }
        50% { opacity: 1; }
        100% { opacity: 0.2; }
    }

    /* New styles for fixed input and scrollable chat */
    .chat-input-container {
        flex: 0 0 auto;
        padding: 1rem;
        background: var(--base-bg);
        border-top: 1px solid var(--accent-color);
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .chat-input {
        flex: 1 1 auto;
        padding: 0.75rem 1rem;
        border-radius: 1rem;
        border: none;
        outline: none;
        font-size: 1rem;
        background: var(--user-gradient-start);
        color: var(--text-color);
    }

    .chat-send-button {
        padding: 0.75rem 1.5rem;
        border-radius: 1rem;
        border: none;
        background: var(--accent-color);
        color: var(--base-bg);
        font-weight: bold;
        cursor: pointer;
        transition: background 0.3s ease;
    }

    .chat-send-button:hover {
        background: var(--neon-glow);
    }
</style>
"""

bot_template = """
<div class="chat-message bot">
    <div class="avatar">
        <img src="https://cdn-icons-png.flaticon.com/512/6134/6134346.png">
    </div>
    <div class="message">{{MSG}}</div>
</div>
"""

user_template = """
<div class="chat-message user">
    <div class="message">{{MSG}}</div>
    <div class="avatar">
        <img src="https://png.pngtree.com/png-vector/20190321/ourmid/pngtree-vector-users-icon-png-image_856952.jpg">
    </div>
</div>
"""

loading_template = """
<div class="chat-message bot">
    <div class="avatar">
        <img src="https://cdn-icons-png.flaticon.com/512/6134/6134346.png">
    </div>
    <div class="message loading">Thinking...</div>
</div>
"""
