from typing import Callable, Any, Dict, List, Optional

class TaskQueue:
    """
    TaskQueue parses a Directed Acyclic Graph (DAG) of sub-tasks 
    and executes them sequentially in topological order.
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
        execution_order = self._topological_sort()
        results = {}

        for task_id in execution_order:
            task_func = self.tasks.get(task_id)
            if not task_func:
                continue
                
            print(f"[TaskQueue] Executing DAG node: {task_id}")
            try:
                results[task_id] = task_func()
            except Exception as e:
                raise RuntimeError(f"Task '{task_id}' failed during execution: {e}") from e

        return results
