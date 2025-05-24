from datetime import datetime, date
from task_manager_app.app import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False, default='staff')  # e.g., 'staff', 'manager', 'admin'
    password_hash = db.Column(db.String(256), nullable=False)  # For storing hashed passwords
    
    # Reporting structure
    reports_to_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    direct_reports = db.relationship('User', backref=db.backref('manager', remote_side=[id]), lazy='dynamic')

    tasks_assigned = db.relationship('Task', foreign_keys='Task.assigned_to_user_id', backref='assignee', lazy=True)
    tasks_created = db.relationship('Task', foreign_keys='Task.created_by_user_id', backref='creator', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    tasks = db.relationship('Task', backref='category', lazy=True)

    def __repr__(self):
        return f'<Category {self.name}>'

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    creation_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='To Do')  # e.g., 'To Do', 'In Progress', 'Completed'
    priority = db.Column(db.String(20), nullable=False, default='Medium')  # e.g., 'Low', 'Medium', 'High'
    is_recurring = db.Column(db.Boolean, default=False) # This field might be redundant if RecurringTaskPattern is used for all recurring tasks
    recurrence_rule = db.Column(db.String(100), nullable=True) # e.g., 'daily', 'weekly', 'monthly:15', 'biweekly', 'quarterly:end'

    assigned_to_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_by_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) # Made nullable for now
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)

    def __repr__(self):
        return f'<Task {self.title}>'

class RecurringTaskPattern(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    base_task_title = db.Column(db.String(200), nullable=False)
    base_task_description = db.Column(db.Text, nullable=True)
    base_task_priority = db.Column(db.String(20), default='Medium')
    base_task_category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    
    assigned_to_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) # Who new instances should be assigned to
    created_by_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # Who defined this pattern
    
    recurrence_rule = db.Column(db.String(100), nullable=False)  # e.g., 'daily', 'weekly', 'biweekly', 'monthly:15' (day of month), 'quarterly:start' (start of quarter)
    start_date = db.Column(db.Date, nullable=False, default=date.today)
    end_date = db.Column(db.Date, nullable=True)
    last_generated_date = db.Column(db.Date, nullable=True) # To keep track of when the last task instance was created

    # Relationships to link back to User and Category for the base pattern
    base_category = db.relationship('Category', foreign_keys=[base_task_category_id])
    assigned_to_user = db.relationship('User', foreign_keys=[assigned_to_user_id], backref='recurring_tasks_assigned')
    created_by_user = db.relationship('User', foreign_keys=[created_by_user_id], backref='recurring_tasks_created')

    def __repr__(self):
        return f'<RecurringTaskPattern {self.base_task_title}>'

class ProcessDocument(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=True) # For storing actual content
    link = db.Column(db.String(500), nullable=True) # For linking to external documents
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True) # Optional category
    category = db.relationship('Category', backref=db.backref('process_documents', lazy=True))
    uploaded_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<ProcessDocument {self.title}>'
