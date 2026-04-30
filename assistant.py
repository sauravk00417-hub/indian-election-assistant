import os
import sys
from typing import List, Dict, Optional

from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential
load_dotenv()

from google import genai
from google.genai import types

LOCAL_CACHE = {
    "How do I register to vote?": (
        "🎯 The Short Answer: You can register to vote online through the Voter Service Portal or offline by submitting Form 6 to your Electoral Registration Officer (ERO).\n\n"
        "📝 The Details:\n"
        "- **Online:** Go to the official voters portal, sign up/login, and fill out Form 6.\n"
        "- **Offline:** Download Form 6 or get it from your local Booth Level Officer (BLO) / ERO, fill it out, and submit it with required documents.\n"
        "- **Documents Required:** A passport-sized photo, proof of age (e.g., birth certificate, 10th standard mark sheet, Aadhaar), and proof of residence (e.g., Aadhaar, passport, utility bill).\n\n"
        "⚠️ Keep in Mind: You must be an Indian citizen ordinarily residing in the constituency, and be 18 years or older on the qualifying date (January 1, April 1, July 1, or October 1).\n\n"
        "🔗 Official Next Step: Visit the official ECI portal at https://voters.eci.gov.in/ or download the Voter Helpline App to begin."
    ),
    "What is the voting age?": (
        "🎯 The Short Answer: The legal voting age in India is 18 years.\n\n"
        "📝 The Details:\n"
        "- Every Indian citizen who has reached the age of 18 is eligible to vote.\n"
        "- Eligibility is determined on specific qualifying dates each year: January 1, April 1, July 1, and October 1.\n"
        "- If you turn 18 before or on any of these dates, you can apply in advance for voter registration.\n\n"
        "⚠️ Keep in Mind: While 18 is the voting age, mere age does not guarantee your ability to vote; you must also be registered on the electoral roll.\n\n"
        "🔗 Official Next Step: Check your eligibility and apply online at the official ECI portal: https://voters.eci.gov.in/"
    ),
    "How to get a Voter ID?": (
        "🎯 The Short Answer: To get a Voter ID, you must successfully register on the electoral roll by submitting Form 6, after which a physical EPIC card will be sent to your address.\n\n"
        "📝 The Details:\n"
        "- Submit **Form 6** online or offline for new voter registration.\n"
        "- After submission, a Booth Level Officer (BLO) may verify your address.\n"
        "- Once approved, your Electors Photo Identity Card (EPIC) will be sent via Speed Post.\n"
        "- You can also download a digital version called e-EPIC directly from the portal.\n\n"
        "⚠️ Keep in Mind: Make sure your application is approved before expecting the physical card; this process usually takes a few weeks.\n\n"
        "🔗 Official Next Step: Track your application status or download your e-EPIC at https://voters.eci.gov.in/"
    ),
    "What happens on voting day step by step?": (
        "🎯 The Short Answer: On voting day, you authenticate your identity, proceed to the polling booth, and cast your vote on the EVM.\n\n"
        "📝 The Details:\n"
        "- **Step 1:** Enter the polling station and stand in line. The First Polling Officer checks your name on the voter list and your ID.\n"
        "- **Step 2:** The Second Polling Officer marks your left forefinger with indelible ink, gives you a slip, and takes your signature.\n"
        "- **Step 3:** Hand the slip to the Third Polling Officer, who directs you to the voting compartment.\n"
        "- **Step 4:** Press the blue button on the Electronic Voting Machine (EVM) next to your chosen candidate. A red light will glow and a beep sound will confirm your vote.\n"
        "- **Step 5:** Verify your vote via the VVPAT slip that appears in the transparent window for 7 seconds.\n\n"
        "⚠️ Keep in Mind: Mobile phones, cameras, and recording devices are strictly prohibited inside the polling booth.\n\n"
        "🔗 Official Next Step: Find your exact polling booth location using the Voter Helpline App or visit https://voters.eci.gov.in/"
    ),
    "How to check my name on the voter list?": (
        "🎯 The Short Answer: You can verify your name on the electoral roll online via the ECI portal or via SMS.\n\n"
        "📝 The Details:\n"
        "- **Search by EPIC:** Enter your EPIC (Voter ID) number on the portal.\n"
        "- **Search by Details:** Input your name, age, district, and assembly constituency to locate your entry.\n"
        "- **Search by Mobile:** If your mobile is linked to your EPIC, you can use it to fetch your details.\n"
        "- **Offline Check:** Contact your Booth Level Officer (BLO) or visit your local Electoral Registration Office.\n\n"
        "⚠️ Keep in Mind: It is crucial to verify your name on the list before election day; holding a Voter ID card is not enough if your name is missing from the final roll.\n\n"
        "🔗 Official Next Step: Search for your name immediately at https://electoralsearch.eci.gov.in/"
    ),
    "What is the ECI?": (
        "🎯 The Short Answer: The Election Commission of India (ECI) is an independent constitutional body responsible for administering elections in India.\n\n"
        "📝 The Details:\n"
        "- The ECI was established on January 25, 1950 (celebrated as National Voters' Day).\n"
        "- It oversees elections to the Lok Sabha, Rajya Sabha, State Legislative Assemblies, and the offices of the President and Vice President.\n"
        "- The commission is composed of the Chief Election Commissioner and two Election Commissioners.\n"
        "- It enforces the Model Code of Conduct to ensure free and fair elections.\n\n"
        "⚠️ Keep in Mind: The ECI does not conduct elections for local bodies like Panchayats and Municipalities; those are handled by State Election Commissions.\n\n"
        "🔗 Official Next Step: Learn more about the commission by visiting the main site at https://eci.gov.in/"
    )
}

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

@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=2, max=15))
def get_response(user_message: str, chat_history=None, knowledge_text: str = "") -> str:
    clean_msg = user_message.strip()
    if clean_msg in LOCAL_CACHE:
        return LOCAL_CACHE[clean_msg]

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
