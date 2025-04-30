from typing import List
from pydantic import BaseModel
import matplotlib.pyplot as plt
import matplotlib
from typing import List
import os
# Step 1: Define the Pydantic model

class ClosenessData(BaseModel):
    survey_name: str
    category: str
    user_id: int
    user_name: str
    closeness_centrality: float

def generate_graph(graph_data: List[ClosenessData]):
    matplotlib.use('Agg')
    filename: str = "output.png"
    user_names = [entry.user_name for entry in graph_data]
    centrality_values = [entry.closeness_centrality for entry in graph_data]

    # Create the bar chart
    plt.figure(figsize=(12, 6))
    bars = plt.bar(user_names, centrality_values, color='skyblue')

    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, yval + 0.01, f"{yval:.2f}", ha='center', va='bottom', fontsize=9)

    plt.xticks(rotation=45, ha='right')
    plt.ylabel('Closeness Centrality')
    plt.title('Closeness Centrality by User')
    plt.tight_layout()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    plt.savefig(filename)
    plt.close()
    print(f"Graph saved as {filename}")

    try:
        if os.name == 'nt':  # Windows
            os.startfile(filename)
        elif os.name == 'posix':
            # macOS
            if subprocess.call(['which', 'open'], stdout=subprocess.DEVNULL) == 0:
                subprocess.Popen(['open', filename])
            # Linux
            elif subprocess.call(['which', 'xdg-open'], stdout=subprocess.DEVNULL) == 0:
                subprocess.Popen(['xdg-open', filename])
            else:
                print("No compatible viewer found to open the file.")
    except Exception as e:
        print(f"Could not open file automatically: {e}")

    return "Graph has been generated and opened"
