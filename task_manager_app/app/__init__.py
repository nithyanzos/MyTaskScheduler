from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
import os
import atexit
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Email Configuration - using placeholders for now
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.example.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', '1', 't']
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'your-email@example.com')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'your-email-password')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@example.com')
app.config['DEFAULT_GROUP_EMAIL_DL'] = os.environ.get('DEFAULT_GROUP_EMAIL_DL', 'your_group_dl@example.com') # Group DL

db = SQLAlchemy(app)
mail = Mail(app)

# Initialize APScheduler
scheduler = BackgroundScheduler(daemon=True) # daemon=True allows app to exit even if scheduler thread is running
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

from task_manager_app.app import routes, models # Import after app and db are defined

# Import and schedule the task generation job
from task_manager_app.app.recurring_tasks_logic import schedule_task_generation
from task_manager_app.app.scheduler_jobs import send_task_reminders # Import send_task_reminders

if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true': # Avoid running scheduler twice in debug mode
   scheduler.add_job(id='ScheduledTaskGeneration', func=schedule_task_generation, trigger='cron', hour=1, minute=0) # Run daily at 1 AM
   scheduler.add_job(id='SendTaskReminders', func=send_task_reminders, trigger='cron', hour=8, minute=0) # Run daily at 8 AM

with app.app_context():
    db.create_all()
