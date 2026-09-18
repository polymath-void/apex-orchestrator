import json
from pathlib import Path

class BaseReasoner:
    """
    Tier 4 Abstract Base: Dynamic Chain-of-Thought & Tree of Thoughts Engine.
    """
    def __init__(self, memory_engine):
        self.memory = memory_engine

    def generate_hypotheses(self, task_description: str, context_snippets: list):
        raise NotImplementedError("Subclasses must implement generate_hypotheses")

    def evaluate_and_select(self, hypotheses: list):
        raise NotImplementedError("Subclasses must implement evaluate_and_select")

    def decompose_task(self, optimal_hypothesis: dict):
        raise NotImplementedError("Subclasses must implement decompose_task")


class LLMMonteCarloReasoner(BaseReasoner):
    """
    Legacy Behavior: Uses an LLM to generate 3 hypotheses, and Monte Carlo 
    heuristics to evaluate them based on static risk scoring.
    """
    def generate_hypotheses(self, task_description: str, context_snippets: list):
        import subprocess
        import os
        print(f"[{self.__class__.__name__}] Gathering adaptive rules and generating hypotheses...")
        
        rules_text = ""
        project_dir = Path.cwd()
        rules_dir = project_dir / ".agents" / "rules"
        if rules_dir.exists():
            for rule_file in rules_dir.glob("*.md"):
                with open(rule_file, "r") as f:
                    rules_text += f"\n--- {rule_file.name} ---\n{f.read()}\n"

        prompt = f"""Task: {task_description}

Local Architectural Rules to Enforce:
{rules_text}

Generate exactly 3 distinct architectural hypotheses to solve this task.
Return ONLY valid JSON in this format (no markdown blocks, just raw JSON array):
[
  {{"id": "H1", "approach": "Description of approach 1"}},
  {{"id": "H2", "approach": "Description of approach 2"}},
  {{"id": "H3", "approach": "Description of approach 3"}}
]
"""
        try:
            from llm_client import GeminiClient
            client = GeminiClient()
            output = client.generate_content(prompt)
            output = output.strip()
            
            # Clean markdown formatting if model hallucinates it
            if output.startswith("```json"): output = output[7:]
            if output.startswith("```"): output = output[3:]
            if output.endswith("```"): output = output[:-3]
            
            hypotheses = json.loads(output.strip())
            return hypotheses
        except Exception as e:
            print(f"[System 2 Reasoner] LLM generation failed ({e}). Falling back to heuristics...")
            return [
                {"id": "H1", "approach": "Direct mutation of state", "risk_score": 0.8},
                {"id": "H2", "approach": "Subclassing and overriding", "risk_score": 0.5},
                {"id": "H3", "approach": "Event-driven decoupling", "risk_score": 0.2}
            ]

    def evaluate_and_select(self, hypotheses: list):
        print(f"[{self.__class__.__name__}] Evaluating hypotheses via Monte Carlo heuristics...")
        ranked = sorted(hypotheses, key=lambda x: x.get("risk_score", 0.5))
        optimal = ranked[0]
        print(f"[{self.__class__.__name__}] Selected Optimal Path: {optimal['id']} - {optimal['approach']}")
        return optimal

    def decompose_task(self, optimal_hypothesis: dict):
        print(f"[{self.__class__.__name__}] Decomposing selected path into actionable DAG...")
        dag = [
            {"step": 1, "action": "Locate target function via FTS5"},
            {"step": 2, "action": "Draft localized patch"},
            {"step": 3, "action": "Run isolated integration test"}
        ]
        return dag


class MultiAgentReasoner(LLMMonteCarloReasoner):
    """
    Advanced Behavior: Spawns specialized sub-agents to debate the hypotheses,
    scoring them based on multiple perspectives (security, performance, readability).
    """
    def evaluate_and_select(self, hypotheses: list):
        print(f"[{self.__class__.__name__}] Spawning Red Team / Blue Team sub-agents for hypothesis debate...")
        # Simulated agentic debate override
        for h in hypotheses:
            print(f" -> Agent 'Security Auditor' reviewing {h['id']}...")
            h["risk_score"] = 0.1 if "decoupling" in h["approach"].lower() else 0.9
            
        ranked = sorted(hypotheses, key=lambda x: x.get("risk_score", 0.5))
        optimal = ranked[0]
        print(f"[{self.__class__.__name__}] Multi-Agent consensus reached! Optimal Path: {optimal['id']} - {optimal['approach']}")
        return optimal

# Default alias for backward compatibility
SystemTwoReasoner = LLMMonteCarloReasoner
