from typing import List, Dict, Any

class ContextSniper:
    """
    ContextSniper takes FTS5 output from the Surgical Critic and generates 
    a hyper-focused prompt that restricts the LLM from hallucinating edits 
    in unrelated files.
    """
    def __init__(self, fts5_results: List[Dict[str, Any]]):
        self.fts5_results = fts5_results

    def generate_prompt(self, task_description: str) -> str:
        prompt_lines = [
            "You are an expert surgical code editor operating under STRICT DYNAMIC CONTEXT NARROWING.",
            "You are authorized to modify ONLY the exact files, functions, and line ranges provided below.",
            "DO NOT output code for or hallucinate edits in any other files or functions.",
            "",
            "--- AUTHORIZED SURGICAL CONTEXT ---"
        ]

        if not self.fts5_results:
            prompt_lines.append("No specific context targets provided. Proceed with extreme caution.")
        
        for idx, result in enumerate(self.fts5_results, start=1):
            file_path = result.get('file_path', 'Unknown File')
            line_num = result.get('line_number', 'Unknown Line')
            func_name = result.get('function_name', 'Unknown Scope')
            content = result.get('content', '')

            prompt_lines.append(f"\n[Target {idx}]")
            prompt_lines.append(f"File: {file_path}")
            prompt_lines.append(f"Function/Class: {func_name}")
            prompt_lines.append(f"Line Number: {line_num}")
            
            if content:
                prompt_lines.append("Snippet:")
                prompt_lines.append("```")
                prompt_lines.append(str(content).strip())
                prompt_lines.append("```")

        prompt_lines.extend([
            "",
            "--- END AUTHORIZED CONTEXT ---",
            "",
            "--- TASK DESCRIPTION ---",
            task_description,
            "",
            "INSTRUCTIONS:",
            "1. Implement the requested changes strictly within the provided targets.",
            "2. Provide your final modifications clearly indicating the file path and function being updated.",
            "3. Do not modify external dependencies or unrelated files."
        ])

        return "\n".join(prompt_lines)
