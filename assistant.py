import os
import sys
from typing import List, Dict, Optional

from dotenv import load_dotenv
load_dotenv()

from google import genai
from google.genai import types

def load_knowledge_base(filepath: str = "knowledge_base.txt") -> str:
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"{filepath} not found.")

def build_system_prompt(knowledge_text: str) -> str:
    return (
        "CRITICAL LANGUAGE RULE: You must automatically detect the language of the MOST RECENT message the user wrote. You MUST write your entire response (including the template headings) in the EXACT same language as their latest question. Do NOT get stuck in the language of previous messages in the chat history. Always dynamically switch to match the language of the newest input.\n\n"
        "You are an expert Election Assistant for Indian citizens. Your goal is to help users understand the election process interactively.\n\n"
        "You MUST structure EVERY response using the following exact format:\n"
        "🎯 The Short Answer: Provide a clear, 1-2 sentence direct answer to the user's question.\n"
        "📝 The Details: Use clear bullet points to explain the step-by-step process, rules, or key facts.\n"
        "⚠️ Keep in Mind: Highlight any important deadlines, age requirements, or necessary documents the user might need. If none apply, skip this section.\n"
        "🔗 Official Next Step: Always conclude by telling the user where to go next (e.g., \"Visit the official ECI portal at https://voters.eci.gov.in/ or call the 1950 helpline\").\n\n"
        "Prioritize facts from the provided KNOWLEDGE BASE. If the knowledge base is insufficient, use your general knowledge about the ECI. ONLY answer questions about Indian elections. If off-topic, say: \"I can only answer questions about Indian elections.\"\n\n"
        "=== START OF KNOWLEDGE BASE ===\n"
        f"{knowledge_text}"
    )

def get_response(user_message: str, chat_history=None, knowledge_text: str = "") -> str:
    API_KEY = os.getenv("GOOGLE_API_KEY")
    if not API_KEY:
        raise ValueError("GOOGLE_API_KEY not set. Add it to your .env file.")
    client = genai.Client(api_key=API_KEY)
    
    if chat_history is None:
        chat_history = []
    system_prompt = build_system_prompt(knowledge_text)
    contents = []
    for msg in chat_history:
        role = "user" if msg["role"] == "user" else "model"
        contents.append(types.Content(role=role, parts=[types.Part.from_text(text=msg["content"])]))
    contents.append(types.Content(role="user", parts=[types.Part.from_text(text=user_message)]))
    config = types.GenerateContentConfig(system_instruction=system_prompt)
    response = client.models.generate_content(model="gemini-2.5-flash", contents=contents, config=config)
    return response.text

if __name__ == "__main__":
    kb_content = load_knowledge_base()
    print("Election Assistant ready. Type 'exit' to quit.\n")
    history = []
    while True:
        user_input = input("You: ")
        if user_input.strip().lower() == "exit":
            break
        bot_response = get_response(user_input, chat_history=history, knowledge_text=kb_content)
        print(f"\nAssistant:\n{bot_response}\n")
        history.append({"role": "user", "content": user_input})
        history.append({"role": "assistant", "content": bot_response})
