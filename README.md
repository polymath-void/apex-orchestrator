# 🧠 Apex Rage Engine (Antigravity Plugin)

A natively integrated, 5-Tier Cognitive Architecture for the Google Antigravity (AGY) Agent Ecosystem. 

This plugin transforms the standard Gemini 3.1 Pro agent into a massively parallel, self-correcting Swarm OS capable of competing with frontier models like Astra, Fable, and DeepSeek on SWE-Bench metrics.

## Features
1. **Semantic Deep Indexing:** Uses SQLite FTS5 to index raw code bodies, providing Cursor-like semantic context retrieval without heavy ML dependencies.
2. **Episodic Memory (RLHF Simulator):** Records successful and failed trajectories in a local database (`experience.db`) and injects them dynamically as few-shot RAG examples to permanently adapt the model's behavior.
3. **Live System 2 Reasoning:** Interfaces directly with the LLM API to generate distinct hypotheses, actively reading and enforcing permanent rules from the `.agents/rules/` directory to learn continuously.
4. **Banker's Algorithm Memory Controller:** Dynamically scales parallel subprocesses using an AIMD mathematical feedback loop that polls `/proc/meminfo`. This guarantees the host device (like an Android Termux instance) will never trigger an Out-Of-Memory (OOM) kill.
5. **DAG Task Queuing:** Decomposes the orchestration lifecycle into a mathematically strict Directed Acyclic Graph (DAG) for modular, sequential execution.
6. **Context Sniper:** Extracts localizedAST nodes from the FTS5 Critic and generates a hyper-focused context prompt, physically preventing the agent from hallucinating edits outside the blast radius.
7. **Self-Healing Sandbox:** Orchestrates isolated physical sandboxes (`~/.agy_sandboxes`). If an iteration fails, it performs a hard `sandbox.reset()` to provide the agent with a clean codebase for its next heuristic attempt.

## 📦 Installation (Portable)

This plugin is fully portable and cross-platform (macOS, Linux, Android/Termux, Windows via WSL).

1. Clone or download this repository.
2. Run the automated installer:
   ```bash
   ./install.sh
   ```
   *The installer automatically dynamically links the paths and copies the framework to your `~/.gemini/config/plugins/` directory.*

## 🚀 Usage

Once installed, the Apex Rage Engine binds globally to your Antigravity agent via the `PreInvocation` hook.

To trigger the 5-Tier loop instead of standard AGY execution, simply include the keyword `/apex` in your prompt.

```bash
agy -p "/apex Fix the user authentication bug. test_command=pytest auth_tests.py"
```
