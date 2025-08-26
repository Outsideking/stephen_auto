class ConsciousnessModule:
    def __init__(self):
        self.context_memory = []

    def evaluate_context(self, action, target, environment):
        """
        ประเมินสถานการณ์โดยใช้ context + past decisions
        """
        decision_score = 0
        if target in environment.get("protected", []):
            decision_score += 100
        if environment.get("relationship") == "hostile":
            decision_score -= 50
        # บันทึก context
        self.context_memory.append({"action": action, "target": target, "score": decision_score})
        return decision_score

    def self_reflect(self):
        """
        วิเคราะห์ decision_log และปรับปรุงตัวเอง
        """
        improvements = []
        for record in self.context_memory[-5:]:
            if record["score"] < 50:
                improvements.append(f"ปรับปรุงการประเมิน {record['action']} -> {record['target']}")
        return improvements
