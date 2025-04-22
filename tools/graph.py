from typing import List
from pydantic import BaseModel
import matplotlib.pyplot as plt
from typing import List
from pydantic import TypeAdapter
import os
# Step 1: Define the Pydantic model
class ClosenessData(BaseModel):
    survey_name: str
    category: str
    user_id: int
    user_name: str
    closeness_centrality: float

# Step 2: Plot and Save Function
def generate_graph(graph_data: List[ClosenessData]):
    filename: str = "closeness_centrality.png"
    user_names = [entry.user_name for entry in graph_data]
    centrality_values = [entry.closeness_centrality for entry in graph_data]

    # Create the bar chart
    plt.figure(figsize=(12, 6))
    bars = plt.bar(user_names, centrality_values, color='skyblue')

    # Add data labels on top of the bars
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, yval + 0.01, f"{yval:.2f}", ha='center', va='bottom', fontsize=9)

    # Set chart labels and title
    plt.xticks(rotation=45, ha='right')
    plt.ylabel('Closeness Centrality')
    plt.title('Closeness Centrality by User')
    plt.tight_layout()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Save the graph as a PNG file
    plt.savefig(filename)
    plt.close()
    
    print(f"Graph saved as {filename}")

    # Open the file after saving
    if os.name == 'nt':  # If the OS is Windows
        os.startfile(filename)
    elif os.name == 'posix':  # If the OS is macOS or Linux
        try:
            os.system(f'open {filename}')  # macOS
        except Exception:
            os.system(f'xdg-open {filename}')  # Linux

    return "Graph has been generated and opened"

raw_data = [
    {"survey_name": "Network Survey", "category": "Operations", "user_id": 1, "user_name": "Caroline Caulfield", "closeness_centrality": 0.22},
    {"survey_name": "Network Survey", "category": "Operations", "user_id": 8, "user_name": "Daisy Proctor", "closeness_centrality": 0.22},
    {"survey_name": "Network Survey", "category": "Operations", "user_id": 11, "user_name": "Anj Meaklim", "closeness_centrality": 0.11},
    {"survey_name": "Network Survey", "category": "Operations", "user_id": 13, "user_name": "Henry Satterthwaite", "closeness_centrality": 0.22},
    {"survey_name": "Network Survey", "category": "Operations", "user_id": 15, "user_name": "Cory Eisentraut", "closeness_centrality": 0.22},
    {"survey_name": "Network Survey", "category": "Operations", "user_id": 17, "user_name": "Fernando Desouches", "closeness_centrality": 0.15},
    {"survey_name": "Network Survey", "category": "Operations", "user_id": 23, "user_name": "Alex Meaklim", "closeness_centrality": 0.0},
    {"survey_name": "Network Survey", "category": "Operations", "user_id": 24, "user_name": "Izzy Dry", "closeness_centrality": 0.0},
    {"survey_name": "Network Survey", "category": "Operations", "user_id": 27, "user_name": "Becky Savoury", "closeness_centrality": 0.0},
    {"survey_name": "Network Survey", "category": "Operations", "user_id": 30, "user_name": "Holly Reynolds", "closeness_centrality": 0.0}
]

# Parse into data models
# adapter = TypeAdapter(List[ClosenessData])
# parsed_data = adapter.validate_python(raw_data)
# plot_and_save_closeness_centrality(parsed_data)