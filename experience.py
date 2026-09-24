import sqlite3
from pathlib import Path
import json

class ExperienceReplayEngine:
    """
    Tier 2 (Apex Edition): The Reinforcement/Episodic Memory Engine.
    Simulates RLHF by persisting failed and successful trajectories.
    Injects successful past diffs into current tasks to aggressively 
    fine-tune the Actor's probability of success.
    """
    def __init__(self, project_dir: str, db_name="experience.db"):
        self.project_dir = Path(project_dir).resolve()
        self.db_path = self.project_dir / db_name
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        # Using FTS5 so we can semantically search past experiences based on task description
        c.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS experiences USING fts5(
                task_description, 
                error_trace, 
                successful_diff
            )
        ''')
        conn.commit()
        conn.close()

    def record_experience(self, task: str, error: str, diff: str):
        """Records a completed trajectory."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(
            "INSERT INTO experiences (task_description, error_trace, successful_diff) VALUES (?, ?, ?)",
            (task, error, diff)
        )
        conn.commit()
        conn.close()
        print(f"[ExperienceEngine] Recorded successful trajectory for task: {task[:30]}...")

    def retrieve_relevant_experience(self, current_task: str):
        """Searches past memory for a similar task and returns the diff that solved it."""
        import re
        
        # Use LLM to extract core architectural concepts for better FTS matching
        try:
            from llm_client import GeminiClient
            client = GeminiClient()
            prompt = f"Extract 3-5 core architectural keywords from this task to use as a database search query. Return ONLY space-separated keywords.\nTask: {current_task}"
            keywords_str = client.generate_content(prompt).strip()
            search_text = f"{current_task} {keywords_str}"
        except Exception:
            search_text = current_task

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        words = re.findall(r'\b[a-zA-Z0-9_]+\b', search_text)
        fts_query = " OR ".join([f"{w}*" for w in words if len(w) > 3])
        
        if not fts_query:
            conn.close()
            return None
            
        try:
            c.execute('''
                SELECT successful_diff, error_trace 
                FROM experiences 
                WHERE experiences MATCH ? 
                ORDER BY rank 
                LIMIT 1
            ''', (fts_query,))
            result = c.fetchone()
        except Exception:
            result = None
            
        conn.close()
        return result
