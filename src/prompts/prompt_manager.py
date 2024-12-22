from src.utils import convert_2d_list_to_string
from src.models import ARCPair
from typing import List

def _load_prompt(prompt_name: str) -> str:
    """
    Load a prompt from the prompts directory
    """
    # Load the pre-prompt as raw string if it exists
    try:
        with open("src/prompts/system_pre_prompt.txt", "r") as f:
            pre_prompt = r"{}".format(f.read())
    except FileNotFoundError:
        pre_prompt = ""

    # Load the main prompt for formatting
    with open(f"src/prompts/{prompt_name}.txt", "r") as f:
        main_prompt = f.read()
    
    return pre_prompt + main_prompt

def convert_task_pairs_to_prompt(training_pairs: List[ARCPair], test_input: ARCPair) -> str:
    """
    Convert the training pairs to a prompt
    """

    prompt_template = _load_prompt("system_prompt")

    training_examples = ""
    for i, pair in enumerate(training_pairs):
        training_examples += f"--Example {i}-- \n\n INPUT: \n\n"
        training_examples += convert_2d_list_to_string(pair.input) + "\n\n"
        training_examples += f"OUTPUT: \n\n"
        training_examples += convert_2d_list_to_string(pair.output) + "\n\n"

    test_input = convert_2d_list_to_string(test_input.input)

    return prompt_template.format(training_examples=training_examples, test_input=test_input)