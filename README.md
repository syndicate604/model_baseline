# Testing model baselines on ARC-AGI with addtionsof Adapters for Google, Openrouter, Langgraph

More about Langchain ```https://langchain-ai.github.io/langgraph/tutorials/introduction/#requirements```

This forked repo has been upgraded with the option to 
- test over 150 models
- test free models from Google
- test content limited models with Langchain to extend the LLM abilities
- add custom prompts

## Adding custom prompts 

## Explanation of `system_pre_prompt.txt` and its Integration with `prompt_manager.py`

This section explains how the `system_pre_prompt.txt` file enhances the prompt generation process in `prompt_manager.py`.

**Background:**

The `prompt_manager.py` script is responsible for loading and formatting prompts used by the language model. 
It takes a main prompt (e.g., `system_prompt.txt`) and inserts training examples and test inputs into it.

**`system_pre_prompt.txt` as an Upgrade:**

The introduction of `system_pre_prompt.txt` allows for a system-level pre-prompt to be added to all prompts. 
This pre-prompt is loaded and prepended to the main prompt before any formatting takes place.

**How it Works:**

1.  **Loading the Pre-Prompt:**
    *   The `_load_prompt` function in `prompt_manager.py` now attempts to load the content of `src/prompts/system_pre_prompt.txt`.
    *   The file is read in RAW Format so you can include special character and math operators but not variables
    *   If the file exists, its content is read as a raw string and stored in the `pre_prompt` variable.
    *   If the file does not exist, `pre_prompt` is set to an empty string.

2.  **Loading the Main Prompt:**
    *   The `_load_prompt` function then loads the main prompt from a file in the `src/prompts` directory (e.g., `system_prompt.txt`).

3.  **Combining Prompts:**
    *   The `pre_prompt` is prepended to the `main_prompt` before being returned. This means that the content of `system_pre_prompt.txt` will always be at the beginning of the final prompt.

4.  **Formatting the Prompt:**
    *   The `convert_task_pairs_to_prompt` function uses the combined prompt (pre-prompt + main prompt) as a template and inserts training examples and test inputs into it.

**Benefits of Using `system_pre_prompt.txt`:**

*   **System-Level Instructions:** The pre-prompt allows you to add instructions or context that should be applied to all prompts. This can include things like:
    *   Specifying the role of the language model.
    *   Setting constraints on the output format.
    *   Providing general guidelines for the task.
*   **Centralized Configuration:** The pre-prompt is defined in a single file, making it easy to modify or update system-level instructions without having to change individual prompt files.
*   **Improved Consistency:** By adding a pre-prompt, you can ensure that all prompts have a consistent starting point, which can lead to more predictable and reliable results.

## Google Experimental Models you want use model='gemini-2.0-flash-exp' FREE for 10 RQM

Get your API Key - ```https://aistudio.google.com/app/apikey```

To run Gemini Models add a "GEMINI_API_KEY" to your env 

```
export GEMINI_API_KEY=XXXXXX
```
## OpenRouter has over 150 models of all kinds you can run but you cannot run FREE models with ARC they are too limited 

```
export OPENROUTER_API_KEY=XXXXXX
```

Get your keys ```https://openrouter.ai/models```

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
