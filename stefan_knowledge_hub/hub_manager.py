import os
import pickle

HUB_DIR = "stefan_knowledge_hub"
SKILL_DIR = os.path.join(HUB_DIR, "skills")
DB_FILE = os.path.join(HUB_DIR, "database.pkl")

os.makedirs(SKILL_DIR, exist_ok=True)
for sub in ["voice","language","decryption","custom"]:
    os.makedirs(os.path.join(SKILL_DIR, sub), exist_ok=True)

# -------------------------------
# โหลดฐานข้อมูล Knowledge Hub
# -------------------------------
def load_hub_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "rb") as f:
            return pickle.load(f)
    return {}

def save_hub_db(db):
    with open(DB_FILE, "wb") as f:
        pickle.dump(db, f)

# -------------------------------
# บันทึก skill ใหม่
# -------------------------------
def add_skill(category, name, skill_object):
    skill_path = os.path.join(SKILL_DIR, category, f"{name}.pkl")
    with open(skill_path, "wb") as f:
        pickle.dump(skill_object, f)
    db = load_hub_db()
    db[name] = {"category": category, "path": skill_path}
    save_hub_db(db)
    print(f"[สตีเฟน] บันทึก skill '{name}' ใน category '{category}' เรียบร้อยแล้ว")

# -------------------------------
# โหลด skill จาก Knowledge Hub
# -------------------------------
def load_skill(name):
    db = load_hub_db()
    if name in db:
        with open(db[name]["path"], "rb") as f:
            return pickle.load(f)
    return None

# -------------------------------
# ตัวอย่างการใช้งาน
# -------------------------------

# เพิ่ม skill ตัวอย่าง (voice embedding)
example_voice_skill = {"embedding": [0.1,0.2,0.3]}  # placeholder
add_skill("voice", "ผู้พูด_ตัวอย่าง", example_voice_skill)

# โหลด skill กลับ
skill = load_skill("ผู้พูด_ตัวอย่าง")
print(f"[สตีเฟน] โหลด skill: {skill}")
