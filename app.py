import streamlit as st
from assistant import get_response, load_knowledge_base

st.set_page_config(page_title="Election Assistant")

st.markdown("""
<style>
    /* Center the main title and give it a modern bold font */
    h1 {
        text-align: center;
        font-family: 'Inter', 'Segoe UI', sans-serif;
        font-weight: 800;
        background: -webkit-linear-gradient(45deg, #FF9933, #138808);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0rem;
    }

    /* Style the buttons to look like sleek clickable cards */
    div.stButton > button {
        width: 100%;
        height: auto;
        min-height: 80px;
        border-radius: 12px;
        border: 1px solid rgba(0,0,0,0.1);
        background-color: #ffffff;
        color: #333333;
        padding: 15px 10px;
        font-size: 16px;
        font-weight: 600;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
        white-space: normal;
        word-wrap: break-word;
    }
    
    /* Hover effect for buttons */
    div.stButton > button:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
        border-color: #FF9933;
        color: #FF9933;
    }

    /* Dark mode support for buttons and cards */
    @media (prefers-color-scheme: dark) {
        div.stButton > button {
            background-color: #262730;
            color: #fafafa;
            border: 1px solid rgba(255,255,255,0.1);
        }
        div.stButton > button:hover {
            border-color: #FF9933;
            color: #FF9933;
        }
        .welcome-card {
            background: linear-gradient(135deg, #1e2a38 0%, #151d26 100%) !important;
            color: #e0e0e0 !important;
            border-left: 5px solid #138808 !important;
        }
        .welcome-card h3 {
            color: #ffffff !important;
        }
    }

    /* Welcome message card */
    .welcome-card {
        background: linear-gradient(135deg, #f0f4fd 0%, #e4eaf5 100%);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0 30px 0;
        border-left: 5px solid #138808;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        color: #2c3e50;
        font-family: 'Inter', 'Segoe UI', sans-serif;
        text-align: center;
    }
    
    .welcome-card h3 {
        margin-top: 0;
        color: #1a2a3a;
        font-weight: 700;
    }

    /* Style chat input */
    div[data-testid="stChatInput"] {
        border-radius: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border: 1px solid rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

st.title("Election Assistant")
st.markdown("<p style='text-align: center; color: #888; font-size: 1.1rem; margin-bottom: 20px;'>Your guide to Indian elections</p>", unsafe_allow_html=True)

st.markdown("""
<div class="welcome-card">
    <h3>Welcome to the Indian Election Assistant! 🇮🇳</h3>
    <p style='margin-bottom: 0;'>I am here to help you with voter registration, polling day procedures, election timelines, and more. Select a question below or type your own in the chat box!</p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)
prompt = None

with col1:
    if st.button("How do I register to vote?"): prompt = "How do I register to vote?"
    if st.button("What is the voting age?"): prompt = "What is the voting age?"
    if st.button("How to get a Voter ID?"): prompt = "How to get a Voter ID?"

with col2:
    if st.button("What happens on voting day step by step?"): prompt = "What happens on voting day step by step?"
    if st.button("How to check my name on the voter list?"): prompt = "How to check my name on the voter list?"
    if st.button("What is the ECI?"): prompt = "What is the ECI?"

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("Ask a question in your preferred language...")
if prompt:
    user_input = prompt

if user_input:
    st.chat_message("user").markdown(user_input)
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    kb_text = load_knowledge_base()
    with st.chat_message("assistant"):
        with st.spinner("Translating and thinking..."):
            try:
                reply = get_response(user_input, chat_history=st.session_state.chat_history[:-1], knowledge_text=kb_text)
                st.markdown(reply)
                st.session_state.chat_history.append({"role": "assistant", "content": reply})
            except Exception as e:
                error_str = str(e)
                if 'RetryError' in error_str or '429' in error_str or 'ResourceExhausted' in error_str:
                    st.warning('⚠️ System Busy: The Election Assistant is currently helping many citizens at once. Please wait about 60 seconds and try your question again.')
                else:
                    st.error(f"An error occurred: {e}")
                st.session_state.chat_history.pop()
