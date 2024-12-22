from .provider import ProviderAdapter
from src.models import ARCTaskOutput
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
from typing import List
load_dotenv()

class GoogleAdapter(ProviderAdapter):
    def __init__(self, model_name: str, max_tokens: int = 4024):
        self.model = self.init_model(model_name)
        self.model_name = model_name
        self.max_tokens = max_tokens

    def init_model(self, model_name: str):
        """
        Initialize the Google Gemini model
        """
        if not os.environ.get("GEMINI_API_KEY"):
            raise ValueError("GEMINI_API_KEY not found in environment variables")

        genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
        model = genai.GenerativeModel(model_name)
        return model
    
    def make_prediction(self, prompt: str) -> str:
        """
        Make a prediction with the Google model
        """
        response = self.model.generate_content(prompt)
        return response.text

    def chat_completion(self, messages, tools=[]) -> str:
        # Convert messages to the format expected by Gemini
        chat = self.model.start_chat()
        for message in messages:
            if message["role"] == "user":
                response = chat.send_message(message["content"])
        return response

    def extract_json_from_response(self, input_response: str) -> List[List[int]]:
        """
        Extract JSON array from the response string
        """
        prompt = f"""
        Extract the 2D array of integers from this text. Return ONLY the array, nothing else.
        If there are multiple arrays, return only the first one.
        
        Text: {input_response}
        """
        
        response = self.make_prediction(prompt)
        
        # Try to find array pattern and parse it
        try:
            # Find the first occurrence of a pattern that looks like a 2D array
            start_idx = response.find("[[")
            end_idx = response.find("]]") + 2
            if start_idx != -1 and end_idx != -1:
                array_str = response[start_idx:end_idx]
                return json.loads(array_str)
            return None
        except json.JSONDecodeError:
            return None

if __name__ == "__main__":
    adapter = GoogleAdapter("gemini-2.0-flash-exp")
    print(type(adapter.extract_json_from_response("[[1, 2, 3], [4, 5, 6]]")))
