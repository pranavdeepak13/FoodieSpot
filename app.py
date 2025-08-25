import streamlit as st
import requests
import uuid
import time

st.set_page_config(
    page_title="FoodieSpot AI",
    page_icon="🍽️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

BACKEND_URL = "http://localhost:8000"

def initialize_session():
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Hello! I'm FoodieSpot AI, your restaurant assistant. I can help you:\n\n• **Book restaurant reservations**\n• **Find restaurant recommendations**\n• **Check restaurant availability**\n\nWhat would you like to do today?"
            }
        ]
    
    if "processing" not in st.session_state:
        st.session_state.processing = False
    
    if "last_message_time" not in st.session_state:
        st.session_state.last_message_time = 0

def send_message_to_backend(message: str):
    try:
        response = requests.post(
            f"{BACKEND_URL}/chat",
            json={
                "message": message,
                "session_id": st.session_state.session_id
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return data["response"]
        else:
            return f"Sorry, I encountered an error (Status: {response.status_code}). Please try again."
            
    except requests.exceptions.Timeout:
        return "Sorry, the request timed out. Please try again."
    except requests.exceptions.ConnectionError:
        return "Sorry, I can't connect to the server. Please make sure the backend is running on port 8000."
    except Exception as e:
        return f"Sorry, an unexpected error occurred: {str(e)}"

def display_message(role: str, content: str):
    if role == "user":
        with st.chat_message("user"):
            st.write(content)
    else:
        with st.chat_message("assistant"):
            st.markdown(content)

def main():
    initialize_session()
    
    st.title("🍽️ FoodieSpot AI")
    st.caption("Your intelligent restaurant assistant")
    
    for message in st.session_state.messages:
        display_message(message["role"], message["content"])
    
    if not st.session_state.processing:
        prompt = st.chat_input("Ask me about restaurants...")
        
        if prompt and prompt.strip():
            current_time = time.time()
            
            if current_time - st.session_state.last_message_time > 1:
                st.session_state.processing = True
                st.session_state.last_message_time = current_time
                
                st.session_state.messages.append({"role": "user", "content": prompt})
                
                with st.chat_message("user"):
                    st.write(prompt)
                
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        response = send_message_to_backend(prompt)
                    st.markdown(response)
                
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.session_state.processing = False
                
                st.rerun()
    else:
        st.chat_input("Processing your message...", disabled=True)

if __name__ == "__main__":
    main()