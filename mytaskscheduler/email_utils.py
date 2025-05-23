import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
from datetime import datetime, timedelta

# Utility functions for sending emails

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# This is a simulation since we're running locally
# In a real environment, you would configure SMTP settings
def send_email_reminder(task, recipient_email):
    """
    Send a reminder email for a task
    
    Args:
        task: Task dictionary containing details
        recipient_email: Email address of the recipient
    
    Returns:
        bool: True if email would have been sent successfully
    """
    try:
        # In a real environment, you would use these settings
        # smtp_server = "smtp.example.com"
        # port = 587
        # sender_email = "taskscheduler@example.com"
        # password = "your_password"
        
        # For now, we'll just log that we would send an email
        logger.info(f"[EMAIL SIMULATION] Sending reminder to {recipient_email}")
        logger.info(f"Subject: Reminder: {task['title']} due on {task['due_date']}")
        logger.info(f"Body: This is a reminder that your task '{task['title']}' is due on {task['due_date']}.")
        logger.info(f"      Description: {task['description']}")
        
        # In a real environment, you'd do something like:
        # message = MIMEMultipart()
        # message["From"] = sender_email
        # message["To"] = recipient_email
        # message["Subject"] = f"Reminder: {task['title']} due on {task['due_date']}"
        # body = f"This is a reminder that your task '{task['title']}' is due on {task['due_date']}.\n\nDescription: {task['description']}"
        # message.attach(MIMEText(body, "plain"))
        # 
        # with smtplib.SMTP(smtp_server, port) as server:
        #     server.starttls()
        #     server.login(sender_email, password)
        #     server.send_message(message)
        
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return False

def check_due_tasks(tasks, days_threshold=1):
    """
    Check for tasks that are due soon and should trigger reminders
    
    Args:
        tasks: List of task dictionaries
        days_threshold: Number of days before due date to send reminder
        
    Returns:
        list: Tasks that need reminders
    """
    today = datetime.now().date()
    reminder_tasks = []
    
    for task in tasks:
        if task['status'] == 'Completed':
            continue
            
        try:
            # Parse the due date from string
            due_date = datetime.strptime(task['due_date'], '%Y-%m-%d').date()
            days_left = (due_date - today).days
            
            # Send reminder if due date is within threshold or overdue
            if 0 <= days_left <= days_threshold:
                reminder_tasks.append(task)
        except (ValueError, KeyError):
            # Skip tasks with invalid date format
            continue
    
    return reminder_tasks
