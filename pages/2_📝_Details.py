import streamlit as st
import pandas as pd

st.title("Model Test Details")

import os
import json
from pathlib import Path

def get_overall_scores():
    """Extract overall scores and IDs with score 1 from all results.json files"""
    scores = {}
    
    # Look for results.json in both 'results' and 'submissions' directories
    search_dirs = ['results', 'submissions']
    
    for base_dir in search_dirs:
        if os.path.exists(base_dir):
            for model_dir in os.listdir(base_dir):
                full_path = os.path.join(base_dir, model_dir)
                if os.path.isdir(full_path):
                    # Look for results.json in the directory
                    json_file = Path(full_path) / 'results.json'
                    if json_file.exists():
                        try:
                            with open(json_file) as f:
                                data = json.load(f)
                                # Handle different JSON structures
                                if isinstance(data, dict):
                                    if "score" in data and "total_tasks" in data:
                                        score_1_ids = []
                                        if "task_results" in data:
                                            score_1_ids = [task_id for task_id, score in data["task_results"].items() if score == 1.0]
                                        scores[model_dir] = {
                                            "score": data["score"],
                                            "total_tasks": data["total_tasks"],
                                            "score_1_ids": score_1_ids
                                        }
                                elif isinstance(data, list) and len(data) > 0:
                                    # Try first element if it's a list
                                    first_item = data[0]
                                    if isinstance(first_item, dict) and "score" in first_item and "total_tasks" in first_item:
                                        score_1_ids = []
                                        if "task_results" in first_item:
                                            score_1_ids = [task_id for task_id, score in first_item["task_results"].items() if score == 1.0]
                                        scores[model_dir] = {
                                            "score": first_item["score"],
                                            "total_tasks": first_item["total_tasks"],
                                            "score_1_ids": score_1_ids
                                        }
                        except json.JSONDecodeError:
                            continue  # Skip invalid JSON files
    return scores

# Get all scores
scores = get_overall_scores()

# Generate scoreboard visualization at the top
st.subheader("Scoreboard Visualization")

# Get all unique test IDs across models and count filled cells
test_id_counts = {}
for model_data in scores.values():
    for test_id in model_data["score_1_ids"]:
        test_id_counts[test_id] = test_id_counts.get(test_id, 0) + 1

# Sort test IDs by number of filled cells (descending), then by ID
sorted_test_ids = sorted(test_id_counts.keys(), 
                        key=lambda x: (-test_id_counts[x], x))

# Add remaining test IDs that have no filled cells
all_test_ids = sorted_test_ids + sorted(set(test_id_counts.keys()).symmetric_difference(test_id_counts.keys()))

# Create a grid showing which models scored on which tests
grid_data = []
for model, data in sorted(scores.items(), key=lambda x: x[0].lower()):  # Sort alphabetically by model name
    row = [model] + ['█' if test_id in data["score_1_ids"] else '░' for test_id in all_test_ids]
    grid_data.append(row)

# Format test IDs vertically for column headers
vertical_test_ids = [f"{id}\n" for id in all_test_ids]

# Create DataFrame for visualization
df = pd.DataFrame(grid_data, columns=['Model'] + vertical_test_ids)

# Create grid layout for checkboxes
st.subheader("Select Models to Display")
cols = st.columns(5)  # Create 5 columns
model_states = {}
models = sorted(scores.keys(), key=lambda x: x.lower())  # Sort alphabetically

# Distribute checkboxes across columns
for i, model in enumerate(models):
    with cols[i % 5]:  # Cycle through columns
        model_states[model] = st.checkbox(model, value=False, key=f"show_{model}")

# Filter dataframe based on toggles
filtered_df = df[df['Model'].isin([model for model, show in model_states.items() if show])]

# Create a container for the scoreboard
scoreboard_container = st.container()

# Split into two columns: fixed and scrollable
fixed_col, scroll_col = scoreboard_container.columns([1, 4])

# Display model names and scores in fixed column
with fixed_col:
    st.markdown("<div style='height: 35px;'></div>", unsafe_allow_html=True)  # Spacer for header
    for model in filtered_df['Model']:
        # Get the score for this model
        score = scores[model]['score']
        st.markdown(
            f"<div style='height: 35px; line-height: 35px;'>{model} - {score}</div>", 
            unsafe_allow_html=True
        )

# Display the grid in scrollable column
with scroll_col:
    # Remove model column since we're showing it separately
    grid_df = filtered_df.drop(columns=['Model'])
    
    st.dataframe(
        grid_df.style
        .set_properties(**{
            'font-size': '9pt',
            'text-align': 'center',
            'color': 'black',
            'font-family': 'monospace',
            'border': '1px solid #ddd'
        })
        .map(lambda x: 'background-color: #e6f4ea' if x == '█' else 'background-color: #f8f9fa')
        .set_properties(**{'color': 'black'})
        .set_table_styles([
            {
                'selector': 'th',
                'props': [
                    ('background-color', '#f0f0f0'),
                    ('color', 'black'),
                    ('font-weight', 'bold'),
                    ('font-size', '10pt'),
                    ('border', '1px solid #ddd')
                ]
            },
            {
                'selector': 'th.col_heading',
                'props': [
                    ('writing-mode', 'vertical-rl'),
                    ('transform', 'rotate(180deg)'),
                    ('text-align', 'left'),
                    ('white-space', 'nowrap'),
                    ('height', '150px')
                ]
            }
        ]),
        use_container_width=True,
        width=None,
        height=(len(filtered_df) + 1) * 35 + 3
    )

# Show score 1 IDs for each model below the scoreboard
st.subheader("Test IDs with Score 1")

# Create a grid layout for test IDs with smaller font
for model, data in sorted(scores.items(), key=lambda x: x[0].lower()):  # Sort alphabetically by model name
    if data["score_1_ids"]:
        st.markdown(f"<p style='font-size:10px;'><b>{model}</b></p>", unsafe_allow_html=True)
        # Create columns for the grid with 20 columns and unlimited rows
        cols = st.columns(20)
        # Distribute test IDs across columns with unlimited rows
        for i, test_id in enumerate(data["score_1_ids"]):
            with cols[i % 20]:
                st.markdown(f"<p style='font-size:8px; margin:0; padding:0;'><code>{test_id}</code></p>", unsafe_allow_html=True)
    else:
        st.markdown(f"<p style='font-size:10px;'><b>{model}</b>: No tests with score 1</p>", unsafe_allow_html=True)
