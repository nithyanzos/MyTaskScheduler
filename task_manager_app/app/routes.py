from flask import render_template, url_for, flash, redirect, request, current_app
from task_manager_app.app import app, db
from task_manager_app.app.models import User, Category, Task, RecurringTaskPattern, ProcessDocument # Import ProcessDocument
from task_manager_app.app.forms import (
    RegistrationForm, EditUserForm, CategoryForm, 
    CreateTaskForm, EditTaskForm, CreateRecurringTaskForm, ProcessDocumentForm # Import ProcessDocumentForm
)
from task_manager_app.app.email_utils import send_email
from task_manager_app.app.recurring_tasks_logic import generate_tasks_for_pattern
from datetime import date, timedelta, datetime # Import datetime
from sqlalchemy import or_ 

@app.route('/')
@app.route('/index')
def index():
    return "Welcome to the Task Manager App!"

# User Management Routes
@app.route('/admin/users/add', methods=['GET', 'POST'])
def add_user():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data, 
            email=form.email.data, 
            role=form.role.data,
            manager=form.reports_to.data # Assign the manager
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('User added successfully!', 'success')
        return redirect(url_for('list_users'))
    return render_template('add_user.html', title='Add User', form=form)

@app.route('/admin/users')
def list_users():
    users = User.query.all()
    return render_template('users.html', title='Manage Users', users=users)

@app.route('/admin/users/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = EditUserForm(obj=user) 
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.role = form.role.data
        user.manager = form.reports_to.data # Update the manager
        # Add password change logic here if included in form
        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('list_users'))
    return render_template('edit_user.html', title='Edit User', form=form, user_id=user_id)

@app.route('/admin/users/delete/<int:user_id>', methods=['POST']) # Changed to POST for better practice
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    # Add logic here to handle tasks assigned to user if necessary
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('list_users'))

# Category Management Routes
@app.route('/categories/add', methods=['GET', 'POST'])
def add_category():
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(name=form.name.data)
        db.session.add(category)
        db.session.commit()
        flash('Category added successfully!', 'success')
        return redirect(url_for('list_categories'))
    return render_template('categories/add_category.html', title='Add Category', form=form)

@app.route('/categories')
def list_categories():
    categories = Category.query.all()
    return render_template('categories/list_categories.html', title='Manage Categories', categories=categories)

# Task Management Routes
@app.route('/tasks/create', methods=['GET', 'POST'])
def create_task():
    form = CreateTaskForm()
    if form.validate_on_submit():
        task = Task(
            title=form.title.data,
            description=form.description.data,
            due_date=form.due_date.data,
            priority=form.priority.data,
            category=form.category.data,
            assignee=form.assigned_to.data,
            # created_by_user_id will be set once auth is implemented
            # For now, let's assume current_user.id if login is implemented, or leave as nullable
        )
        db.session.add(task)
        db.session.commit() # Commit to get task.id for the email
        
        if task.assignee:
            try:
                send_email(
                    to=task.assignee.email,
                    subject=f"New Task Assigned: {task.title}",
                    template_name_or_body='email/task_assigned_email.html',
                    user=task.assignee,
                    task=task
                )
                flash('Task created successfully and notification sent!', 'success')
            except Exception as e:
                current_app.logger.error(f"Failed to send email for new task {task.id}: {e}")
                flash('Task created successfully, but failed to send notification email.', 'warning')
        else:
            flash('Task created successfully!', 'success')
            
        return redirect(url_for('list_tasks'))
    return render_template('tasks/create_task.html', title='Create Task', form=form)

@app.route('/tasks')
def list_tasks():
    query = request.args.get('q')
    if query:
        tasks = Task.query.filter(
            or_(
                Task.title.ilike(f'%{query}%'),
                Task.description.ilike(f'%{query}%')
            )
        ).all()
    else:
        tasks = Task.query.all()
    return render_template('tasks/list_tasks.html', title='Tasks', tasks=tasks, search_query=query)

