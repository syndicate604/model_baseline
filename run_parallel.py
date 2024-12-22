import multiprocessing as mp
import subprocess
import sys
import time
import argparse
from pathlib import Path

def run_task(task_id, model_name):
    cmd = [
        "python3", "-m", "main",
        "--data_dir", "data/arc-agi/data/evaluation",
        "--provider", "openrouter",
        "--model", model_name,
        "--task_id", task_id,
        "--save_submission_dir", f"submissions/{model_name.split('/')[-1]}",
        "--print_logs"
    ]
    max_retries = 3
    retry_delay = 5  # seconds
    
    for attempt in range(max_retries):
        try:
            subprocess.run(cmd, check=True)
            print(f"✓ Completed task {task_id}")
            return
        except subprocess.CalledProcessError as e:
            if attempt < max_retries - 1:
                print(f"× Error in task {task_id} (attempt {attempt + 1}/{max_retries}): {e}")
                print(f"  Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print(f"× Failed task {task_id} after {max_retries} attempts: {e}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default="google/gemini-flash-1.5", help="Model name to use for inference")
    args = parser.parse_args()

    # Read task IDs from file
    task_file = Path("./data/task_lists/public_evaluation.txt")
    with open(task_file) as f:
        task_ids = [line.strip() for line in f if line.strip()]
    
    # Filter task IDs to continue from the next one
    start_index = task_ids.index(last_processed_id) + 1 if last_processed_id in task_ids else 0
    task_ids = task_ids[start_index:]
    
    # Number of parallel processes
    num_processes = 5  # reduced to avoid rate limiting
    
    # Create pool and run tasks
    print(f"Starting {len(task_ids)} tasks with {num_processes} parallel processes")
    with mp.Pool(num_processes) as pool:
        pool.starmap(run_task, [(task_id, args.model) for task_id in task_ids])
    
    print("\nAll tasks completed!")

if __name__ == "__main__":
    main()
