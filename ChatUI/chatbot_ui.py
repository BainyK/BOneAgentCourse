from openai import OpenAI
import streamlit as st
import time

client = OpenAI(base_url="http://localhost:11434/v1", api_key="not-needed")

# Tampilkan judul chatbot
st.title("Chatbot")

# buat variable session
if "messages" not in st.session_state:
  st.session_state["messages"] = [
    {"role": "assistant", "content": "Apa yang bisa saya bantu?"},
  ]

# Tammpilkan History chat di box message
for msg in st.session_state.messages:
  st.chat_message(msg["role"]).write(msg["content"])

# Buat input box untuk menunggu chat dari user
if prompt := st.chat_input():
  st.session_state.messages.append({"role": "user", "content": prompt})
  
  with st.chat_message("user"):
    st.markdown(prompt)
  
  with st.chat_message("assistant"):
      message_placeholder = st.empty()
      full_response = ""

      completion = client.chat.completions.create(
        model="llama3.2",
        messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
        stream=True,        
        )
      
      for chunk in completion:
        if chunk.choices[0].delta.content:
          full_response += chunk.choices[0].delta.content                  
          message_placeholder.markdown(full_response + "▌")
          time.sleep(0.03)
      
      message_placeholder.markdown(full_response)
      st.session_state.messages.append({"role": "assistant", "content": full_response})