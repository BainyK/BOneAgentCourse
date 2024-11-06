from openai import OpenAI

client = OpenAI(base_url="http://localhost:11434/v1", api_key="not-needed")

def send_message(message):    
    completion = client.chat.completions.create(
        model="llama3.2",
        messages=[
            {"role": "system", "content": "Kamu adalah assisten yang sangat membantu."},
            {"role": "user", "content": message},
        ]
    )
    print(completion.choices[0].message.content)

    
if __name__ == "__main__":
    while True:
        user_input = input("Anda: ")
        if user_input.lower() == "exit":
            break
        print("Chatbot: ")
        send_message(user_input)
        
        print("\n---------------\n")