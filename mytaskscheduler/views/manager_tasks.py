from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime, date
from ..models import save_tasks, load_tasks, MANAGER_TASKS_FILE
from ..email_utils import send_email_reminder, check_due_tasks

bp = Blueprint('manager_tasks', __name__, url_prefix='/managers')

# Load tasks from file
def get_manager_tasks():
    return load_tasks(MANAGER_TASKS_FILE)

def save_manager_tasks(tasks):
    save_tasks(tasks, MANAGER_TASKS_FILE)
    
def get_next_id():
    tasks = get_manager_tasks()
    if not tasks:
        return 1
    return max(task['id'] for task in tasks) + 1

@bp.route('/')
def manager_dashboard():
    query = request.args.get('q', '').lower()
    today = date.today()
    all_tasks = get_manager_tasks()
    filtered_tasks = []
    
    for task in all_tasks:
        # Overdue logic
        if task['status'] != 'Completed' and task['due_date'] < today.strftime('%Y-%m-%d'):
            task['status'] = 'Overdue'
        # Search filter
        if query:
            if (query in task['title'].lower() or 
                query in task['description'].lower() or 
                query in task['assignee'].lower() or 
                query in (task.get('tags','').lower())):
                filtered_tasks.append(task)
        else:
            filtered_tasks.append(task)
    
    # Check if any tasks need reminders
    due_tasks = check_due_tasks(all_tasks)
    for task in due_tasks:
        send_email_reminder(task, f"{task['assignee']}@example.com")
    
    # Save any status changes
    save_manager_tasks(all_tasks)
            
    return render_template('manager_dashboard.html', tasks=filtered_tasks)

@bp.route('/add', methods=['GET', 'POST'])
def add_task():
    if request.method == 'POST':
        task = {
            'id': get_next_id(),
            'title': request.form['title'],
            'description': request.form['description'],
            'assignee': request.form['assignee'],
            'due_date': request.form['due_date'],
            'status': 'Pending',
            'priority': request.form.get('priority', 'Normal'),
            'tags': request.form.get('tags', ''),
        }
        tasks = get_manager_tasks()
        tasks.append(task)
        save_manager_tasks(tasks)
        return redirect(url_for('manager_tasks.manager_dashboard'))
    return render_template('add_manager_task.html')

@bp.route('/complete/<int:task_id>')
def complete_task(task_id):
    tasks = get_manager_tasks()
    for task in tasks:
        if task['id'] == task_id:
            task['status'] = 'Completed'
            break
    save_manager_tasks(tasks)
    return redirect(url_for('manager_tasks.manager_dashboard'))