@app.route('/tasks/edit/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    original_assignee_id = task.assigned_to_user_id
    form = EditTaskForm(obj=task)
    
    if form.validate_on_submit():
        task.title = form.title.data
        task.description = form.description.data
        task.due_date = form.due_date.data
        task.priority = form.priority.data
        task.status = form.status.data
        task.category = form.category.data
        task.assignee = form.assigned_to.data # This is the User object from QuerySelectField
        
        db.session.commit() # Commit changes to the task
        
        new_assignee_id = task.assigned_to_user_id
        
        email_sent_or_attempted = False
        if task.assignee and (new_assignee_id != original_assignee_id or (request.form.get('notify_update') == 'true')): # Also check if user wants to re-notify
            try:
                email_subject = f"Task Updated: {task.title}"
                if new_assignee_id != original_assignee_id:
                    email_subject = f"New Task Assignment: {task.title}" # Or different subject if re-assigned
                
                send_email(
                    to=task.assignee.email,
                    subject=email_subject,
                    template_name_or_body='email/task_updated_email.html', # Or task_assigned_email if re-assigned
                    user=task.assignee,
                    task=task
                )
                flash('Task updated successfully and notification sent!', 'success')
                email_sent_or_attempted = True
            except Exception as e:
                current_app.logger.error(f"Failed to send email for updated task {task.id}: {e}")
                flash('Task updated successfully, but failed to send notification email.', 'warning')
                email_sent_or_attempted = True
        
        if not email_sent_or_attempted:
            flash('Task updated successfully!', 'success')
            
        return redirect(url_for('list_tasks'))
        
    return render_template('tasks/edit_task.html', title='Edit Task', form=form, task_id=task_id)

@app.route('/tasks/delete/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('list_tasks'))

@app.route('/tasks/update_status/<int:task_id>', methods=['POST'])
def update_task_status(task_id):
    task = Task.query.get_or_404(task_id)
    new_status = request.form.get('status')
    if new_status:
        task.status = new_status
        db.session.commit()
        flash('Task status updated successfully!', 'success')
    else:
        flash('No status provided.', 'danger')
    return redirect(url_for('list_tasks'))

# "My Tasks" View
@app.route('/my_tasks/<int:user_id>')
def my_tasks(user_id):
    user = User.query.get_or_404(user_id)
    # Assuming a user can only see their own tasks unless they are a manager/admin
    # For now, this just shows tasks assigned to the user_id in the URL
    tasks = Task.query.filter_by(assignee=user).order_by(Task.due_date.asc()).all()
    return render_template('tasks/my_tasks.html', title=f'My Tasks for {user.username}', tasks=tasks, user=user)

# "Manager View"
@app.route('/manager_view/<int:manager_id>')
def manager_view(manager_id):
    manager = User.query.get_or_404(manager_id)
    if manager.role not in ['manager', 'admin']: # Admins can also be managers
        flash(f'User {manager.username} does not have manager privileges.', 'warning')
        return redirect(url_for('list_users')) # Or redirect to index or their own tasks

    direct_reports = manager.direct_reports.all()
    if not direct_reports:
        flash(f'{manager.username} has no direct reports.', 'info')
        tasks = []
    else:
        report_ids = [report.id for report in direct_reports]
        tasks = Task.query.filter(Task.assigned_to_user_id.in_(report_ids)).order_by(Task.due_date.asc()).all()

    return render_template('tasks/manager_view.html', 
                           title=f'Tasks Managed by {manager.username}', 
                           tasks=tasks, 
                           manager=manager, 
                           direct_reports=direct_reports)

# Recurring Task Routes
@app.route('/recurring_tasks/create', methods=['GET', 'POST'])
def create_recurring_task():
    form = CreateRecurringTaskForm()
    if form.validate_on_submit():
        pattern = RecurringTaskPattern(
            base_task_title=form.base_task_title.data,
            base_task_description=form.base_task_description.data,
            base_task_priority=form.base_task_priority.data,
            base_task_category=form.base_task_category.data, # This is an object
            assigned_to_user=form.assigned_to.data,         # This is an object
            recurrence_rule=form.recurrence_rule.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            # created_by_user_id will be set once auth is implemented
            # For now, assuming it's nullable or set to a default user if any
        )
        db.session.add(pattern)
        db.session.commit() # Commit to get pattern.id

        # Generate initial tasks for the next 60 days
        try:
            generate_tasks_for_pattern(pattern.id, upto_date=date.today() + timedelta(days=60))
            flash('Recurring task pattern created and initial tasks generated!', 'success')
        except Exception as e:
            current_app.logger.error(f"Error generating initial tasks for pattern {pattern.id}: {e}")
            flash('Recurring task pattern created, but failed to generate initial tasks.', 'warning')
            
        return redirect(url_for('list_recurring_tasks'))
    return render_template('recurring/create_recurring.html', title='Define Recurring Task', form=form)

@app.route('/recurring_tasks')
def list_recurring_tasks():
    patterns = RecurringTaskPattern.query.all()
    return render_template('recurring/list_recurring.html', title='Recurring Task Patterns', patterns=patterns)

@app.route('/recurring_tasks/delete/<int:pattern_id>', methods=['POST'])
def delete_recurring_task(pattern_id):
    pattern = RecurringTaskPattern.query.get_or_404(pattern_id)
    
    # Optional: Delete future, non-completed tasks generated by this pattern
    # tasks_to_delete = Task.query.filter(
    #     Task.title == pattern.base_task_title, # A simple way to link, better with foreign key
    #     Task.is_recurring == True,
    #     Task.status != 'Completed',
    #     Task.due_date >= datetime.combine(date.today(), datetime.min.time()) 
    # ).all()
    # for task in tasks_to_delete:
    #    db.session.delete(task)
    
    db.session.delete(pattern)
    db.session.commit()
    flash('Recurring task pattern deleted successfully.', 'success')
    return redirect(url_for('list_recurring_tasks'))

# Group Email for Category Route
@app.route('/tasks/email_category_summary', methods=['GET', 'POST'])
def email_category_summary():
    form = SendCategoryEmailForm()
    if form.validate_on_submit():
        category = form.category.data
        subject = form.subject.data
        if not subject.strip(): # Ensure subject is not just whitespace
            subject = f"Task Summary for Category: {category.name}" # Default if empty
        elif category.name not in subject: # Append category name if not already there
            subject = f"{subject} (Category: {category.name})"

        custom_message = form.custom_message.data

        tasks_in_category = Task.query.filter(
            Task.category_id == category.id,
            Task.status != 'Completed' # Exclude completed tasks
        ).all()

        if not tasks_in_category:
            flash(f'No active tasks found in category "{category.name}". Email not sent.', 'info')
            return redirect(url_for('email_category_summary'))

        recipients = set() # Use a set to ensure uniqueness
        if form.send_to_dl.data:
            dl_email = current_app.config.get('DEFAULT_GROUP_EMAIL_DL')
            if dl_email:
                recipients.add(dl_email)
            else:
                flash('Default Group Email DL is not configured. Cannot send to DL.', 'warning')
        
        if form.send_to_assignees.data:
            for task in tasks_in_category:
                if task.assignee and task.assignee.email:
                    recipients.add(task.assignee.email)

        if not recipients:
            flash('No recipients found (DL not selected/configured, or no assignees with email). Email not sent.', 'warning')
            return redirect(url_for('email_category_summary'))
        
        try:
            html_body = render_template(
                'email/category_tasks_email.html',
                tasks=tasks_in_category,
                category=category,
                custom_message=custom_message
            )
            send_email(
                to=list(recipients),
                subject=subject,
                template_name_or_body=html_body
            )
            flash(f'Email summary for category "{category.name}" sent to {len(recipients)} recipient(s).', 'success')
        except Exception as e:
            current_app.logger.error(f"Failed to send category summary email for '{category.name}': {e}")
            flash(f'Failed to send email summary for category "{category.name}". Error: {e}', 'danger')
        
        return redirect(url_for('list_tasks')) # Or back to the form, or category list

    return render_template('tasks/email_category_summary_form.html', title='Email Category Task Summary', form=form)

# Process Document Routes
@app.route('/documents')
def list_documents():
    documents = ProcessDocument.query.order_by(ProcessDocument.uploaded_at.desc()).all()
    return render_template('documents/list_documents.html', title='Process Documents', documents=documents)

@app.route('/documents/add', methods=['GET', 'POST'])
def add_document():
    form = ProcessDocumentForm()
    if form.validate_on_submit():
        doc = ProcessDocument(
            title=form.title.data,
            content=form.content.data,
            link=form.link.data,
            category=form.category.data
        )
        db.session.add(doc)
        db.session.commit()
        flash('Process document saved successfully!', 'success')
        return redirect(url_for('list_documents'))
    return render_template('documents/add_document.html', title='Add Process Document', form=form)

@app.route('/documents/view/<int:doc_id>')
def view_document(doc_id):
    document = ProcessDocument.query.get_or_404(doc_id)
    return render_template('documents/view_document.html', title=document.title, document=document)

@app.route('/documents/edit/<int:doc_id>', methods=['GET', 'POST'])
def edit_document(doc_id):
    document = ProcessDocument.query.get_or_404(doc_id)
    form = ProcessDocumentForm(obj=document)
    if form.validate_on_submit():
        document.title = form.title.data
        document.content = form.content.data
        document.link = form.link.data
        document.category = form.category.data
        document.uploaded_at = datetime.utcnow() # Update timestamp
        db.session.commit()
        flash('Process document updated successfully!', 'success')
        return redirect(url_for('list_documents'))
    return render_template('documents/edit_document.html', title=f'Edit {document.title}', form=form, document=document)

@app.route('/documents/delete/<int:doc_id>', methods=['POST'])
def delete_document(doc_id):
    document = ProcessDocument.query.get_or_404(doc_id)
    db.session.delete(document)
    db.session.commit()
    flash('Process document deleted successfully!', 'success')
    return redirect(url_for('list_documents'))
