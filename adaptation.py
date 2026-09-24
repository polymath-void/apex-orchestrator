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
    Advanced behavior: Uses the LLM directly to synthesize a permanent rule from failures.
    """
    def extract_lesson(self, failed_attempts: list, successful_diff: str, task: str):
        print(f"[{self.__class__.__name__}] Spinning up diagnostic engine to analyze failures and synthesize rule...")
        try:
            from llm_client import GeminiClient
            import json
            
            llm = GeminiClient()
            prompt = f"Task: {task}\nFailed Attempts:\n"
            for i, fail in enumerate(failed_attempts):
                prompt += f"Attempt {i}: {fail}\n"
            prompt += f"Successful Diff:\n{successful_diff}\n"
            prompt += "Based on this, what is the core anti-pattern to avoid and the correct pattern to enforce? Respond with ONLY a JSON object having keys: 'anti_pattern', 'correct_pattern', 'enforcement'."
            
            response = llm.generate_content(prompt).strip()
            
            if response.startswith('```json'): response = response[7:]
            if response.startswith('```'): response = response[3:]
            if response.endswith('```'): response = response[:-3]
            
            data = json.loads(response.strip())
            return {
                "trigger_context": f"Task: {task}",
                "anti_pattern": data.get("anti_pattern", "Unknown anti-pattern"),
                "correct_pattern": data.get("correct_pattern", "Unknown correct pattern"),
                "enforcement": data.get("enforcement", "Enforce correct pattern")
            }
        except Exception as e:
            print(f"[{self.__class__.__name__}] Failed to synthesize rule dynamically: {e}")
            return {
                "trigger_context": f"Task: {task}",
                "anti_pattern": "Agent attempted brute-force without checking architecture.",
                "correct_pattern": "Perform a semantic check via CodebaseArchitect.",
                "enforcement": "Mandate graph-check."
            }

class HeuristicAdaptationEngine(AgenticAdaptationEngine):
    """
    Extracts deep AST heuristics to build targeted rules.
    """
    def extract_lesson(self, failed_attempts: list, successful_diff: str, task: str):
        # We can extend this further to parse the actual AST of successful_diff
        # For now, it leverages AgenticAdaptationEngine logic with specific prompt tuning.
        return super().extract_lesson(failed_attempts, successful_diff, task + " (Enforce strict AST safety)")

# Default alias for backward compatibility
AdaptationEngine = HeuristicAdaptationEngine

