import multiprocessing as mp
import subprocess
import sys
import time
import argparse
from pathlib import Path

def init_submodules():
    subprocess.run(["git", "submodule", "update", "--init"], check=True)

def run_task(task_id, model_name):
    cmd = [
        "bash", "-c", 
        f"source ~/.installs/arc-test/bin/activate && python3 -m main "
        f"--data_dir data/arc-agi/data/evaluation "
        f"--provider openrouter "
        f"--model {model_name} "
        f"--task_id {task_id} "
        f"--save_submission_dir submissions/{model_name.split('/')[-1]} "
        "--print_logs"
    ]
    max_retries = 3
    retry_delay = 5  # seconds
    
    for attempt in range(max_retries):
        try:
            subprocess.run(cmd, check=True, stdout=sys.stdout, stderr=sys.stderr)
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
    # Initialize git submodules first
    init_submodules()

    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default="google/gemini-flash-1.5", help="Model name to use for inference")
    parser.add_argument("--last_task_id", type=str, default=None, help="Last processed task ID to continue from")
    args = parser.parse_args()

    # Read task IDs from file
    task_file = Path("./data/task_lists/public_evaluation.txt")
    with open(task_file) as f:
        task_ids = [line.strip() for line in f if line.strip()]
    
    # Filter task IDs to continue from the next one if last_task_id is provided
    start_index = 0
    if args.last_task_id and args.last_task_id in task_ids:
        start_index = task_ids.index(args.last_task_id) + 1
    task_ids = task_ids[start_index:]
    
    # Number of parallel processes
    num_processes = 20  # reduced to avoid rate limiting
    
    # Create pool and run tasks
    print(f"Starting {len(task_ids)} tasks with {num_processes} parallel processes")
    with mp.Pool(num_processes) as pool:
        pool.starmap(run_task, [(task_id, args.model) for task_id in task_ids])
    
    print("\nAll tasks completed!")

if __name__ == "__main__":
    main()
