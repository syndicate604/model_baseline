# Testing model baselines on ARC-AGI

This repo contains code for testing model baselines on ARC-AGI. The input data is a folder containing individual files for ARC-AGI tasks.


## Setup

`git clone https://github.com/syndicate604/model_baseline.git`

`git submodule update --init`

`pip install -r requirements.txt`


## Testing a single task with ARC defaults

To test a single task, run:
`python3 -m main --data_dir data/arc-agi/data/evaluation --provider anthropic --model claude-3-5-sonnet-20241022 --task_id 0a1d4ef5 --print_logs`

Use the optional parameters to save and print the submission:

`python3 -m main --data_dir data/arc-agi/data/evaluation --provider anthropic --model claude-3-5-sonnet-20241022 --task_id {} --save_submission_dir submissions/claude_sonnet_20241022 --print_logs`

This will write one `<id>.json` file per task.

## ** NEW ** Testing all 400 Arc Tasks with my Sequential Task Runner [run_sequential.py]

This script is designed to run ARC-AGI evaluation tasks sequentially with rate limiting. It provides a robust way to process multiple tasks while handling API rate limits and tracking progress.

### Features

- **Command Line Arguments**:
  - `--provider`: Specify the LLM provider (default: "openrouter")
  - `--model`: Specify the model name (default: "qwen/qwen-2.5-coder-32b-instruct")

- **Automatic Progress Tracking**:
  - Automatically creates a submission directory based on the model name
  - Skips already completed tasks
  - Continues from where it left off if interrupted

- **Rate Limiting**:
  - Built-in rate limiting (10 requests per minute)
  - Helps prevent API throttling

### Usage

Basic usage:
```bash
python3 run_sequential.py
```

### How It Works
- Task Loading: Reads task IDs from data/task_lists/public_evaluation.txt
- ## Progress Management:
- Creates a submission directory named {model_name}_{provider}
- Tracks completed tasks by checking existing JSON files
- Skips already completed tasks
- ## Execution:
- Runs each task sequentially using the main evaluation script
- Implements rate limiting between requests
- Handles errors gracefully without stopping the entire process
- ## Output:
- Saves results in the submission directory
- Provides progress updates in the console


## Running tests with ARC concurrency using BREW

Testing multiple tasks in a single run can be slow. You can use the your parallel technique of choice to speed this up.

For example with the `parallel` [command](https://www.gnu.org/software/parallel/):

`brew install parallel`

`parallel --jobs 20 --progress python3 -m main --data_dir data/arc-agi/data/evaluation --provider anthropic --model claude-3-5-sonnet-20241022 --task_id {} --save_submission_dir submissions/claude_sonnet_20241022 --print_logs :::: ./data/task_lists/public_evaluation.txt`

Note: In order to use parllel you'll need a list of task ids. `generate_tasks_list.py` helps with this. Public data task ids are already supplied.

`python3 -m src.utils.generate_tasks_list --task_dir data/arc-agi/data/training --output_file data/task_lists/public_training`

### *** NEW ** 


## Scoring

You can score your submissions by pointing the scoring script at your submissions directory:

`python3 -m src.scoring.scoring --task_dir data/arc-agi/data/evaluation --submission_dir submissions/claude_sonnet_20241022 --print_logs --results_dir results/claude_sonnet_20241022`

Note: You'll also need to tell the script which task set to score.

## Results

Results are stored in the `results` folder. You can view historical results for models here.

# Contributing

This repo is welcome to contributions!

Specifically, we would love help adding more model adapters to the `src/adapters` folder.

More will get added by the ARC-AGI team, but we'll also gladly accept contributions from the community.

For more information visit the [ARC Prize](https://arcprize.org/).
