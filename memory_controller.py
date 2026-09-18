import time
import threading

class BankersMemoryController:
    """
    Implements Dijkstra's Banker's Algorithm adapted for Android LMK avoidance.
    Ensures that parallel subprocesses (like AGY agents) do not cross the 
    safe memory margin, dynamically throttling concurrency based on physical RAM.
    """
    def __init__(self, agent_mb=250, safe_margin_mb=350):
        self.agent_mb = agent_mb
        self.safe_margin_mb = safe_margin_mb
        self.lock = threading.Lock()
        self.condition = threading.Condition(self.lock)
        self.active_agents = 0

    def _get_available_memory_mb(self):
        try:
            with open('/proc/meminfo', 'r') as f:
                for line in f:
                    if 'MemAvailable' in line:
                        kb = int(line.split()[1])
                        return kb / 1024
            
            # Fallback for older kernels without MemAvailable
            with open('/proc/meminfo', 'r') as f:
                memfree = buffers = cached = 0
                for line in f:
                    if 'MemFree' in line: memfree = int(line.split()[1])
                    if 'Buffers' in line: buffers = int(line.split()[1])
                    if 'Cached' in line: cached = int(line.split()[1])
                return (memfree + buffers + cached) / 1024
        except Exception:
            # Failsafe dummy value if /proc/meminfo is restricted
            return 2048 

    def request_allocation(self, process_id):
        with self.condition:
            while True:
                avail_mb = self._get_available_memory_mb()
                projected_mb = avail_mb - self.agent_mb
                
                # Banker's Safety Condition
                if projected_mb > self.safe_margin_mb:
                    self.active_agents += 1
                    print(f"[\033[92mBanker's Algorithm\033[0m] Allocation GRANTED for {process_id}. Active Swarms: {self.active_agents}. Avail RAM: {avail_mb:.0f}MB -> Projected: {projected_mb:.0f}MB")
                    return
                else:
                    print(f"[\033[91mBanker's Algorithm\033[0m] Allocation DENIED for {process_id}. LMK Risk! Avail RAM: {avail_mb:.0f}MB. Applying Backpressure (waiting)...")
                    self.condition.wait(timeout=2.0)

    def release_allocation(self, process_id):
        with self.condition:
            self.active_agents -= 1
            avail_mb = self._get_available_memory_mb()
            print(f"[\033[94mBanker's Algorithm\033[0m] Allocation RELEASED by {process_id}. Active Swarms: {self.active_agents}. Avail RAM: {avail_mb:.0f}MB")
            self.condition.notify_all()
