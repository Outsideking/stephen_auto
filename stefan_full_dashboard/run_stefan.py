from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import threading
import pickle, os, time
from core.core_rule_engine import CoreRuleEngine
from hub.hub_manager import KnowledgeHub

app = Flask(__name__)
CORS(app)

# -------------------------------
# Load Knowledge Hub & Core Rule Engine
# -------------------------------
hub = KnowledgeHub()
core = CoreRuleEngine(master_name="Thanva Phupingbut")

# -------------------------------
# รับคำสั่ง #สตีเฟน ผ่าน API
# -------------------------------
@app.route("/api/stefan_command", methods=["POST"])
def stefan_command():
    data = request.json
    command_type = data.get("command_type")
    params = data.get("params")

    response = {"status":"unknown"}
    
    # ตัวอย่าง: บันทึก skill voice
    if command_type == "add_voice_skill":
        name = params["name"]
        embedding = params["embedding"]
        hub.add_skill("voice", name, embedding)
        response["status"] = "voice skill added"
    
    # ตัวอย่าง: Evaluate action ผ่าน Core Rule Engine
    elif command_type == "evaluate_action":
        result = core.evaluate_action(
            actor=params.get("actor"),
            action_type=params.get("action_type"),
            target=params.get("target"),
            context=params.get("context")
        )
        response["status"] = "evaluated"
        response["result"] = result

    return jsonify(response)

# -------------------------------
# API สำหรับ dashboard
# -------------------------------
@app.route("/api/skills")
def get_skills():
    return jsonify(hub.list_skills())

@app.route("/api/logs")
def get_logs():
    return jsonify(core.decision_log)

# -------------------------------
# หน้า Dashboard
# -------------------------------
dashboard_html = open("dashboard/dashboard.html").read()
@app.route("/")
def dashboard():
    return render_template_string(dashboard_html)

# -------------------------------
# Run Flask App 24 ชั่วโมง
# -------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
