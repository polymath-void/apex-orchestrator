import os
import json
from pathlib import Path

class AdaptationEngine:
    """
    Tier 5: The Metacognitive Rule Generator (Continuous Adaptation).
    If the agent fails repeatedly but eventually succeeds, this engine extracts
    the underlying logical flaw and writes a permanent system rule so the agent
    never makes the same conceptual mistake again.
    """
    def __init__(self, project_dir: str):
        self.project_dir = Path(project_dir).resolve()
        self.rules_dir = self.project_dir / ".agents" / "rules"
        os.makedirs(self.rules_dir, exist_ok=True)

    def extract_lesson(self, failed_attempts: list, successful_diff: str, task: str):
        """
        In a live environment, an LLM parses the delta between the failures
        and the success, extracting a structural rule.
        """
        print("[Adaptation Engine] Analyzing trajectory delta to extract core logic flaw...")
        
        # Simulated extraction of a paradigm-shifting lesson
        lesson = {
            "trigger_context": task,
            "anti_pattern": "Directly mutating state without emitting an event.",
            "correct_pattern": "Always decouple state changes via event emitters.",
            "enforcement": "Reject any diff that mutates state variables directly."
        }
        return lesson

    def write_permanent_rule(self, lesson: dict):
        """
        Writes the lesson as a permanent Markdown rule file injected into the
        agent's global system prompt on next boot.
        """
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
            
        print(f"[Adaptation Engine] Permanent adaptation rule written to {rule_path}")
