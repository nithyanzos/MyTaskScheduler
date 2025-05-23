from flask import Flask, render_template
from datetime import datetime, timedelta
from .models import load_tasks, TEAM_TASKS_FILE, MANAGER_TASKS_FILE, MY_TASKS_FILE

app = Flask(__name__)

from .views import team_tasks, manager_tasks, my_tasks

app.register_blueprint(team_tasks.bp)
app.register_blueprint(manager_tasks.bp)
app.register_blueprint(my_tasks.bp)

@app.route('/')
def index():
    # Get today and tomorrow dates for comparison
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)
    today_str = today.strftime('%Y-%m-%d')
    tomorrow_str = tomorrow.strftime('%Y-%m-%d')
    
    # Count active tasks in each category
    team_tasks_data = load_tasks(TEAM_TASKS_FILE)
    manager_tasks_data = load_tasks(MANAGER_TASKS_FILE)
    my_tasks_data = load_tasks(MY_TASKS_FILE)
    
    # Filter for active tasks (not completed and must have a non-empty, non-whitespace title)
    active_team_tasks = len([t for t in team_tasks_data if t.get('status') != 'Completed' and t.get('title') and t.get('title').strip()])
    active_manager_tasks = len([t for t in manager_tasks_data if t.get('status') != 'Completed' and t.get('title') and t.get('title').strip()])
    active_my_tasks = len([t for t in my_tasks_data if t.get('status') != 'Completed' and t.get('title') and t.get('title').strip()])
    
    # Get upcoming deadlines
    all_tasks = team_tasks_data + manager_tasks_data + my_tasks_data
    upcoming_tasks = sorted(
        [t for t in all_tasks if t.get('status') != 'Completed'],
        key=lambda x: x.get('due_date', '9999-12-31')
    )[:3]  # Get the 3 most urgent tasks
    
    # Calculate how many tasks are due today
    tasks_due_today = len([t for t in all_tasks if t.get('due_date') == today_str and t.get('status') != 'Completed'])
    
    return render_template('index.html', 
                          team_count=active_team_tasks,
                          manager_count=active_manager_tasks,
                          my_count=active_my_tasks,
                          upcoming_tasks=upcoming_tasks,
                          today_str=today_str,
                          tomorrow_str=tomorrow_str,
                          tasks_due_today=tasks_due_today)
