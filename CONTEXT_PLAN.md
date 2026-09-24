# The Apex Rage Engine Blueprint (Targeting 95%+ Competitiveness)

## 1. The Core Deficits to Solve
To beat GPT-6 Astra, Claude Fable 5.1, and Cursor, a naive Actor-Critic loop is insufficient. We must engineer systems that replicate their massive pre-training, context windows, and native tool-use via local programmatic equivalents.

1. **Semantic Understanding vs. AST Maps:** Astra understands *what* code does. Our previous AST map only knows *where* it is.
2. **Contextual Memory (RLHF Equivalent):** Fable learns from execution trajectories. Our previous system was stateless and forgot everything after a test passed.
3. **Targeted Heuristic Critique:** Naive loops just feed raw `stderr` back to the model. An advanced loop requires a Critic that analyzes the AST and the error to provide surgical guidance.

## 2. The Architectural Upgrades

### Layer 1: Semantic FTS5 Engine (The Cursor Equalizer)
We will upgrade `architect.py` to utilize **SQLite FTS5 (Full-Text Search)**. 
- Instead of just logging `function_name` and `line_number`, it will extract the **docstrings and raw code bodies**.
- It will index them into a Virtual FTS5 table. 
- **Result:** The system can perform semantic-like searches. If a bug says "user login fails on token expiry", the engine searches FTS5 for "token expiry login" and instantly returns the exact AST nodes, perfectly mimicking Cursor's Shadow Workspace context retrieval.

### Layer 2: Episodic Experience Replay (The Astra Equalizer)
We will create `experience.py` (a local RAG system for execution trajectories).
- **Mechanism:** Every time the Sandbox loop succeeds, the Orchestrator records the original prompt, the failed attempts, and the final successful `diff` into `experience.db`.
- **Injection:** Before the Actor attempts a new task, the Orchestrator queries `experience.db` for similar tasks and injects the past successful diff into the system prompt.
- **Result:** This artificially simulates RLHF (Reinforcement Learning from Human Feedback) by giving the model dynamic, highly relevant few-shot examples of its own past successes.

### Layer 3: The Surgical Critic (The Fable Equalizer)
- Instead of just returning `stderr`, the validation loop will employ an analyzer that extracts the exact line number from the traceback, queries the Tier 1 AST database for the surrounding context, and builds a specialized "Critic Report".
- **Result:** The Actor receives a mathematically precise breakdown of *why* the code failed, rather than raw noise.

## 3. Implementation Phases
- [ ] **Phase 1:** Upgrade `architect.py` with FTS5 and Code Body Extraction.
- [ ] **Phase 2:** Implement `experience.py` for Episodic Memory persistence.
- [ ] **Phase 3:** Overhaul `core.py` to integrate Semantic Search and Experience Replay into the Actor-Critic loop.
- [ ] **Phase 4:** System Testing (Simulate a complex bug fix utilizing semantic search and memory).
