import os
import shutil
import time
from pathlib import Path
from core import SandboxManager, ActorCriticSwarm, ApexOrchestrator

def run_system_test():
    print("=== Starting Orchestrator System Test ===")
    
    # Setup dummy project
    dummy_dir = "/data/data/com.termux/files/home/Projects/DummyTarget"
    os.makedirs(dummy_dir, exist_ok=True)
    
    # Write broken code
    with open(os.path.join(dummy_dir, "math_lib.py"), "w") as f:
        f.write("def add(a, b):\n    return a - b\n")
        
    # Write test
    test_code = '''
import sys
from math_lib import add
if add(2, 3) != 5:
    print("Error: 2+3 did not equal 5")
    sys.exit(1)
print("Tests Passed!")
sys.exit(0)
'''
    with open(os.path.join(dummy_dir, "test_math.py"), "w") as f:
        f.write(test_code)
        
    # Write workflow
    with open(os.path.join(dummy_dir, "workflow.json"), "w") as f:
        import json
        json.dump({"status": "pending", "type": "JSON_Task"}, f)

    print("\n--- Booting Apex Orchestrator (Live AGY Connection) ---")
    orch = ApexOrchestrator(dummy_dir)
    orch.execute_task("Fix the bug in math_lib.py where add() subtracts instead of adds.", "python3 test_math.py")
    
    # Test Apply to Main
    print("\n--- Testing Main Sync ---")
    with open(os.path.join(dummy_dir, "math_lib.py"), "r") as f:
        content = f.read()
        if "return a + b" in content or "a+b" in content or "a + b" in content:
            print("✅ Fix successfully merged back to main project.")
        else:
            print("❌ Sync to main failed. Content is:")
            print(content)
            
    # Cleanup
    shutil.rmtree(dummy_dir, ignore_errors=True)
    print("\n=== System Test Completed Successfully ===")

if __name__ == "__main__":
    run_system_test()
