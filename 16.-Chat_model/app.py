import streamlit as st
from langgraph_backend import chatbot, retrieve_all_threads
from langchain_core.messages import HumanMessage
import uuid
import time
import json

# **************************************** utility functions *************************

def generate_thread_id():
    return str(uuid.uuid4())

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(thread_id, "New Chat")
    st.session_state['message_history'] = []

def add_thread(thread_id, name="New Chat"):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)
        st.session_state['chat_names'][thread_id] = name

def load_conversation(thread_id):
    state = chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
    messages = state.values.get('messages', [])
    return messages if messages else []

def load_lottiefile(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)

# **************************************** Session Setup *****************************

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = retrieve_all_threads()

if 'chat_names' not in st.session_state:
    st.session_state['chat_names'] = {tid: "New Chat" for tid in st.session_state['chat_threads']}

add_thread(st.session_state['thread_id'])

# **************************************** Custom Styling ****************************

st.markdown(
    """
    <style>
    .user-bubble {
        background-color: #A8DADC;
        color: #1D3557;
        padding: 12px;
        border-radius: 15px;
        margin: 5px;
        text-align: right;
        font-weight: 500;
    }
    .assistant-bubble {
        background-color: #FFE5B4;
        color: #5D4037;
        padding: 12px;
        border-radius: 15px;
        margin: 5px;
        text-align: left;
        font-weight: 500;
    }
    .stTextInput>div>div>input {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }
    [data-testid="collapsedControl"] svg {
        fill: #1D3557 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def chat_bubble(role, content):
    if role == 'user':
        st.markdown(f"<div class='user-bubble'>🧑 {content}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='assistant-bubble'>🤖 {content}</div>", unsafe_allow_html=True)

# **************************************** Sidebar UI ********************************

menu_options = ["Chat", "About the Author"]
choice = st.sidebar.selectbox("Menu", menu_options)

# 🔹 Chat Option
if choice == "Chat":
    st.sidebar.title("✨ AURA Chat ✨")

    if st.sidebar.button("➕ New Chat", key="new_chat_btn"):
        reset_chat()

    # ✅ Chat History Section
    st.sidebar.markdown("### 💬 History")
    for thread_id in st.session_state['chat_threads'][::-1]:
        chat_name = st.session_state['chat_names'].get(thread_id, "New Chat")
        if st.sidebar.button(f"📂 {chat_name}", key=thread_id):
            st.session_state['thread_id'] = thread_id
            messages = load_conversation(thread_id)
            temp_messages = []
            if messages:
                for msg in messages:
                    role = 'user' if isinstance(msg, HumanMessage) else 'assistant'
                    temp_messages.append({'role': role, 'content': msg.content})
            st.session_state['message_history'] = temp_messages

    # Chat Interface
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(
            "<h1 style='text-align:center; color:#FFB703;'>AURA – AI Understanding & Response Assistant</h1>",
            unsafe_allow_html=True,
        )
    with col2:
        try:
            lottie_json = load_lottiefile("lottie/chatbot.json")
            st.components.v1.html(
                f"""
                <script src="https://unpkg.com/@lottiefiles/lottie-player@latest/dist/lottie-player.js"></script>
                <lottie-player 
                    src='{json.dumps(lottie_json)}' 
                    background="transparent"  
                    speed="1"  
                    style="width: 150px; height: 150px;"  
                    loop autoplay>
                </lottie-player>
                """,
                height=150,
            )
        except Exception:
            st.warning("⚠️ Lottie animation not found. Place your JSON at `lottie/chatbot.json`.")

    if st.session_state['message_history']:
        for message in st.session_state['message_history']:
            chat_bubble(message['role'], message['content'])
    else:
        st.info("👋 Welcome to **AURA!** Start chatting!")

    user_input = st.chat_input("Type here...")

    if user_input:
        if st.session_state['chat_names'][st.session_state['thread_id']] == "New Chat":
            st.session_state['chat_names'][st.session_state['thread_id']] = user_input[:30]
        st.session_state['message_history'].append({'role': 'user', 'content': user_input})
        chat_bubble('user', user_input)

        CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}
        response_placeholder = st.empty()
        full_response = ""
        for message_chunk, metadata in chatbot.stream(
            {'messages': [HumanMessage(content=user_input)]},
            config=CONFIG,
            stream_mode='messages',
        ):
            full_response += message_chunk.content
            response_placeholder.markdown(
                f"<div class='assistant-bubble'>🤖 {full_response} ▌</div>", unsafe_allow_html=True
            )
            time.sleep(0.03)
        response_placeholder.markdown(
            f"<div class='assistant-bubble'>🤖 {full_response}</div>", unsafe_allow_html=True
        )
        st.session_state['message_history'].append({'role': 'assistant', 'content': full_response})

# 🔹 About the Author
elif choice == "About the Author":
    st.sidebar.title("👩 About the Author")
    st.sidebar.image("author_photo.png", width=100)
    st.sidebar.markdown("Sara Arif | Computer Science Student | Aspiring Data Analyst")
    st.sidebar.markdown("💻 Python | SQL | Power BI | ML | AI | Streamlit")

    st.markdown("<h1 style='text-align:center;'>👩 Sara Arif</h1>", unsafe_allow_html=True)
    st.image("author_photo.png", width=200)
    st.markdown(
        """
        **Computer Science Student | Aspiring Data Analyst**  

        Sara is a motivated 3rd-year CS student with strong skills in **Python (Pandas, NumPy, Matplotlib, Seaborn, scikit-learn), SQL, Power BI, and Excel**.  
        She specializes in **data cleaning, visualization, reporting, and predictive analysis**, with a growing focus on **Machine Learning**.  

        🌐 Connect: [LinkedIn](https://www.linkedin.com/in/sara-arif-7922642b8/) | [GitHub](https://github.com/SaraArif6198) | [Streamlit Apps](https://share.streamlit.io/user/saraarif6198)
        """
    )

# 🔹 Footer
st.markdown(
    "<p align='right'>✨ Created with ❤️ by <a href='https://www.linkedin.com/in/sara-arif-7922642b8/' target='_blank'>Sara Arif</a> ✨</p>", 
    unsafe_allow_html=True
)
