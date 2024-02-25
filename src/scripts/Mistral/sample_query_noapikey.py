from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

api_key = "API_KEY"

def run_mistral(user_message, model="mistral-medium"):
    client = MistralClient(api_key=api_key)
    messages = [
        ChatMessage(role="user", content=user_message)
    ]
    chat_response = client.chat(
        model=model,
        messages=messages
    )
    return (chat_response.choices[0].message.content)

initial_prompt = "Are you familiar with programming in C++?"

print(run_mistral(initial_prompt))