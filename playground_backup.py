import os
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq

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

def view_past_runs(limit=5):
    conn = sqlite3.connect("playground_runs.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM runs ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    if not rows:
        print("No runs saved yet.")
        return
    print("\n--- Past Runs ---")
    for row in rows:
        print(f"\nRun #{row[0]} | {row[1]} | Temp: {row[5]} | Tokens: {row[9]}")
        print(f"Prompt: {row[4][:60]}")
        print(f"Response: {row[6][:100]}")

def ask_ai(user_message, system_prompt="You are a helpful assistant.", temperature=0.7):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=temperature,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
    )
    reply = response.choices[0].message.content
    return reply, response.usage

def temperature_sweep(prompt, system_prompt="You are a helpful assistant."):
    print(f"\nPrompt: {prompt}")
    print("=" * 50)
    for temp in [0.0, 0.5, 1.0]:
        reply, usage = ask_ai(prompt, system_prompt, temperature=temp)
        print(f"\nTemperature {temp}:")
        print(reply)
        print(f"Tokens used: {usage.prompt_tokens + usage.completion_tokens}")
        save_run("llama-3.3-70b-versatile", system_prompt, prompt, temp, reply, usage)
        print("-" * 50)

def main():
    init_database()
    print("\n?? Welcome to Prompt Playground CLI")
    print("=====================================")

    while True:
        print("\nWhat would you like to do?")
        print("1. Ask AI a question")
        print("2. Run a temperature sweep")
        print("3. View past runs")
        print("4. Exit")

        choice = input("\nEnter choice (1-4): ").strip()

        if choice == "1":
            system = input("System prompt (press Enter for default): ").strip()
            if not system:
                system = "You are a helpful assistant."
            prompt = input("Your message: ").strip()
            temp = input("Temperature 0.0 to 1.0 (press Enter for 0.7): ").strip()
            temp = float(temp) if temp else 0.7

            print("\n? Thinking...")
            reply, usage = ask_ai(prompt, system, temp)
            print(f"\n?? AI says:\n{reply}")
            print(f"\n?? Tokens used: {usage.prompt_tokens + usage.completion_tokens}")
            save_run("llama-3.3-70b-versatile", system, prompt, temp, reply, usage)
            print("? Run saved!")

        elif choice == "2":
            system = input("System prompt (press Enter for default): ").strip()
            if not system:
                system = "You are a helpful assistant."
            prompt = input("Your message: ").strip()
            temperature_sweep(prompt, system)

        elif choice == "3":
            n = input("How many past runs to show? (press Enter for 5): ").strip()
            n = int(n) if n else 5
            view_past_runs(n)

        elif choice == "4":
            print("\nGoodbye! ??")
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()
