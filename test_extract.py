import json

# Load the results.json file
with open('results/claude-3-5-haiku/results.json') as f:
    data = json.load(f)

# Extract score 1 IDs from task_results
score_1_ids = [task_id for task_id, score in data['task_results'].items() if score == 1.0]

print(f"Found {len(score_1_ids)} score 1 IDs:")
print(score_1_ids)
