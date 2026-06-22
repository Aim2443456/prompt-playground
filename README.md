# Converse Lab — AI Prompt Playground

A full-featured AI prompt playground built during my AI Engineering Internship at MTN Nigeria. This tool lets users experiment with AI models — testing system prompts, comparing outputs across temperatures, and chatting with full conversation memory.

🔗 **Live App:** [converse-lab.streamlit.app](https://converse-lab.streamlit.app)

## Features

- **Ask AI** — Send a question with a custom system prompt and temperature setting
- **Temperature Sweep** — Compare the same prompt's output across temperatures 0.0, 0.5 and 1.0
- **Chat Mode** — Full conversational memory; the AI remembers everything said in the session
- **Past Runs** — All interactions are saved to a SQLite database and viewable in the app
- **Multi-Model Support** — Switch between Llama 3.3, Llama 3.1, Llama 4 Scout, Qwen 3 and more via Groq

## Tech Stack

- **Python**
- **Groq API** (Llama models)
- **SQLite** for persistence
- **Streamlit** for the web interface

## What I Learned

- How AI SDKs work under the hood and how API calls are structured
- Token accounting and why it matters for cost management
- How system prompts and temperature shape AI behaviour
- Building conversational memory using message history
- Storing and retrieving structured data with SQLite
- Deploying a Python web app to the cloud with Streamlit

## Run Locally

```bash
git clone https://github.com/Aim2443456/prompt-playground.git
cd prompt-playground
pip install -r requirements.txt
streamlit run app.py
```

You'll need a free [Groq API key](https://console.groq.com) added to a `.env` file:

---

Built by **Muhammed Adetunji Ibraheem** — Electrical and Electronics Engineering student at FUT Minna, AI Engineering Intern at MTN Nigeria.

[GitHub](https://github.com/Aim2443456) | 
[LinkedIn](https://www.linkedin.com/in/muhammed-ibraheem-ab340a239)