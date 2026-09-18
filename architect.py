import os
import ast
import sqlite3
from pathlib import Path

class CodebaseArchitect:
    """
    Tier 1 (Apex Edition): The Semantic Spatial Memory Engine.
    Uses SQLite FTS5 to index raw code bodies and docstrings, granting the 
    Orchestrator Cursor-like deep contextual retrieval without heavy ML models.
    """
    def __init__(self, project_dir: str, db_name="architect_memory.db"):
        self.project_dir = Path(project_dir).resolve()
        self.db_path = self.project_dir / db_name
        self._init_db()

    def _init_db(self):
        """Initialize the SQLite graph database with FTS5 for semantic search."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Standard AST table
        c.execute('''
            CREATE TABLE IF NOT EXISTS ast_nodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                node_type TEXT NOT NULL,
                name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                line_number INTEGER
            )
        ''')
        
        # FTS5 Virtual Table for Semantic Search
        c.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS semantic_index USING fts5(
                name, docstring, body, file_path, line_number UNINDEXED
            )
        ''')
        
        # Clear previous state
        c.execute('DELETE FROM ast_nodes')
        c.execute('DELETE FROM semantic_index')
        conn.commit()
        conn.close()

    def map_project(self):
        """Walk the project and map AST structures with Semantic Indexing."""
        print(f"[Architect] Starting Deep Semantic mapping on {self.project_dir}...")
        for root, dirs, files in os.walk(self.project_dir):
            dirs[:] = [d for d in dirs if d not in ('.git', 'node_modules', '__pycache__', '.sandboxes')]
            for file in files:
                if file.endswith('.py'):
                    file_path = Path(root) / file
                    self._parse_file(file_path)
        print(f"[Architect] Semantic Mapping complete. Indexed in FTS5.")

    def _parse_file(self, file_path: Path):
        """Extract AST and raw code bodies for indexing."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            tree = ast.parse(source_code, filename=str(file_path))
            
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    node_type = "function" if isinstance(node, ast.FunctionDef) else "class"
                    docstring = ast.get_docstring(node) or ""
                    
                    # Extract raw code segment
                    try:
                        body = ast.get_source_segment(source_code, node) or ""
                    except Exception:
                        body = ""

                    # Insert into Standard AST
                    c.execute(
                        "INSERT INTO ast_nodes (node_type, name, file_path, line_number) VALUES (?, ?, ?, ?)",
                        (node_type, node.name, str(file_path), node.lineno)
                    )
                    
                    # Insert into Semantic FTS5
                    c.execute(
                        "INSERT INTO semantic_index (name, docstring, body, file_path, line_number) VALUES (?, ?, ?, ?, ?)",
                        (node.name, docstring, body, str(file_path), node.lineno)
                    )
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[Architect] Failed to index {file_path}: {e}")

    def semantic_search(self, query: str, limit=3):
        """Searches the codebase for semantic matches using FTS5."""
        import re
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Sanitize query: only keep alphanumeric words > 2 chars
        words = re.findall(r'\b[a-zA-Z0-9_]+\b', query)
        fts_query = " OR ".join([f"{w}*" for w in words if len(w) > 2])
        
        if not fts_query:
            conn.close()
            return []
            
        try:
            c.execute(f'''
                SELECT file_path, line_number, name, snippet(semantic_index, 2, '>>>', '<<<', '...', 15) 
                FROM semantic_index 
                WHERE semantic_index MATCH ? 
                ORDER BY rank 
                LIMIT ?
            ''', (fts_query, limit))
            results = c.fetchall()
        except Exception as e:
            print(f"[Architect] FTS5 Search Error: {e}")
            results = []
            
        conn.close()
        return results

if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    architect = CodebaseArchitect(target)
    architect.map_project()
