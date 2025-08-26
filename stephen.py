import sqlite3, time, os, smtplib, requests
from datetime import datetime
from email.mime.text import MIMEText
from openai import OpenAI

# --------------------------
DB_PROMPT = "chatgpt_data.db"
DB_KNOWLEDGE = "gpt_knowledge.db"
PROMPT_FILE = "prompts.txt"
NEW_PROMPT_FILE = "new_prompts.txt"
KNOWLEDGE_FILE = "new_knowledge.txt"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
EMAIL_TO = os.getenv("ALERT_EMAIL")
EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_PASS = os.getenv("EMAIL_PASS")
MAX_RETRIES = 3

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

def save_knowledge(knowledge):
    timestamp = datetime.utcnow()
    with sqlite3.connect(DB_KNOWLEDGE) as conn:
        c = conn.cursor()
        c.execute('INSERT INTO gpt_knowledge (knowledge, timestamp) VALUES (?, ?)',
                  (knowledge, timestamp))
        conn.commit()
    print(f"Knowledge saved: {knowledge[:50]}... at {timestamp}")

# --------------------------
def load_prompt_ids():
    if not os.path.exists(PROMPT_FILE): return []
    with open(PROMPT_FILE, "r") as f:
        return [line.strip() for line in f if line.strip()]

def add_new_prompts():
    if not os.path.exists(NEW_PROMPT_FILE): return []
    new_prompts=[]
    for line in open(NEW_PROMPT_FILE):
        pid=line.strip()
        if pid and pid not in load_prompt_ids():
            new_prompts.append(pid)
    if new_prompts:
        with open(PROMPT_FILE, "a") as f:
            for pid in new_prompts: f.write(pid+"\n")
        print(f"Added new prompts: {new_prompts}")
        open(NEW_PROMPT_FILE,"w").close()
    return new_prompts

def add_new_knowledge():
    if not os.path.exists(KNOWLEDGE_FILE): return []
    new_knowledge=[]
    for line in open(KNOWLEDGE_FILE):
        content=line.strip()
        if content:
            new_knowledge.append(content)
            save_knowledge(content)
    if new_knowledge:
        alert_msg=f"New knowledge added: {new_knowledge}"
        send_discord_alert(alert_msg)
        send_email_alert("New Knowledge Added", alert_msg)
        open(KNOWLEDGE_FILE,"w").close()
    return new_knowledge

# --------------------------
def get_latest_version(prompt_id):
    return "2"

def get_chatgpt_message(prompt_id, version):
    for attempt in range(1, MAX_RETRIES+1):
        try:
            client=OpenAI(api_key=OPENAI_API_KEY)
            response=client.responses.create(prompt={"id":prompt_id,"version":version})
            return response.output_text.strip()
        except Exception as e:
            if "invalid_state" in str(e):
                print(f"Attempt {attempt}: invalid_state, retrying...")
                time.sleep(2)
            else: raise
    print(f"Failed to get message for {prompt_id} v{version} after {MAX_RETRIES} retries")
    return None

# --------------------------
def send_discord_alert(message):
    if not DISCORD_WEBHOOK: return
    requests.post(DISCORD_WEBHOOK, json={"content": message})

def send_email_alert(subject, body):
    if not EMAIL_TO or not EMAIL_FROM or not EMAIL_PASS: return
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_FROM
    msg['To'] = EMAIL_TO
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com',465) as server:
            server.login(EMAIL_FROM,EMAIL_PASS)
            server.sendmail(EMAIL_FROM,[EMAIL_TO],msg.as_string())
        print("Email alert sent.")
    except Exception as e:
        print(f"Failed to send email: {e}")

# --------------------------
def main():
    init_db()
    print("เริ่มระบบสตีเฟนครบวงจรพร้อมสอนอัตโนมัติ...")
    try:
        while True:
            add_new_prompts()
            add_new_knowledge()
            for pid in load_prompt_ids():
                version=get_latest_version(pid)
                msg=get_chatgpt_message(pid,version)
                if msg: save_message(pid,version,msg)
            time.sleep(60)
    except KeyboardInterrupt:
        print("หยุดการทำงานแล้ว")

if __name__=="__main__":
    main()
