from typing import Callable, Any, Dict, List, Optional
import concurrent.futures

class BaseTaskQueue:
    """
    Abstract BaseTaskQueue for DAG parsing and dependency resolution.
    """
    def __init__(self):
        self.graph: Dict[str, List[str]] = {}
        self.in_degree: Dict[str, int] = {}
        self.tasks: Dict[str, Callable[[], Any]] = {}

    def add_task(self, task_id: str, task_func: Callable[[], Any], dependencies: Optional[List[str]] = None) -> None:
        if task_id not in self.graph:
            self.graph[task_id] = []
            self.in_degree[task_id] = 0
            
        self.tasks[task_id] = task_func

        if dependencies:
            for dep in dependencies:
                if dep not in self.graph:
                    self.graph[dep] = []
                    self.in_degree[dep] = 0
                
                self.graph[dep].append(task_id)
                self.in_degree[task_id] += 1

    def _topological_sort(self) -> List[str]:
        in_degree_copy = self.in_degree.copy()
        queue = [node for node, degree in in_degree_copy.items() if degree == 0]
        execution_order = []
        visited_count = 0

        while queue:
            current = queue.pop(0)
            execution_order.append(current)
            visited_count += 1

            for dependent in self.graph.get(current, []):
                in_degree_copy[dependent] -= 1
                if in_degree_copy[dependent] == 0:
                    queue.append(dependent)

        if visited_count != len(in_degree_copy):
            raise ValueError("Cycle detected in Task DAG! Execution order cannot be resolved.")
        
        return execution_order

    def execute_all(self) -> Dict[str, Any]:
        """Must be overridden by subclasses."""
        raise NotImplementedError("Subclasses must implement execute_all")


class SequentialTaskQueue(BaseTaskQueue):
    """
    Legacy execution model: Runs tasks sequentially in topological order.
    """
    def execute_all(self) -> Dict[str, Any]:
        execution_order = self._topological_sort()
        results = {}

        for task_id in execution_order:
            task_func = self.tasks.get(task_id)
            if not task_func:
                continue
                
            print(f"[SequentialTaskQueue] Executing DAG node: {task_id}")
            try:
                results[task_id] = task_func()
            except Exception as e:
                raise RuntimeError(f"Task '{task_id}' failed during execution: {e}") from e

        return results


class AdaptiveRetryTaskQueue(SequentialTaskQueue):
    """
    Adaptive execution model: Overrides execution to automatically retry 
    failed nodes by analyzing the failure.
    """
    def __init__(self, max_retries=2):
        super().__init__()
        self.max_retries = max_retries

    def execute_all(self) -> Dict[str, Any]:
        execution_order = self._topological_sort()
        results = {}

        for task_id in execution_order:
            task_func = self.tasks.get(task_id)
            if not task_func:
                continue
                
            print(f"[AdaptiveRetryTaskQueue] Executing DAG node: {task_id}")
            attempts = 0
            success = False
            while attempts < self.max_retries and not success:
                try:
                    results[task_id] = task_func()
                    success = True
                except Exception as e:
                    attempts += 1
                    print(f"⚠️ [AdaptiveRetryTaskQueue] Task '{task_id}' failed (Attempt {attempts}/{self.max_retries}): {e}")
                    if attempts == self.max_retries:
                        raise RuntimeError(f"Task '{task_id}' permanently failed after {self.max_retries} attempts.") from e
                    print(f"[AdaptiveRetryTaskQueue] Adapting and retrying '{task_id}'...")
                    # Future adaptive logic goes here (e.g., self-healing via agents)

        return results


class DynamicDAGTaskQueue(SequentialTaskQueue):
    """
    A task queue that allows tasks to dynamically append new tasks 
    during execution (e.g. adding 'debug' if a task fails).
    """
    def execute_all(self) -> Dict[str, Any]:
        results = {}
        # We re-evaluate sort continuously in case graph mutated
        while True:
            # Re-sort to pick up new nodes
            try:
                execution_order = self._topological_sort()
            except Exception as e:
                raise RuntimeError(f"Cycle detected during dynamic expansion: {e}")

            # Filter out tasks we already executed
            pending = [t for t in execution_order if t not in results]
            if not pending:
                break

            task_id = pending[0] # execute the next pending
            task_func = self.tasks.get(task_id)
            if not task_func:
                results[task_id] = None
                continue
                
            print(f"[DynamicDAGTaskQueue] Executing DAG node: {task_id}")
            try:
                results[task_id] = task_func()
            except Exception as e:
                # Add a dynamic node to handle the error
                recovery_task_id = f"{task_id}_recovery_{len(self.tasks)}"
                print(f"[DynamicDAGTaskQueue] Task {task_id} failed. Injecting dynamic recovery node: {recovery_task_id}")
                
                # Dynamic task definition
                def recovery_func():
                    print(f"[Recovery] Attempting to auto-fix state for {task_id} failure: {e}")
                    # Could invoke a sub-agent here
                    return f"Recovered from {e}"

                self.add_task(recovery_task_id, recovery_func)
                # Ensure the original dependent tasks wait for recovery
                for dep, edges in list(self.graph.items()):
                    if task_id in edges:
                        self.graph[dep].append(recovery_task_id)
                        self.in_degree[recovery_task_id] += 1
                
                # Note: We just raise for now to avoid infinite loops, but in a full system 
                # we'd allow the recovery task to unblock.
                raise RuntimeError(f"Task '{task_id}' failed and dynamic recovery is still experimental: {e}")

        return results


class ParallelSwarmQueue(BaseTaskQueue):
    """
    Executes independent tasks in parallel using concurrent.futures.
    Ideal for Swarm deployments.
    """
    def execute_all(self) -> Dict[str, Any]:
        execution_order = self._topological_sort()
        results = {}
        in_degree_running = self.in_degree.copy()
        completed = set()

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            while len(completed) < len(execution_order):
                # Find ready tasks
                ready_tasks = [
                    t for t in execution_order 
                    if t not in completed and in_degree_running[t] == 0
                ]
                
                if not ready_tasks:
                    # Wait a bit if we have tasks running but none ready
                    import time
                    time.sleep(0.1)
                    continue

                futures = {}
                for t in ready_tasks:
                    func = self.tasks.get(t)
                    if func:
                        print(f"[ParallelSwarmQueue] Dispatching node: {t}")
                        futures[executor.submit(func)] = t
                    else:
                        completed.add(t)
                        self._update_degrees(t, in_degree_running)

                for future in concurrent.futures.as_completed(futures):
                    t = futures[future]
                    try:
                        results[t] = future.result()
                    except Exception as e:
                        raise RuntimeError(f"Parallel task '{t}' failed: {e}") from e
                    completed.add(t)
                    self._update_degrees(t, in_degree_running)

        return results

    def _update_degrees(self, completed_task: str, in_degree_running: Dict[str, int]):
        for dependent in self.graph.get(completed_task, []):
            if in_degree_running[dependent] > 0:
                in_degree_running[dependent] -= 1

# Default alias to maintain backward compatibility
TaskQueue = ParallelSwarmQueue
