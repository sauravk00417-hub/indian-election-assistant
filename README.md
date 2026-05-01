# Indian Election Assistant

## 🎯 1. Chosen Vertical
Our project fits into the vertical of **"AI for Citizen Services - Election Assistance"**. We built this persona to bridge the gap between complex official regulations and the everyday citizen, providing verified, simple, and multilingual access to Indian election rules.

## 🧠 2. Approach and Logic
We developed a hybrid approach for this assistant, prioritizing speed, accuracy, and efficient use of the API. Our logic has two core layers:

### Layer 1: The "Offline Brain" (LOCAL\_CACHE)
For the most common, fundamental questions (represented by our 6 preset buttons), we built a local dictionary. When a user clicks one of these buttons, the app immediately fetches the answer from this cache. This approach has three key benefits:
*   **Zero Cost:** It uses no API quota, preserving resources for custom queries.
*   **Instant Response:** There is no "Thinking..." spinner for these questions.
*   **Flawless Formatting:** We pre-formatted these answers with bolding, bullet points, and the required structure for perfect accuracy and presentation.

### Layer 2: The "Online Brain" (Gemini Pro AI)
For any question that is not in the cache—including questions in Hindi, Marathi, or any regional language—the app dynamically routes the query to the Gemini Pro 2.5 Flash model. We engineered the interaction to be robust:
*   **Knowledge-Base Prioritization:** We created a verified `knowledge_base.txt` containing rules from the ECI. The system prompt instructs Gemini to prioritize information from this file to eliminate "AI hallucinations".
*   **Dynamic Language Detection:** The AI is instructed to automatically detect the language of the *most recent* user message and respond in that *exact same language*, allowing for a seamless, natural, multilingual chat experience.
*   **Structured Output:** We enforce a strict strict response template:
    *   🎯 **The Short Answer:** A 1-2 sentence direct response.
    *   📝 **The Details:** Bullet points with clear processes or rules.
    *   ⚠️ **Keep in Mind:** Key deadlines or requirements.
    *   🔗 **Official Next Step:** Direct links to official ECI portals.

## 🛠️ 3. How the Solution Works
The application has three main components working together:

### Frontend (Streamlit)
Built with **`streamlit`**, `app.py` manages the user interface. It contains custom CSS for sleek card-style buttons and welcome cards. It handles user input through a custom chat box and column-based preset buttons, manages `session_state` for chat history, and displays the final structured answers.

### Backend (Python & Gemini Pro)
Contained in `assistant.py`, this layer holds the central logic. It uses **`google-genai`** to communicate with Gemini and **`python-dotenv`** to securely manage the API key. It also includes the full strict persona and response-structuring logic.

### Verified Knowledge Base
The **`knowledge_base.txt`** file is our trusted data source. It includes clear sections on voter registration, Voter ID procedures, polling day steps, general election timelines, key bodies (like BLOs and EROs), the Model Code of Conduct, and EVM/VVPAT security.

### Smart Error Handling & Robustness
We anticipated challenges and built the following robustness features:
*   **Automated Retries:** We use the **`tenacity`** library with exponential backoff on our main `get_response` call. If Google's API is temporarily unavailable, the app quietly retries 5 times before failing.
*   **Rate Limit Management:** Our `app.py` explicitly catches rate-limit errors (429 Resource Exhausted) and displays a polite, human-readable **"System Busy"** yellow warning, instructing the user to wait a specific cooldown period. This prevents the app from crashing and improves user experience.

## 📝 4. Assumptions Made
1.  **Persona Consistency:** The system prompt forces the AI to have a strict persona as an **"Expert Election Assistant"**. It assumes it should *only* answer questions about Indian elections. If a user asks an off-topic question, the assistant is pre-set to politely decline and guide them back to election topics.
2.  **Quota Constraints:** We assumed the app would be running on the free-tier API, which has a strict limit of 15 Requests Per Minute. We built the offline cache and the rate-limit warning system specifically to manage this assumption.
3.  **User Language Fluency:** We assumed users may be highly fluent in regional languages but less so in English, so we gave the AI a clear, unyielding command to always match the user's latest detected language, including all response headers.
