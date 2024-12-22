import subprocess
import os
import time
from pathlib import Path

def main():
    # Read task IDs from file
    task_file = Path("./data/task_lists/public_evaluation.txt")
    with open(task_file) as f:
        task_ids = [line.strip() for line in f if line.strip()]

    # Define the submissions directory
    submissions_dir = Path("submissions/gemini-2.0-flash-exp-gmode")
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

    # Rate limiting setup
    requests_per_minute = 10
    delay_between_requests = 60 / requests_per_minute  # seconds

    # Run tasks sequentially
    for task_id in tasks_to_run:
        print(f"\nStarting task {task_id}")
        cmd = [
            "python3", "-m", "main",
            "--data_dir", "data/arc-agi/data/evaluation",
            "--provider", "google",
            "--model", "gemini-2.0-flash-exp",
            "--task_id", task_id,
            "--save_submission_dir", "submissions/gemini-2.0-flash-exp-gmode",
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
