# Testing model baselines on ARC-AGI with addtionsof Adapters for Google, Openrouter, Lanngraph

The forked repo has been upgraded with the option to test

## Google Expermental Models 

To run Gemini Models add a "GEMINI_API_KEY" to your env 

```
export GEMINI_API_KEY=XXXXXX
```

## OpenRouter has over 150 models of all kinds you can run but you cannot run FREE models with ARC they are too limited 

```
export OPENROUTER_API_KEY=XXXXXX
```

This repo contains code for testing model baselines on ARC-AGI. 
The input data is a folder containing individual files for ARC-AGI tasks.


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

### *** NEW **  `run_sequential.py` Script Explanation

This script is designed to run a series of tasks one after the other (sequentially). It's used to evaluate language models on a set of predefined tasks. Here's a breakdown of how it works:

**Purpose:**

The `run_sequential.py` script automates the process of running evaluation tasks for different language models. 
It reads a list of tasks from a file, executes each task, and saves the results. It also handles rate limiting to avoid overloading the API.

**How it Works:**

1.  **Task List:** The script reads task IDs from the file `data/task_lists/public_evaluation.txt`. Each line in this file represents a unique task to be performed.

2.  **Command-Line Arguments:**
    *   `--provider`: Specifies the provider of the language model (e.g., "openrouter"). The default is "openrouter".
    *   `--model`: Specifies the name of the language model to use (e.g., "qwen/qwen-2.5-coder-32b-instruct"). The default is "qwen/qwen-2.5-coder-32b-instruct".

3.  **Submission Directory:** The script creates a directory to store the results of each task. The directory name is based on the model and provider, for example: `submissions/qwen-2.5-coder-32b-instruct_openrouter`.

4.  **Skipping Completed Tasks:** Before running a task, the script checks if a submission file already exists in the submission directory. If it does, the task is skipped to avoid re-running it.

5.  **Sequential Execution:** The script then iterates through the list of tasks that need to be run. For each task:
    *   It executes the `main.py` script using `python3 -m main` with the specified provider, model, task ID, and submission directory.
    *   It waits for a short period of time (rate limiting) before starting the next task. This is to avoid sending too many requests to the API at once.

**Rate Limiting:**

The script includes a rate limiting mechanism to ensure that the API is not overloaded. It waits a specific amount of time between each task execution. This is particularly important when using services like Gemini, which have strict rate limits.

**Example Usage:**

To run the script with the default settings, you can simply run:

```bash
python run_sequential.py
```

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
