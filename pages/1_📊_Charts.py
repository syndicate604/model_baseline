import streamlit as st
import matplotlib.pyplot as plt

st.title("Model Performance Charts")

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
                                        scores[model_dir] = {
                                            "score": data["score"],
                                            "total_tasks": data["total_tasks"],
                                            "score_1_ids": []
                                        }
                                elif isinstance(data, list) and len(data) > 0:
                                    # Try first element if it's a list
                                    first_item = data[0]
                                    if isinstance(first_item, dict) and "score" in first_item and "total_tasks" in first_item:
                                        scores[model_dir] = {
                                            "score": first_item["score"],
                                            "total_tasks": first_item["total_tasks"],
                                            "score_1_ids": []
                                        }
                        except json.JSONDecodeError:
                            continue  # Skip invalid JSON files
    return scores

# Get all scores
scores = get_overall_scores()

# Create horizontal bar chart
if scores:
    fig, ax = plt.subplots(figsize=(5, len(scores) * 0.25))
    
    # Sort by score descending
    sorted_scores = sorted(scores.items(), key=lambda x: x[1]["score"], reverse=True)
    
    # Extract data for plotting
    names = [name for name, _ in sorted_scores]
    values = [data["score"] for _, data in sorted_scores]
    
    # Create horizontal bars
    y_pos = range(len(names))
    ax.barh(y_pos, values, color='skyblue')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(names, fontsize=8)
    ax.set_xlabel("Score", fontsize=9)
    ax.set_title("Model Performance Summary", fontsize=10)
    
    # Add score values at the end of each bar
    for i, v in enumerate(values):
        ax.text(v + 1, i, f"{v:.1f}", color='black', va='center', fontsize=8)
    
    st.pyplot(fig)
else:
    st.warning("No data available for charts")
