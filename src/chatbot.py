import streamlit as st
#from services.api_requests import query_chatbot

def chatbot_page():
    st.title("Invoice Chatbot")

    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "session_id" not in st.session_state:
        st.session_state.session_id = "test"

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    #Input from the user
    user_input = st.chat_input("Enter your question")

    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)

        # Store user input in session state
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.spinner("Generating Response"):
            #Input the post request for the response
            with st.chat_message("assistant"):
                st.markdown("hello")


            st.session_state.messages.append({"role": "assistant", "content": "hello"})
