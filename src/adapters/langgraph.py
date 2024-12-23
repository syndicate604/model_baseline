from typing import TypedDict, Tuple, Optional, List, Union, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv
from src.adapters.provider import ProviderAdapter
import os
import time
from pathlib import Path
import traceback
import re
import json

load_dotenv()

class State(TypedDict):
    messages: List
    next_step: str
    current_response: str
    final_json: Optional[str]
    retries: int
    task_id: str

class LangGraphAdapter(ProviderAdapter):
    def __init__(self, model_name: str, max_tokens: int = 8192, max_response_length: int = 2048):
        if not os.environ.get("OPENROUTER_API_KEY"):
            raise ValueError("OPENROUTER_API_KEY environment variable not set")
        
        self.api_key = os.environ.get("OPENROUTER_API_KEY")
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.max_response_length = max_response_length
        self.base_url = 'https://openrouter.ai/api/v1'
        
        # Create logs directory if it doesn't exist
        self.logs_dir = Path("logs/langgraph_conversations")
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize the LLM with higher temperature for exploration
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=0.7,
            max_tokens=max_tokens,
            timeout=120,  # Increase timeout
            max_retries=3,  # Increase retries
            api_key=self.api_key,
            base_url=self.base_url
        )
        
        # Create the graph workflow
        self.workflow = self._create_workflow()
        print(f"Initializing LangGraph with model: {model_name}")

    def _extract_json_array(self, text: str) -> Optional[str]:
        """Extract a valid JSON array from text using multiple methods."""
        if not text:
            return None
            
        def is_valid_array(arr):
            """Check if array structure is valid for ARC."""
            try:
                if not isinstance(arr, list):
                    return False
                if not arr:  # Empty outer array is valid
                    return True
                if not all(isinstance(inner, list) for inner in arr):
                    return False
                return True
            except Exception:
                return False
        
        # Method 1: Direct JSON parsing
        try:
            text = text.strip()
            if text.startswith('```') and text.endswith('```'):
                text = text[3:-3].strip()
            if text.startswith('json'):
                text = text[4:].strip()
                
            parsed = json.loads(text)
            if is_valid_array(parsed):
                return json.dumps(parsed)
        except:
            pass
            
        # Method 2: Regex extraction
        try:
            matches = re.findall(r'\[\s*\[(?:[^\[\]]|\[(?:[^\[\]]|\[[^\[\]]*\])*\])*\]\s*\]', text)
            for match in matches:
                try:
                    parsed = json.loads(match)
                    if is_valid_array(parsed):
                        return match
                except:
                    continue
        except:
            pass
            
        # Method 3: Extract numbers and build array
        try:
            numbers = re.findall(r'\d+', text)
            if numbers:
                json_array = [[int(num) for num in numbers]]
                return json.dumps(json_array)
        except:
            pass
            
        return None

    def _should_continue(self, state: State) -> Union[Tuple[str, str], str]:
        """Determine if we should continue generating or end."""
        try:
            # Log current state
            self._log_conversation(state["task_id"], 
                f"Checking continuation:\nRetries: {state.get('retries', 0)}\nResponse length: {len(state['current_response'])}",
                "DEBUG")
            
            # Check if response is too short or invalid
            if len(state["current_response"]) < 5 or "sorry" in state["current_response"].lower():
                self._log_conversation(state["task_id"], 
                    "Response too short or invalid, retrying...",
                    "WARNING")
                if state.get("retries", 0) < 2:  # Allow 2 retries
                    state["retries"] = state.get("retries", 0) + 1
                    return ("continue", "generate")
                return END
            
            # Check if response is too long
            if len(state["current_response"]) > self.max_response_length:
                self._log_conversation(state["task_id"], 
                    f"Response too long ({len(state['current_response'])} chars), truncating...",
                    "WARNING")
                # Try to extract JSON from what we have
                json_array = self._extract_json_array(state["current_response"])
                if json_array:
                    state["final_json"] = json_array
                return END
            
            # Try to extract JSON array
            json_array = self._extract_json_array(state["current_response"])
            if json_array:
                state["final_json"] = json_array
                return END
                
            # Check if we've exceeded retries
            if state.get("retries", 0) >= 2:  # Allow 2 retries
                return END
                
            # Continue with retry
            state["retries"] = state.get("retries", 0) + 1
            return ("continue", "generate")
            
        except Exception as e:
            self._log_conversation(state["task_id"], 
                f"Error in _should_continue:\n{str(e)}\nTraceback:\n{traceback.format_exc()}",
                "ERROR")
            return END

    def _create_workflow(self) -> Any:
        """Create and compile the LangGraph workflow."""
        # Create graph
        workflow = StateGraph(State)

        # Add generation node
        workflow.add_node("generate", self._generate)
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "generate",
            self._should_continue,
            {
                ("continue", "generate"): "generate",  # Map tuple to node name
                END: END
            }
        )
        
        # Set entry point
        workflow.set_entry_point("generate")
        
        # Compile and return the compiled workflow
        return workflow.compile()

    def _generate(self, state: State) -> State:
        """Generate a response using the LLM."""
        try:
            # Get response from LLM
            response = self.llm.invoke(state["messages"])
            content = response.content if hasattr(response, 'content') else str(response)
            
            # Update state
            state["current_response"] = content
            self._log_conversation(state["task_id"], f"Raw model response:\n{content}", "ASSISTANT")
            
            return state
            
        except Exception as e:
            self._log_conversation(state["task_id"], 
                f"Error in _generate:\n{str(e)}\nTraceback:\n{traceback.format_exc()}",
                "ERROR")
            state["current_response"] = "[[]]"  # Set empty response on error
            return state

    def _log_conversation(self, task_id: str, message: str, message_type: str = "INFO"):
        """Log conversation to a file."""
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        log_file = self.logs_dir / f"{task_id}_{timestamp}.log"
        
        with open(log_file, "a", encoding='utf-8') as f:
            f.write(f"\n{'='*80}\n")
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} [{message_type}]\n")
            f.write(f"{message}\n")
            f.flush()  # Force write to disk

    def make_prediction(self, prompt: str) -> str:
        """Make a prediction with the LangGraph-enhanced model."""
        task_match = re.search(r"task (\w+)", prompt.lower())
        task_id = task_match.group(1) if task_match else time.strftime("%Y%m%d_%H%M%S")
        
        # Log the start of a new task
        self._log_conversation(task_id, f"Starting new task: {task_id}", "START")
        self._log_conversation(task_id, f"Prompt:\n{prompt}", "PROMPT")
        
        messages = [
            SystemMessage(content="""You are solving an ARC (Abstraction and Reasoning Corpus) task.
IMPORTANT: Your ENTIRE response must be a single JSON array. NO explanations, NO code, NO markdown.

Examples of valid responses:
[[1,2,3], [4,5,6]]
[[0,0], [1,1]]
[[8]]

RULES:
1. Think carefully about the pattern
2. Consider all examples thoroughly
3. But do NOT write any explanations
4. Do NOT write any code
5. Do NOT use markdown
6. Output ONLY the final JSON array
7. NO text before or after the array
8. NO comments or descriptions
9. ONLY the array itself

STOP IMMEDIATELY after outputting the array. Do not add ANY additional text."""),
            HumanMessage(content=f"Output ONLY a JSON array solution for this task:\n{prompt}")
        ]
        
        # Initialize the state
        state = State(
            messages=messages,
            next_step="generate",
            current_response="",
            final_json=None,
            retries=0,
            task_id=task_id
        )
        
        try:
            # Run the graph
            self._log_conversation(task_id, "Running workflow...", "DEBUG")
            result = self.workflow.invoke(state)
            self._log_conversation(task_id, f"Workflow result: {result}", "DEBUG")
            
            # Try to extract JSON from the response
            if result.get("current_response"):
                # First try to find a JSON array at the start
                content = result["current_response"].strip()
                if content.startswith("["):
                    # Try to extract just the array part
                    try:
                        array_end = content.rindex("]") + 1
                        json_str = content[:array_end]
                        parsed = json.loads(json_str)
                        if isinstance(parsed, list):
                            self._log_conversation(task_id, f"Found JSON at start: {json_str}", "SUCCESS")
                            return json_str
                    except:
                        pass
                
                # If that fails, try our normal extraction
                json_array = self._extract_json_array(result["current_response"])
                if json_array:
                    self._log_conversation(task_id, f"Found JSON: {json_array}", "SUCCESS")
                    return json_array
            
            self._log_conversation(task_id, "No valid JSON found, returning empty array", "WARNING")
            return "[[]]"
            
        except Exception as e:
            self._log_conversation(task_id, 
                f"Error in make_prediction:\n{str(e)}\nTraceback:\n{traceback.format_exc()}",
                "ERROR")
            return "[[]]"

    def chat_completion(self, messages: List[Dict[str, str]], tools: List = None) -> str:
        """Not implemented for LangGraph adapter."""
        raise NotImplementedError("Chat completion not implemented for LangGraph adapter")

    def extract_json_from_response(self, input_response: str) -> List[List[int]]:
        """Extract and format the JSON response."""
        try:
            # Try to extract JSON array using our helper method
            json_array = self._extract_json_array(input_response)
            if json_array:
                # Parse the JSON string back to a list
                parsed = json.loads(json_array)
                if isinstance(parsed, list):
                    return parsed
        except Exception as e:
            print(f"Error extracting JSON: {str(e)}")
            traceback.print_exc()
        
        # Return empty array as fallback
        return [[]]
