# 🧠 Apex Orchestrator (Antigravity Plugin)

A natively integrated, 5-Tier Cognitive Architecture for the Google Antigravity (AGY) Agent Ecosystem. 

This plugin transforms the standard Gemini 3.1 Pro agent into a massively parallel, self-correcting Swarm OS capable of competing with frontier models like Astra, Fable, and DeepSeek on SWE-Bench metrics.

## Features
1. **Semantic Deep Indexing:** Uses SQLite FTS5 to index raw code bodies, providing Cursor-like semantic context retrieval without heavy ML dependencies.
2. **Episodic Memory (RLHF Simulator):** Records successful and failed trajectories in a local database (`experience.db`) and injects them dynamically as few-shot RAG examples to permanently adapt the model's behavior.
3. **System 2 Reasoning:** Enforces a Tree of Thoughts (ToT) protocol. Evaluates 3 distinct hypotheses using Monte Carlo heuristics before execution.
4. **Parallel Actor-Critic Swarm:** Spawns 3 simultaneous, isolated physical sandboxes (`~/.agy_sandboxes`) and races the hypotheses. The first model to pass the test suite wins.
5. **Surgical Critic:** Analyzes failures and generates targeted AST heuristics instead of raw stack traces.

## 📦 Installation (Portable)

This plugin is fully portable and cross-platform (macOS, Linux, Android/Termux, Windows via WSL).

1. Clone or download this repository.
2. Run the automated installer:
   ```bash
   ./install.sh
   ```
   *The installer automatically dynamically links the paths and copies the framework to your `~/.gemini/config/plugins/` directory.*

## 🚀 Usage

Once installed, the Apex Orchestrator binds globally to your Antigravity agent via the `PreInvocation` hook.

To trigger the 5-Tier loop instead of standard AGY execution, simply include the keyword `/apex` in your prompt.

```bash
agy -p "/apex Fix the user authentication bug. test_command=pytest auth_tests.py"
```
