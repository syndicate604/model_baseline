import json
import os
from typing import List
import requests
from src.adapters.provider import ProviderAdapter
from dotenv import load_dotenv

load_dotenv()

class OpenRouterAdapter(ProviderAdapter):
    def __init__(self, model_name: str, max_tokens: int = 4024):
        if not os.environ.get("OPENROUTER_API_KEY"):
            raise ValueError("OPENROUTER_API_KEY environment variable not set")
        self.api_key = os.environ.get("OPENROUTER_API_KEY")
        self.model_name = model_name
        self.max_tokens = max_tokens
        print(f"Initializing OpenRouter with model: {model_name}")

    def make_prediction(self, prompt: str) -> str:
        """
        Make a prediction with the OpenRouter model
        """
        messages = [
            {"role": "system", "content": "You are a pattern recognition expert. Your ONLY task is to output a JSON array representing the solution. You must ONLY output the array in the format [[x,y,z], [a,b,c], ...] with NO explanation, NO reasoning, and NO additional text. Any explanation or additional text will cause a failure."},
            {"role": "user", "content": f"Based on the examples below, be consise, output ONLY a JSON array solution:\n{prompt}"}
        ]
        print(f"\nPrompt: {messages[1]['content'][:200]}...\n")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/arcprizeorg/model_baseline",
            "X-Title": "Model Baseline Testing"
        }
        
        data = {
            "model": self.model_name,
            "messages": messages,
            "max_tokens": self.max_tokens,
            "temperature": 1.2,
            "stream": False
        }
        
        print("\nRequest parameters:")
        print(json.dumps({"headers": {k:v for k,v in headers.items() if k != "Authorization"}, 
                         "data": data}, indent=2))
        print("\nResponse:")
        print("-" * 80)
        
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data,
                stream=False
            )
            response.raise_for_status()
            result = response.json()
            if result.get('choices') and result['choices'][0].get('message', {}).get('content'):
                return result['choices'][0]['message']['content']
            return ""
                
        except Exception as e:
            print(f"\nException during request: {str(e)}")
            return ""

    def chat_completion(self, messages, tools=[]) -> str:
        return self.make_prediction(messages[0]['content'])

    def extract_json_from_response(self, input_response: str) -> List[List[int]]:
        print("\nModel Response:")
        print("-" * 80)
        print(input_response)
        print("-" * 80)
        return input_response