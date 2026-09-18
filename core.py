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
        
    def reset(self):
        print(f"[Sandbox] Rolling back {self.sandbox_dir} to clean state.")
        shutil.rmtree(self.sandbox_dir, ignore_errors=True)
        shutil.copytree(self.source_dir, self.sandbox_dir, ignore=shutil.ignore_patterns('.git', 'node_modules', '__pycache__'))
        
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
            if semantic_hints:
                from sniper import ContextSniper
                formatted_results = []
                for hint in semantic_hints:
                    formatted_results.append({
                        "file_path": hint[0],
                        "line_number": hint[1],
                        "function_name": hint[2],
                        "content": hint[3]
                    })
                sniper = ContextSniper(formatted_results)
                critic_report = sniper.generate_prompt(f"Fix this test failure:\n{stderr[:500]}")
            else:
                critic_report = f"Raw Stderr: {stderr[:500]}\n(No semantic context found in FTS5)"
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
        print(f"\n=== [Apex Orchestrator] Booting Intelligence Sequence ===")
        from task_queue import TaskQueue
        
        queue = TaskQueue()
        state = {}
        
        def retrieve_memory():
            state['past_diff'] = self.experience.retrieve_relevant_experience(task_description)
            if state['past_diff']:
                print(f"[Episodic Memory] Injecting past successful trajectory...")
        
        def generate_hypotheses():
            state['hypotheses'] = self.reasoner.generate_hypotheses(task_description, [])
            print(f"[Memory Safe Compute] Testing {len(state['hypotheses'])} distinct hypotheses sequentially...")
            
        def run_sandbox_race(hypothesis, memory_controller):
            from task_queue import TaskQueue
            sandbox = SandboxManager(self.project_path)
            s_dir = sandbox.create_sandbox()
            swarm = ActorCriticSwarm(s_dir, self.memory)
            
            loop_count = 0
            success = False
            final_critic_report = ""
            
            while loop_count < swarm.max_loops and not success:
                loop_count += 1
                
                actor_prompt = f"Task: {task_description}\nHypothesis to Execute: {hypothesis['approach']}\n"
                if state.get('past_diff'):
                    actor_prompt += f"Context from similar past task:\n{state['past_diff']}\n"
                if final_critic_report:
                    actor_prompt += f"\nPrevious Attempt Failed! {final_critic_report}\nFix the code based on this STRICT sniper heuristic."
                    
                # Gated Execution via Banker's Algorithm
                memory_controller.request_allocation(f"Hypothesis {hypothesis['id']}")
                try:
                    import os
                    env = os.environ.copy()
                    env["APEX_ACTIVE"] = "1"
                    subprocess.run(["agy", "-p", actor_prompt], cwd=s_dir, env=env)
                finally:
                    memory_controller.release_allocation(f"Hypothesis {hypothesis['id']}")
                
                is_valid, out, critic_report = swarm.run_test_suite(test_command)
                if is_valid:
                    success = True
                else:
                    final_critic_report = critic_report
                    sandbox.reset()
                    
            return {"hypothesis": hypothesis, "is_valid": success, "sandbox": sandbox, "critic_report": final_critic_report}

        def execute_hypotheses():
            import concurrent.futures
            from memory_controller import BankersMemoryController
            
            # Initialize Banker's Controller with safe Android margins
            mem_controller = BankersMemoryController(agent_mb=250, safe_margin_mb=350)
            
            success_result = None
            failed_attempts = []
            
            print(f"[Scaling Compute] Racing {len(state['hypotheses'])} distinct hypotheses via AIMD Memory Parallelism...")
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=len(state['hypotheses'])) as executor:
                futures = {executor.submit(run_sandbox_race, h, mem_controller): h for h in state['hypotheses']}
                
                for future in concurrent.futures.as_completed(futures):
                    result = future.result()
                    if result["is_valid"]:
                        print(f"\n🚀 [Swarm Intelligence] Hypothesis {result['hypothesis']['id']} succeeded first! Terminating race.")
                        success_result = result
                        # Cancel remaining futures if possible, or just let them clean up
                        break
                    else:
                        print(f"\n❌ [Swarm Intelligence] Hypothesis {result['hypothesis']['id']} failed.")
                        failed_attempts.append(result["critic_report"])
                        result["sandbox"].cleanup()
                        
            state['success_result'] = success_result
            state['failed_attempts'] = failed_attempts
            
        def apply_adaptation():
            success_result = state.get('success_result')
            failed_attempts = state.get('failed_attempts', [])
            
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
                print("[Orchestrator] Fatal Failure across ALL swarms. Extracting anti-pattern rule to prevent repeat...")
                self._update_workflow("failed")
                lesson = self.adaptation.extract_lesson(failed_attempts, "NONE", task_description)
                self.adaptation.write_permanent_rule(lesson)
                
        # Build DAG
        queue.add_task("memory", retrieve_memory)
        queue.add_task("reasoning", generate_hypotheses, dependencies=["memory"])
        queue.add_task("execution", execute_hypotheses, dependencies=["reasoning"])
        queue.add_task("adaptation", apply_adaptation, dependencies=["execution"])
        
        # Execute DAG
        queue.execute_all()
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
