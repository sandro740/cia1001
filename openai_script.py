from openai import OpenAI
import os
from dotenv import load_dotenv

print("Loading environment variables...")
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("Error: No OPENAI_API_KEY found in .env file")
    exit(1)

print("Setting up OpenAI client...")
client = OpenAI(api_key=api_key)

print("\nWhat would you like to ask the AI? (Type your question and press Enter)")
user_input = input("> ")

try:
    print("\nSending request to OpenAI...")
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_input}
        ]
    )
    print("\nAI Response:")
    print(response.choices[0].message.content)
except Exception as e:
    print(f"An error occurred: {str(e)}")