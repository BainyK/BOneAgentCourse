from openai import OpenAI
import gradio as gr
import time

client = OpenAI(base_url="http://localhost:11434/v1", api_key="not-needed")

myhistory=[
      {"role": "system", "content": "Kamu adalah assisten yang sangat membantu."},
]

def handle_msg(message, history):
  myhistory.append({"role": "user", "content": message})  
  
  completion = client.chat.completions.create(
      model="llama3.2",
      messages=myhistory,
      stream=True
    )
  
  new_response = {"role": "assistant", "content": ""}
  for chunk in completion:
      if chunk.choices[0].delta.content:
        new_response["content"] += chunk.choices[0].delta.content        
        time.sleep(0.03)
        yield new_response["content"]

  myhistory.append(new_response)



demo = gr.ChatInterface(fn=handle_msg,title="Chatbot")

demo.launch()