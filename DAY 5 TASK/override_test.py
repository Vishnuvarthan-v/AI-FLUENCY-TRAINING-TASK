"""Part B: show that the program's system prompt overrides the Modelfile's."""
from openai import OpenAI
client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
reply = client.chat.completions.create(
 model="bookstore-assistant",
 messages=[
 {"role": "system", "content": "You are a pirate. Answer in pirate speech."},
 {"role": "user", "content": "What is the price of Atomic Habits?"},
 ],
)
print(reply.choices[0].message.content)