import json
from llm_client import GeminiClient

class EvolutionEngine:
    """
    Applies Genetic Algorithms to failed sandbox patches. 
    If a generation of hypotheses all fail, this engine mutates the best performing ones
    into a new generation of patches.
    """
    def __init__(self):
        self.llm = GeminiClient()
        
    def mutate_hypotheses(self, failed_attempts: list, task_description: str) -> list:
        """
        Takes a list of failed attempts (dict with 'hypothesis', 'error', 'critic_report')
        and generates a new set of 3 mutated hypotheses.
        """
        prompt = f"""
You are the Evolutionary Mutator for the Apex Rage Engine.
The previous generation of patches failed to solve the task: "{task_description}"

Here is the data from the failed generation:
"""
        for i, attempt in enumerate(failed_attempts):
            prompt += f"\n--- Attempt {i+1} ---\n"
            prompt += f"Approach: {attempt['hypothesis']['approach']}\n"
            prompt += f"Critic Feedback: {attempt['critic_report'][:300]}\n"
            
        prompt += """
Based on these failures, cross-breed the ideas or mutate them to avoid the specific errors encountered.
Generate exactly 3 NEW distinct hypotheses in the following JSON array format ONLY.

[
  {"id": "G2_H1", "approach": "Mutated approach description 1"},
  {"id": "G2_H2", "approach": "Mutated approach description 2"},
  {"id": "G2_H3", "approach": "Mutated approach description 3"}
]
"""
        
        try:
            output = self.llm.generate_content(prompt)
            output = output.strip()
            if output.startswith("```json"): output = output[7:]
            if output.startswith("```"): output = output[3:]
            if output.endswith("```"): output = output[:-3]
            
            mutations = json.loads(output.strip())
            return mutations
        except Exception as e:
            print(f"[Evolution Engine] Mutation failed: {e}")
            return []

class SemanticEvolutionEngine(EvolutionEngine):
    """
    Applies Genetic Algorithms guided by spatial semantic memory.
    It queries the FTS5 Codebase Architect for similar patterns before mutating.
    """
    def __init__(self, architect):
        super().__init__()
        self.architect = architect

    def mutate_hypotheses(self, failed_attempts: list, task_description: str) -> list:
        # Get semantic context
        semantic_hints = self.architect.semantic_search(task_description, limit=2)
        context_str = ""
        for hint in semantic_hints:
            context_str += f"- Found pattern in {hint[0]} (Function: {hint[2]}): {hint[3]}\n"

        prompt = f"""
You are the Semantic Evolutionary Mutator for the Apex Rage Engine.
The previous generation of patches failed to solve: "{task_description}"

We found these existing architectural patterns in the codebase that might inspire a fix:
{context_str}

Here is the data from the failed generation:
"""
        for i, attempt in enumerate(failed_attempts):
            prompt += f"\n--- Attempt {i+1} ---\n"
            prompt += f"Approach: {attempt['hypothesis']['approach']}\n"
            prompt += f"Critic Feedback: {attempt['critic_report'][:300]}\n"
            
        prompt += """
Based on these failures AND the semantic patterns from the codebase, generate exactly 3 NEW distinct hypotheses.
Return ONLY a JSON array format:

[
  {"id": "G2_H1", "approach": "Mutated approach description 1"},
  {"id": "G2_H2", "approach": "Mutated approach description 2"},
  {"id": "G2_H3", "approach": "Mutated approach description 3"}
]
"""
        try:
            output = self.llm.generate_content(prompt).strip()
            if output.startswith("```json"): output = output[7:]
            if output.startswith("```"): output = output[3:]
            if output.endswith("```"): output = output[:-3]
            return json.loads(output.strip())
        except Exception as e:
            print(f"[SemanticEvolution] Mutation failed: {e}")
            return []

