import json
import os
from datetime import datetime

# Data models for tasks, users, etc.

# File paths for storing tasks
TEAM_TASKS_FILE = os.path.join(os.path.dirname(__file__), 'data', 'team_tasks.json')
MANAGER_TASKS_FILE = os.path.join(os.path.dirname(__file__), 'data', 'manager_tasks.json')
MY_TASKS_FILE = os.path.join(os.path.dirname(__file__), 'data', 'my_tasks.json')

# Ensure data directory exists
os.makedirs(os.path.join(os.path.dirname(__file__), 'data'), exist_ok=True)

def save_tasks(tasks, file_path):
    """Save tasks to a JSON file"""
    # Convert datetime objects to strings for JSON serialization
    serializable_tasks = []
    for task in tasks:
        task_copy = task.copy()
        serializable_tasks.append(task_copy)
    
    with open(file_path, 'w') as f:
        json.dump(serializable_tasks, f, indent=2)

def load_tasks(file_path):
    """Load tasks from a JSON file"""
    if not os.path.exists(file_path):
        return []
    
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        # Return empty list if file is empty or doesn't exist
        return []
