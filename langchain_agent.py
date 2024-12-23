from src.adapters import LangGraphAdapter

def test_langgraph():
    # Initialize the adapter
    adapter = LangGraphAdapter("qwen/qwq-32b-preview")
    
    # Test with a simple ARC-style prompt
    prompt = """
    Input grid 1:
    0 0 0
    0 1 0
    0 0 0
    
    Output grid 1:
    1 1 1
    1 1 1
    1 1 1
    
    Input grid 2:
    0 0 0 0
    0 1 1 0
    0 0 0 0
    
    Output grid 2:
    1 1 1 1
    1 1 1 1
    1 1 1 1
    
    Input grid 3:
    0 0 0
    0 1 0
    0 1 0
    
    Output grid 3:
    ?
    """
    
    # Make prediction
    response = adapter.make_prediction(prompt)
    print("\nTest Prompt:")
    print("-" * 80)
    print(prompt)
    print("\nModel Response:")
    print("-" * 80)
    print(response)

if __name__ == "__main__":
    test_langgraph()
