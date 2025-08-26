import sqlite3, time, os, smtplib, requests
from datetime import datetime
from email.mime.text import MIMEText
from openai import OpenAI

# --------------------------
DB_PROMPT = "chatgpt_data.db"
DB_KNOWLEDGE = "gpt_knowledge.db"
PROMPT_ID = "pmpt_68add9940bd08190aa74ee6025219b7e00f19b04cb84f6ba"
PROMPT_VERSION = "2"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
EMAIL_TO = os.getenv("ALERT_EMAIL")
EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_PASS = os.getenv("EMAIL_PASS")
MAX_RETRIES = 3

# --------------------------
def check_stephen_status():
    if not OPENAI_API_KEY:
        print("❌ OPENAI_API_KEY ยังไม่ถูกตั้งค่า")
        return False
    client = OpenAI(api_key=OPENAI_API_KEY)
    try:
        response = client.responses.create(
            prompt={"id": PROMPT_ID, "version": PROMPT_VERSION}
        )
        output = response.output_text.strip()
        if output:
            print("✅ สตีเฟนพร้อมใช้งาน")
            print("ตัวอย่างข้อความ:", output[:200], "...")
            return True
        else:
            print("⚠️ สตีเฟนดึงข้อความได้ แต่เป็นค่าว่าง")
            return False
    except Exception as e:
        print("❌ เกิดข้อผิดพลาด:", e)
        return False

# --------------------------
def init_db():
    for db, table_sql in [(DB_PROMPT, '''
        CREATE TABLE IF NOT EXISTS chatgpt_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt_id TEXT,
            version TEXT,
            message TEXT,
            timestamp DATETIME
        )'''),
        (DB_KNOWLEDGE, '''
        CREATE TABLE IF NOT EXISTS gpt_knowledge (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            knowledge TEXT,
            timestamp DATETIME
        )''')]:
        with sqlite3.connect(db) as conn:
            c = conn.cursor()
            c.execute(table_sql)
            conn.commit()

def save_message(prompt_id, version, msg):
    timestamp = datetime.utcnow()
    with sqlite3.connect(DB_PROMPT) as conn:
        c = conn.cursor()
        c.execute('INSERT INTO chatgpt_messages (prompt_id, version, message, timestamp) VALUES (?, ?, ?, ?)',
                  (prompt_id, version, msg, timestamp))
        conn.commit()
    print(f"Saved ({prompt_id} v{version}): {msg[:50]}... at {timestamp}")

# --------------------------
def get_chatgpt_message(prompt_id, version):
    for attempt in range(1, MAX_RETRIES+1):
        try:
            client = OpenAI(api_key=OPENAI_API_KEY)
            response = client.responses.create(
                prompt={"id": prompt_id, "version": version}
            )
            return response.output_text.strip()
        except Exception as e:
            if "invalid_state" in str(e):
                print(f"Attempt {attempt}: invalid_state, retrying...")
                time.sleep(2)
            else:
                raise
    print(f"Failed to get message for {prompt_id} v{version} after {MAX_RETRIES} retries")
    return None

# --------------------------
def main():
    init_db()
    print("ตรวจสอบสถานะสตีเฟน...")
    if not check_stephen_status():
        print("❌ สตีเฟนไม่พร้อมใช้งาน โปรดตรวจสอบ API Key และ Prompt ID")
        return
    print("เริ่มระบบสตีเฟนอัตโนมัติ...")
    try:
        while True:
            msg = get_chatgpt_message(PROMPT_ID, PROMPT_VERSION)
            if msg:
                save_message(PROMPT_ID, PROMPT_VERSION, msg)
            time.sleep(60)
    except KeyboardInterrupt:
        print("หยุดการทำงานแล้ว")

if __name__ == "__main__":
    main()
