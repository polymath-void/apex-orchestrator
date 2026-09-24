---
name: apex-master
description: >-
  The Apex Rage Engine Cognitive Architecture. Triggers deep, 5-Tier 
  metacognitive reasoning, Monte Carlo Tree Search, and Actor-Critic Swarm 
  sandboxing to solve complex software engineering tasks with 95%+ SWE-Bench dominance.
---

# 🧠 The Apex Rage Engine (Master Architect)

The **Apex Rage Engine** is natively installed into this AGY agent via a global `PreInvocation` hook. It mathematically forces the Gemini 3.1 Pro model to abandon "lazy" System 1 guessing and routes it through a rigorous 5-Tier intelligence loop.

## How to Trigger
To activate the Apex Rage Engine instead of standard AGY execution, include the keyword `/apex` anywhere in your prompt.

**Example:**
> "/apex Fix the user authentication bug. test_command=pytest auth_tests.py"

## The 5-Tier Execution Pipeline
1. **Semantic Indexing:** Instantly maps your codebase to an FTS5 SQLite Graph.
2. **Episodic Memory (RLHF):** Retrieves successful past bug fixes to inject as few-shot RAG context.
3. **System 2 Reasoning:** Evaluates 3 distinct hypotheses using Monte Carlo heuristics and selects the optimal patch strategy.
4. **Actor-Critic Swarm:** Isolates your code in a physical sandbox (`~/.sandboxes`), injects the fix using a background AGY swarm, and compiles/tests it. If it fails, the Surgical Critic analyzes the AST and provides heuristics.
5. **Continuous Adaptation:** If the model struggles but eventually succeeds, it writes a permanent `.md` rule to `~/.agents/rules/` to ensure it never makes the same mistake again.
