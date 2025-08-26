import time
from stephen import get_chatgpt_message, save_message

# ตัวอย่างคำสั่ง workflow อัตโนมัติ
def auto_workflow(command, file_name=None):
    """
    1. สแกนคู่มือ Help
    2. ใช้ scanzaclip + tpsclip ปฏิบัติคำสั่ง
    3. บันทึกผลลัพธ์ลง Knowledge Base
    """
    print(f"เริ่ม workflow: {command}")
    
    # Step 1: ดึงคู่มือจาก Help
    help_text = get_chatgpt_message("pmpt_68add9940bd08190aa74ee6025219b7e00f19b04cb84f6ba", "2")
    print("คู่มือ Help:", help_text[:200], "...")

    # Step 2: ปฏิบัติคำสั่งตามคู่มือ
    if command == "new_file":
        print(f"สร้างไฟล์ใหม่: {file_name}")
        # simulate scanzaclip + tpsclip action
        print("ใช้ scanzaclip scan, กด, copy/paste, scroll ตามคู่มือ")

    elif command == "edit_file":
        print(f"แก้ไขไฟล์: {file_name}")
        print("ใช้ tpsclip scan, scroll, พิมพ์ข้อความตามคู่มือ")

    # Step 3: บันทึกผลลัพธ์ลง Knowledge Base
    save_message("workflow", "auto", f"{command} executed for {file_name}")

    print(f"Workflow {command} เสร็จสมบูรณ์\n")
    time.sleep(1)

# ตัวอย่างรัน workflow
if __name__ == "__main__":
    commands = [("new_file", "example1.txt"), ("edit_file", "example1.txt")]
    for cmd, file in commands:
        auto_workflow(cmd, file)
