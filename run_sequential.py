import subprocess
import os
import time
import argparse
from pathlib import Path

def get_model_shortname(model_path):
    # Extract the last part of the model path and remove any preview/beta suffixes
    model_name = model_path.split('/')[-1]
    for suffix in ['-preview', '-beta']:
        if suffix in model_name:
            model_name = model_name.replace(suffix, '')
    return model_name

def init_submodules():
    subprocess.run(["git", "submodule", "update", "--init"], check=True)

def main():
    # Initialize git submodules first
    init_submodules()
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", default="openrouter", help="Provider name")
    parser.add_argument("--model", default="qwen/qwen-2.5-coder-32b-instruct", help="Model name")
    args = parser.parse_args()

    # Read task IDs from file
    task_file = Path("./data/task_lists/public_evaluation.txt")
    with open(task_file) as f:
        task_ids = [line.strip() for line in f if line.strip()]

    # Create submission directory name based on model name
    model_shortname = get_model_shortname(args.model)
    submissions_dir = Path(f"submissions/{model_shortname}_{args.provider}")
    submissions_dir.mkdir(parents=True, exist_ok=True)
    completed_ids = {f.stem for f in submissions_dir.glob("*.json")}

    # Filter task IDs to skip completed ones until the last one
    tasks_to_run = []
    for task_id in task_ids:
        if task_id in completed_ids:
            print(f"Skipping completed task: {task_id}")
        else:
            tasks_to_run.append(task_id)

    # Now tasks_to_run contains only the tasks that need to be executed
    print(f"Tasks to run: {tasks_to_run}")

    # Rate limiting setup is necessary for Gemini 
    requests_per_minute = 10
    delay_between_requests = 60 / requests_per_minute  # seconds

    # Run tasks sequentially
    for task_id in tasks_to_run:
        print(f"\nStarting task {task_id}")
        cmd = [
            "python3", "-m", "main",
            "--data_dir", "data/arc-agi/data/evaluation",
            "--provider", args.provider,
            "--model", args.model,
            "--task_id", task_id,
            "--save_submission_dir", str(submissions_dir),
            "--print_logs"
        ]
        try:
            subprocess.run(cmd, check=True)
            print(f"Completed task {task_id}")
        except subprocess.CalledProcessError as e:
            print(f"Error in task {task_id}: {e}")
            continue

        # Sleep to maintain the rate limit
        time.sleep(delay_between_requests)

if __name__ == "__main__":
    main()
