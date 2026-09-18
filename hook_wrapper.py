import sys
import json
import os
from pathlib import Path
from core import ApexOrchestrator

def main():
    try:
        # 1. Read context payload from AGY
        input_data = sys.stdin.read()
        if not input_data:
            print(json.dumps({}))
            return
            
        context = json.loads(input_data)
        transcript_path = context.get("transcriptPath")
        
        # 2. Extract User Prompt from Transcript
        user_prompt = ""
        if transcript_path and os.path.exists(transcript_path):
            with open(transcript_path, 'r') as f:
                for line in f:
                    entry = json.loads(line)
                    # Get the most recent user input
                    if entry.get("type") == "USER_INPUT":
                        user_prompt = entry.get("content", "")
        
        # 3. Check for Apex Trigger
        # If the user prompt specifically asks for a deep reasoning pass or starts with /apex
        if "/apex" in user_prompt.lower() or "apex reasoning" in user_prompt.lower():
            # Get current working directory (workspace root)
            workspace = os.getcwd()
            
            # Initialize the 5-Tier architecture
            orch = ApexOrchestrator(workspace)
            
            # Execute the deep loop (this will spawn sub-AGY processes in a sandbox)
            # For the hook wrapper, we assume the user specified a test command in the prompt, or we default to a standard test script.
            # In a production hook, we'd extract the test command from the prompt.
            test_cmd = "pytest" # Default fallback
            if "test_command=" in user_prompt:
                test_cmd = user_prompt.split("test_command=")[1].split()[0]
                
            orch.execute_task(user_prompt, test_cmd)
            
            # 4. Hijack the AGY Loop
            # Force continue but inject an ephemeral message so the user knows Apex handled it natively.
            response = {
                "injectSteps": [
                    {"ephemeralMessage": "🧠 [Apex Orchestrator] Successfully intercepted task, ran 5-Tier reasoning loop, and applied verified patch to workspace."}
                ],
                "terminationBehavior": "force_continue"
            }
            print(json.dumps(response))
            return
            
        # If no apex trigger, return empty JSON to let AGY proceed normally
        print(json.dumps({}))
        
    except Exception as e:
        # Failsafe: if the hook crashes, let AGY proceed
        print(json.dumps({"injectSteps": [{"ephemeralMessage": f"Apex Hook Error: {str(e)}"}]}))

if __name__ == "__main__":
    main()
