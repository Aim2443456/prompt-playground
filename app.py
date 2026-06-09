import os
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq
import streamlit as st

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def init_database():
    conn = sqlite3.connect("playground_runs.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            model TEXT,
            system_prompt TEXT,
            user_prompt TEXT,
            temperature REAL,
            response TEXT,
            input_tokens INTEGER,
            output_tokens INTEGER,
            total_tokens INTEGER
        )
    """)
    conn.commit()
    conn.close()

def save_run(model, system_prompt, user_prompt, temperature, response, usage):
    conn = sqlite3.connect("playground_runs.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO runs
        (timestamp, model, system_prompt, user_prompt, temperature, response, input_tokens, output_tokens, total_tokens)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().isoformat(),
        model,
        system_prompt,
        user_prompt,
        temperature,
        response,
        usage.prompt_tokens,
        usage.completion_tokens,
        usage.prompt_tokens + usage.completion_tokens
    ))
    conn.commit()
    conn.close()

def get_past_runs(limit=10):
    conn = sqlite3.connect("playground_runs.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM runs ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def ask_ai(user_message, system_prompt, temperature, model):
    response = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
    )
    reply = response.choices[0].message.content
    return reply, response.usage

def main():
    init_database()

    st.set_page_config(
        page_title="Prompt Playground",
        page_icon="🤖",
        layout="wide"
    )

    st.title("Prompt Playground - MTN AI Internship")
    st.markdown("Test AI models with different prompts and temperatures.")
    st.divider()

    st.sidebar.title("Settings")

    model = st.sidebar.selectbox(
        "Choose Model",
        [
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "meta-llama/llama-4-scout-17b-16e-instruct",
            "qwen/qwen3-32b"
        ]
    )

    temperature = st.sidebar.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1,
        help="Higher = more creative. Lower = more focused."
    )

    st.sidebar.divider()
    st.sidebar.markdown("### Temperature Guide")
    st.sidebar.markdown("0.0 - 0.3 = Facts, code, data")
    st.sidebar.markdown("0.4 - 0.6 = General chat")
    st.sidebar.markdown("0.7 - 1.0 = Creative writing")

    tab1, tab2, tab3, tab4 = st.tabs(["Ask AI", "Temperature Sweep", "Past Runs", "Chat Mode"])

    with tab1:
        st.subheader("Ask AI a Question")

        system_prompt = st.text_area(
            "System Prompt",
            value="You are a helpful assistant.",
            height=100,
            help="Instructions that shape how the AI behaves."
        )

        user_message = st.text_area(
            "Your Message",
            placeholder="Type your question here...",
            height=150
        )

        if st.button("Send", type="primary"):
            if not user_message.strip():
                st.warning("Please enter a message.")
            else:
                with st.spinner("Thinking..."):
                    reply, usage = ask_ai(user_message, system_prompt, temperature, model)
                    save_run(model, system_prompt, user_message, temperature, reply, usage)

                st.success("Response received!")
                st.markdown("### AI Response:")
                st.markdown(reply)

                col1, col2, col3 = st.columns(3)
                col1.metric("Input Tokens", usage.prompt_tokens)
                col2.metric("Output Tokens", usage.completion_tokens)
                col3.metric("Total Tokens", usage.prompt_tokens + usage.completion_tokens)

    with tab2:
        st.subheader("Temperature Sweep")
        st.markdown("Ask the same question at temperatures 0.0, 0.5 and 1.0 and compare results.")

        sweep_system = st.text_area(
            "System Prompt",
            value="You are a helpful assistant.",
            height=100,
            key="sweep_system"
        )

        sweep_message = st.text_area(
            "Your Message",
            placeholder="Type your question here...",
            height=150,
            key="sweep_message"
        )

        if st.button("Run Temperature Sweep", type="primary"):
            if not sweep_message.strip():
                st.warning("Please enter a message.")
            else:
                temperatures = [0.0, 0.5, 1.0]
                cols = st.columns(3)

                for i, temp in enumerate(temperatures):
                    with cols[i]:
                        st.markdown(f"### Temperature {temp}")
                        with st.spinner(f"Getting response at {temp}..."):
                            reply, usage = ask_ai(sweep_message, sweep_system, temp, model)
                            save_run(model, sweep_system, sweep_message, temp, reply, usage)
                        st.markdown(reply)
                        st.caption(f"Tokens: {usage.prompt_tokens + usage.completion_tokens}")

    with tab3:
        st.subheader("Past Runs")
        st.markdown("All your previous AI conversations saved from this session.")

        limit = st.slider("Number of runs to show", 5, 50, 10)

        if st.button("Refresh"):
            st.rerun()

        rows = get_past_runs(limit)

        if not rows:
            st.info("No runs saved yet. Ask AI a question first!")
        else:
            st.markdown(f"Showing last **{len(rows)}** runs:")

            for row in rows:
                with st.expander(f"Run #{row[0]} | {row[1][:19]} | Temp: {row[5]} | Tokens: {row[9]}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Model:**")
                        st.code(row[2])
                        st.markdown("**System Prompt:**")
                        st.markdown(row[3])
                        st.markdown("**User Message:**")
                        st.markdown(row[4])
                    with col2:
                        st.markdown("**AI Response:**")
                        st.markdown(row[6])
                        st.metric("Total Tokens", row[9])

    with tab4:
        st.subheader("Chat Mode")
        st.markdown("AI remembers the full conversation history within this session.")

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        if "messages" not in st.session_state:
            st.session_state.messages = []

        chat_system = st.text_area(
            "System Prompt",
            value="You are a helpful assistant.",
            height=100,
            key="chat_system"
        )

        if st.button("Clear Conversation"):
            st.session_state.chat_history = []
            st.session_state.messages = []
            st.rerun()

        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Type your message here..."):
            st.session_state.chat_history.append(
                {"role": "user", "content": prompt}
            )

            if not st.session_state.messages:
                st.session_state.messages = [
                    {"role": "system", "content": chat_system}
                ]

            st.session_state.messages.append(
                {"role": "user", "content": prompt}
            )

            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = client.chat.completions.create(
                        model=model,
                        temperature=temperature,
                        messages=st.session_state.messages
                    )
                    reply = response.choices[0].message.content
                    tokens = response.usage.prompt_tokens + response.usage.completion_tokens

                st.markdown(reply)
                st.caption(f"Tokens used: {tokens} | Messages in history: {len(st.session_state.messages)}")

            st.session_state.chat_history.append(
                {"role": "assistant", "content": reply}
            )
            st.session_state.messages.append(
                {"role": "assistant", "content": reply}
            )                    

if __name__ == "__main__":
    main()