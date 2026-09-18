import os
import json
from pathlib import Path

class BaseAdaptationEngine:
    """
    Tier 5 Abstract Base: Metacognitive Rule Generator (Continuous Adaptation).
    """
    def __init__(self, project_dir: str):
        self.project_dir = Path(project_dir).resolve()
        self.rules_dir = self.project_dir / ".agents" / "rules"
        os.makedirs(self.rules_dir, exist_ok=True)

    def extract_lesson(self, failed_attempts: list, successful_diff: str, task: str):
        raise NotImplementedError("Subclasses must implement extract_lesson")

    def write_permanent_rule(self, lesson: dict):
        rule_name = f"auto_rule_{hash(lesson['trigger_context']) % 10000}.md"
        rule_path = self.rules_dir / rule_name
        
        markdown_content = f"""# Auto-Generated Adaptation Rule
**Context Trigger:** {lesson['trigger_context']}

## ❌ Anti-Pattern (DO NOT DO THIS)
{lesson['anti_pattern']}

## ✅ Correct Pattern (ENFORCED)
{lesson['correct_pattern']}

**System Enforcement:** {lesson['enforcement']}
"""
        with open(rule_path, "w") as f:
            f.write(markdown_content)
            
        print(f"[{self.__class__.__name__}] Permanent adaptation rule written to {rule_path}")


class LocalAdaptationEngine(BaseAdaptationEngine):
    """
    Legacy behavior: Hardcoded, simulated extraction of rules.
    """
    def extract_lesson(self, failed_attempts: list, successful_diff: str, task: str):
        print(f"[{self.__class__.__name__}] Analyzing trajectory delta to extract core logic flaw...")
        
        # Simulated extraction of a paradigm-shifting lesson
        lesson = {
            "trigger_context": task,
            "anti_pattern": "Directly mutating state without emitting an event.",
            "correct_pattern": "Always decouple state changes via event emitters.",
            "enforcement": "Reject any diff that mutates state variables directly."
        }
        return lesson


class AgenticAdaptationEngine(BaseAdaptationEngine):
    """
    Advanced behavior: Uses a sub-agent to synthesize a rule from failures.
    """
    def extract_lesson(self, failed_attempts: list, successful_diff: str, task: str):
        print(f"[{self.__class__.__name__}] Spinning up diagnostic agent to analyze failures and synthesize rule...")
        # In a real system, we would prompt an LLM here with the `failed_attempts` and `successful_diff`
        # For now, we simulate an advanced synthesized rule.
        lesson = {
            "trigger_context": f"Task: {task}. Multi-agent failure consensus.",
            "anti_pattern": "Agent attempted to brute-force a patch without checking FTS5 architecture.",
            "correct_pattern": "Perform a semantic check via CodebaseArchitect before finalizing the diff.",
            "enforcement": "If modifying core modules, mandate a graph-check before execution."
        }
        return lesson

# Default alias for backward compatibility
AdaptationEngine = LocalAdaptationEngine
