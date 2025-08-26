from core.core_rule_engine import CoreRuleEngine
from hub.hub_manager import KnowledgeHub
from consciousness.consciousness import ConsciousnessModule
from scanzaclip_analysis.scanzaclip import ScanzaclipAnalyzer

# -------------------------------
# สร้าง instance
# -------------------------------
core = CoreRuleEngine(master_name="Thanva Phupingbut", heirs=["ทายาทเจ้านาย"])
hub = KnowledgeHub()
conscious = ConsciousnessModule()
scanzaclip = ScanzaclipAnalyzer()

# -------------------------------
# ตัวอย่างการประมวลผล Self-Upgrade
# -------------------------------
clip_example = {"steps": ["ingest", "process", "analyze"]}
analysis_result = scanzaclip.analyze_clip(clip_example)

# ประเมิน decision ผ่าน consciousness
decision_score = conscious.evaluate_context(action="help", target="ครอบครัวเจ้านาย", environment={"protected":["ครอบครัวเจ้านาย"], "relationship":"friendly"})
improvements = conscious.self_reflect()

print("Analysis Result:", analysis_result)
print("Decision Score:", decision_score)
print("Self-Improvement Suggestions:", improvements)
