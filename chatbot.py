import streamlit as st
import time
from model import model
from data import load_data

# Set the page configuration
st.set_page_config(page_title="Chatbot", layout="centered")

# Custom CSS for chat bubbles, title, and sync message
st.markdown("""
    <style>
    body {
        background-color: #2a2a2a;
        color: white;
        font-family: 'Roboto', sans-serif;
    }
    .chat-container {
        max-width: 700px;
        margin: auto;
        padding: 20px;
    }
    .user-message, .assistant-message {
        display: inline-block;
        padding: 10px 15px;
        border-radius: 20px;
        margin: 10px 0;
        max-width: 80%;
        word-wrap: break-word;
    }
    .user-message {
        background-color: #4A90E2;
        color: white;
        text-align: right;
        align-self: flex-end;
    }
    .assistant-message {
        background-color: #f1f0f0;
        color: black;
        text-align: left;
        align-self: flex-start;
    }
    .message-container {
        display: flex;
        align-items: center;
        margin-bottom: 10px;
    }
    .message-container.user {
        justify-content: flex-end;
    }
    .message-container.assistant {
        justify-content: flex-start;
    }
    .message-icon {
        width: 40px;
        height: 40px;
        margin: 0 10px;
    }
    .message-icon.user {
        order: 2;
    }
    .message-icon.assistant {
        order: 1;
    }
    .user-message {
        order: 1;
    }
    .assistant-message {
        order: 2;
    }
    .response-time {
        font-size: 0.8em;
        color: #888;
        margin-left: 50px;
    }
    .st-chat-input input {
        background-color: #1f1f1f;
        color: white;
        border-radius: 20px;
        padding: 10px;
        margin-top: 20px;
        width: calc(100% - 20px);
    }
    .st-chat-input input::placeholder {
        color: #888;
    }
    .st-chat-input input:focus {
        border: none;
        outline: none;
    }
    .chatbot-title {
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 20px;
    }
    .chatbot-title h1 {
        color: #4A90E2;
        font-size: 2.5em;
        margin-right: 10px;
    }
    .chatbot-title img {
        width: 40px;
        height: 40px;
    }
    </style>
""", unsafe_allow_html=True)

# Title fixed at the top with new styling
st.markdown("""
    <div class="chatbot-title">
        <h1>AgraBot</h1>
        <img src="https://cdn-icons-png.flaticon.com/512/6134/6134346.png" alt="chatbot-icon">
    </div>
""", unsafe_allow_html=True)

# Sidebar with language selection, separator line, and Sync button
with st.sidebar:
    language = st.selectbox("Select Language", ["English", "Swahili"])
    
    if language == "English":
        data_folder = 'data/data_en'
    else:
        data_folder = 'data/data_sw'
    
    # Add a horizontal line separator with custom color AFTER the language selection
    st.markdown("""<hr style="border:0.5px solid #333333;">""", unsafe_allow_html=True)
    
    if st.button("Sync with Remote Database"):
        with st.spinner("Syncing with remote database..."):
            time.sleep(4)  # Simulate a delay for syncing
        st.success("Sync complete")

# Load data based on selected language
questions, answers = load_data(data_folder)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Function to render messages
def render_messages():
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"""
                <div class="message-container user">
                    <div class="user-message">{message["content"]}</div>
                    <img class="message-icon user" src="https://cdn-icons-png.flaticon.com/256/1011/1011867.png" alt="user-icon">
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class="message-container assistant">
                    <img class="message-icon assistant" src="https://cdn-icons-png.flaticon.com/512/6134/6134346.png" alt="assistant-icon">
                    <div class="assistant-message">{message["content"]}</div>
                </div>
            """, unsafe_allow_html=True)
            if "time_taken" in message:
                st.markdown(f"""
                    <div class="response-time">Response Time: {message["time_taken"]:.2f} seconds</div>
                """, unsafe_allow_html=True)

# Accept user input
prompt = st.chat_input("How can I help you today?")

if prompt:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Re-render messages including the new user message
    render_messages()

    # Call the assistant model
    with st.spinner("Thinking..."):
        start_time = time.time()
        
        results = model.rank(prompt, questions, return_documents=True, top_k=1)
        
        end_time = time.time()
        time_taken = end_time - start_time

        if results:
            corpus_id = results[0]['corpus_id']
            similarity = results[0]['score']  # Assuming the similarity score is returned in the 'score' field

            if similarity < 0.1:
                if data_folder == 'data/data_en':
                    response = "Sorry, this question does not match any of the topics in our database."
                else:
                    response = "Samahani, swali hili halilingani na mada yoyote katika hifadhidata yetu."
            else:
                response = answers[corpus_id]
        
            # Add assistant response to chat history with response time
            st.session_state.messages.append({"role": "assistant", "content": response, "time_taken": time_taken})
        
        # Re-render messages including the new assistant message
        st.rerun()

# Display chat messages from history on app rerun
render_messages()