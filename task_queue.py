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
        queue = [node for node, degree in self.in_degree.items() if degree == 0]
        execution_order = []
        visited_count = 0

        while queue:
            current = queue.pop(0)
            execution_order.append(current)
            visited_count += 1

            for dependent in self.graph.get(current, []):
                self.in_degree[dependent] -= 1
                if self.in_degree[dependent] == 0:
                    queue.append(dependent)

        if visited_count != len(self.in_degree):
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

# Default alias to maintain backward compatibility
TaskQueue = SequentialTaskQueue
