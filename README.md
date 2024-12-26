# Testing model baselines on ARC-AGI with addtionsof Adapters for Google, Openrouter, Langgraph

QUICK START
```
1. export GEMINI_API_KEY=XXXXXX
2. pip install -r requirements.txt
2. python3 run_sequential.py
```

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

More about Langchain ```https://langchain-ai.github.io/langgraph/tutorials/introduction/#requirements```

## Explanation of `src/adapters/langgraph.py`

This file defines the `LangGraphAdapter` class, which is responsible for interacting with a language model using LangGraph. 
LangGraph allows for the creation of complex workflows for handling interactions with language models. 
This adapter is specifically designed for solving abstract reasoning problems, particularly those in the style of the Abstraction and Reasoning Corpus (ARC).

**Key Components:**

1.  **`LangGraphAdapter` Class:**
    *   **Initialization (`__init__`)**:
        *   Takes the `model_name`, `max_tokens`, and `max_response_length` as input.
        *   Retrieves the `OPENROUTER_API_KEY` from environment variables.
        *   Initializes the `ChatOpenAI` language model with specified parameters, including a higher temperature for exploration, increased timeout, and retries.
        *   Creates a directory for logs (`logs/langgraph_conversations`).
        *   Calls `_create_workflow()` to set up the LangGraph workflow.
    *   **`_extract_json_array(self, text: str) -> Optional[str]`**:
        *   This method attempts to extract a valid JSON array from a given text using multiple methods:
            *   Direct JSON parsing (if the text is a valid JSON string).
            *   Regex extraction (if the text contains a JSON array within it).
            *   Extracting numbers and building an array (if the text contains only numbers).
        *   Returns the extracted JSON array as a string or `None` if no valid JSON array is found.
    *   **`_should_continue(self, state: State) -> Union[Tuple[str, str], str]`**:
        *   This method determines whether the LangGraph workflow should continue generating a response or end.
        *   It checks if the response is too short, too long, or contains "sorry".
        *   It also checks if a valid JSON array can be extracted from the response.
        *   It allows for a maximum of 2 retries if the response is invalid.
        *   Returns `("continue", "generate")` to continue the workflow or `END` to stop.
    *   **`_create_workflow(self) -> Any`**:
        *   Creates a `StateGraph` object, which represents the LangGraph workflow.
        *   Adds a "generate" node that calls the `_generate` method.
        *   Adds conditional edges using `_should_continue` to determine the next step.
        *   Sets the entry point to "generate".
        *   Compiles the workflow and returns it.
    *   **`_generate(self, state: State) -> State`**:
        *   This method is responsible for generating a response using the language model.
        *   It invokes the LLM with the current messages in the state.
        *   Updates the state with the model's response.
        *   Logs the raw model response.
        *   Returns the updated state.
    *   **`_log_conversation(self, task_id: str, message: str, message_type: str = "INFO")`**:
        *   Logs the conversation to a file in the `logs/langgraph_conversations` directory.
        *   Each log entry includes a timestamp, message type, and the message itself.
    *   **`make_prediction(self, prompt: str) -> str`**:
        *   This is the main method for making a prediction.
        *   It extracts a task ID from the prompt or generates a timestamp if no task ID is found.
        *   It logs the start of the task and the prompt.
        *   It initializes the state with the system and human messages.
        *   It invokes the LangGraph workflow with the initial state.
        *   It attempts to extract a JSON array from the final response.
        *   Returns the extracted JSON array or an empty array if no valid JSON is found.
    *   **`chat_completion(self, messages: List[Dict[str, str]], tools: List = None) -> str`**:
        *   Raises a `NotImplementedError` as chat completion is not implemented for this adapter.
    *   **`extract_json_from_response(self, input_response: str) -> List[List[int]]`**:
        *   Extracts and formats the JSON response using the `_extract_json_array` method.
        *   Returns the parsed JSON as a list of lists of integers.

2.  **`State` TypedDict:**
    *   Defines the structure of the state object used by LangGraph.
    *   Includes fields for messages, next step, current response, final JSON, retries, and task ID.

**Workflow:**

The LangGraph workflow consists of the following steps:

1.  **Generate:** The `_generate` method invokes the language model to generate a response.
2.  **Conditional Check:** The `_should_continue` method checks the response and determines if the workflow should continue or end.
3.  **Loop or End:** If the response is invalid or needs to be retried, the workflow loops back to the "generate" node. Otherwise, the workflow ends.

**How it Works Together:**

The `LangGraphAdapter` uses LangGraph to create a workflow that handles the interaction with the language model. The `make_prediction` method sets up the initial state and invokes the workflow. The workflow then iteratively generates responses, checks their validity, and extracts the final JSON array. The `_log_conversation` method logs all interactions for debugging and analysis.

**In Summary:**

The `src/adapters/langgraph.py` file defines the `LangGraphAdapter` class, which uses LangGraph to manage interactions with a language model. It includes a custom workflow for generating responses, extracting JSON, and handling retries. This adapter is specifically designed for solving abstract reasoning problems and provides a robust and flexible way to interact with language models.



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
For more information visit the [ARC Prize](https://arcprize.org/).
