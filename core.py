import os
import shutil
import subprocess
import json
import time
from pathlib import Path

from architect import CodebaseArchitect
from experience import ExperienceReplayEngine
from reasoning import SystemTwoReasoner
from adaptation import AdaptationEngine

class SandboxManager:
    def __init__(self, source_dir: str, sandbox_base=None):
        self.source_dir = Path(source_dir).resolve()
        self.sandbox_base = Path(sandbox_base) if sandbox_base else Path.home() / ".agy_sandboxes"
        self.sandbox_id = f"sandbox_{int(time.time())}"
        self.sandbox_dir = self.sandbox_base / self.sandbox_id
        
    def create_sandbox(self):
        os.makedirs(self.sandbox_base, exist_ok=True)
        if self.sandbox_dir.exists():
            shutil.rmtree(self.sandbox_dir)
        shutil.copytree(self.source_dir, self.sandbox_dir, ignore=shutil.ignore_patterns('.git', 'node_modules', '__pycache__'))
        print(f"[Sandbox] Created at {self.sandbox_dir}")
        return self.sandbox_dir
        
    def apply_to_main(self):
        print(f"[Sandbox] Tests passed. Applying {self.sandbox_dir} to {self.source_dir}")
        shutil.copytree(self.sandbox_dir, self.source_dir, dirs_exist_ok=True, ignore=shutil.ignore_patterns('.git', 'node_modules', '__pycache__'))
        
    def cleanup(self):
        shutil.rmtree(self.sandbox_dir, ignore_errors=True)

class ActorCriticSwarm:
    def __init__(self, sandbox_dir: Path, memory: CodebaseArchitect):
        self.sandbox_dir = sandbox_dir
        self.memory = memory
        self.max_loops = 5
        
    def run_test_suite(self, test_command: str):
        print(f"[Critic] Executing verification: {test_command}")
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        process = subprocess.Popen(
            test_command, cwd=self.sandbox_dir, shell=True, 
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env
        )
        stdout, stderr = process.communicate()
        is_valid = (process.returncode == 0)
        
        critic_report = ""
        if not is_valid:
            semantic_hints = self.memory.semantic_search(stderr, limit=1)
            critic_report = f"Raw Stderr: {stderr[:500]}\n"
            if semantic_hints:
                file_path, line_no, func, snippet = semantic_hints[0]
                critic_report += f"-> [Critic Heuristic]: Likely bug near {func} in {Path(file_path).name} (L{line_no}). "
                critic_report += f"Context: {snippet}"
        return is_valid, stdout, critic_report

class ApexOrchestrator:
    """The Complete 5-Tier Intelligence & Adaptation Engine."""
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.workflow_path = os.path.join(project_path, "workflow.json")
        
        # Initialize Core Engines
        self.memory = CodebaseArchitect(self.project_path)
        self.experience = ExperienceReplayEngine(self.project_path)
        self.reasoner = SystemTwoReasoner(self.memory)
        self.adaptation = AdaptationEngine(self.project_path)
        
        self.memory.map_project() 
        
    def execute_task(self, task_description: str, test_command: str):
        import concurrent.futures
        print(f"\n=== [Apex Orchestrator] Booting Intelligence Sequence ===")
        
        # 1. Experience Replay (RLHF Simulator)
        past_diff = self.experience.retrieve_relevant_experience(task_description)
        if past_diff:
            print(f"[Episodic Memory] Injecting past successful trajectory...")
            
        # 2. System 2 Reasoning & Metacognitive Planning
        hypotheses = self.reasoner.generate_hypotheses(task_description, [])
        
        print(f"[Scaling Compute] Racing {len(hypotheses)} distinct hypotheses in parallel sandboxes...")
        
        def run_sandbox_race(hypothesis):
            # Create isolated sandbox for this specific hypothesis
            sandbox = SandboxManager(self.project_path)
            s_dir = sandbox.create_sandbox()
            swarm = ActorCriticSwarm(s_dir, self.memory)
            
            actor_prompt = f"Task: {task_description}\nHypothesis to Execute: {hypothesis['approach']}\n"
            if past_diff:
                actor_prompt += f"Context from similar past task:\n{past_diff}\n"
                
            print(f"[Parallel Swarm] Spawning AGY Model for {hypothesis['id']}...")
            subprocess.run(["agy", "-p", actor_prompt], cwd=s_dir)
            
            is_valid, out, critic_report = swarm.run_test_suite(test_command)
            return {"hypothesis": hypothesis, "is_valid": is_valid, "sandbox": sandbox, "critic_report": critic_report}

        # 3. Parallel Swarm Execution
        success_result = None
        failed_attempts = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(hypotheses)) as executor:
            futures = {executor.submit(run_sandbox_race, h): h for h in hypotheses}
            
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result["is_valid"]:
                    print(f"\n🚀 [Swarm Intelligence] Hypothesis {result['hypothesis']['id']} succeeded first! Terminating race.")
                    success_result = result
                    break # We found a winner!
                else:
                    print(f"\n❌ [Swarm Intelligence] Hypothesis {result['hypothesis']['id']} failed.")
                    failed_attempts.append(result["critic_report"])
                    result["sandbox"].cleanup() # Cleanup losers
                    
        # 4. Continuous Adaptation & Learning
        if success_result:
            winning_sandbox = success_result["sandbox"]
            winning_sandbox.apply_to_main()
            self._update_workflow("completed")
            self.experience.record_experience(task_description, "NONE", "SIMULATED_SUCCESSFUL_PATCH")
            
            if len(failed_attempts) > 0:
                lesson = self.adaptation.extract_lesson(failed_attempts, "SUCCESS", task_description)
                self.adaptation.write_permanent_rule(lesson)
                
            winning_sandbox.cleanup()
        else:
            print("[Orchestrator] Fatal Failure across ALL parallel swarms. Extracting anti-pattern rule to prevent repeat...")
            self._update_workflow("failed")
            lesson = self.adaptation.extract_lesson(failed_attempts, "NONE", task_description)
            self.adaptation.write_permanent_rule(lesson)
            
        print(f"=== [Apex Orchestrator] Execution Complete ===")
        
    def _update_workflow(self, status: str):
        if os.path.exists(self.workflow_path):
            with open(self.workflow_path, 'r') as f:
                data = json.load(f)
            data['status'] = status
            with open(self.workflow_path, 'w') as f:
                json.dump(data, f, indent=4)

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 2:
        orch = ApexOrchestrator(sys.argv[1])
        orch.execute_task("Automated Meta-Cognitive Task", sys.argv[2])
