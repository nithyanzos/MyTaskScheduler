from datetime import date, timedelta, datetime
from task_manager_app.app import db, app as current_app # Import app for app_context
from task_manager_app.app.models import Task, User
from task_manager_app.app.email_utils import send_email
import logging

def send_task_reminders():
    """
    Sends email reminders for tasks that are due soon or overdue.
    """
    with current_app.app_context(): # Ensure we're in app context for DB operations and config
        current_app.logger.info("Scheduler: Running send_task_reminders job.")
        
        today = date.today()
        due_soon_date_start = datetime.combine(today + timedelta(days=1), datetime.min.time())
        due_soon_date_end = datetime.combine(today + timedelta(days=2), datetime.max.time()) # Within next 48 hours

        # Tasks due soon (e.g., tomorrow and the day after)
        tasks_due_soon = Task.query.filter(
            Task.due_date >= due_soon_date_start,
            Task.due_date <= due_soon_date_end,
            Task.status != 'Completed'
        ).all()

        # Overdue tasks
        overdue_tasks = Task.query.filter(
            Task.due_date < datetime.combine(today, datetime.min.time()), # Due date is before today
            Task.status != 'Completed'
        ).all()

        reminders_sent_count = 0

        for task in tasks_due_soon:
            if task.assignee and task.assignee.email:
                try:
                    send_email(
                        to=task.assignee.email,
                        subject=f"Task Reminder: '{task.title}' is due soon",
                        template_name_or_body='email/task_reminder_email.html',
                        user=task.assignee,
                        task=task,
                        overdue=False
                    )
                    reminders_sent_count +=1
                    current_app.logger.info(f"Sent due soon reminder for task ID {task.id} to {task.assignee.email}")
                except Exception as e:
                    current_app.logger.error(f"Error sending due soon reminder for task {task.id}: {e}")
            else:
                current_app.logger.warning(f"Task ID {task.id} (due soon) has no assignee or assignee email.")


        for task in overdue_tasks:
            if task.assignee and task.assignee.email:
                try:
                    send_email(
                        to=task.assignee.email,
                        subject=f"Task Overdue: '{task.title}'",
                        template_name_or_body='email/task_reminder_email.html',
                        user=task.assignee,
                        task=task,
                        overdue=True
                    )
                    reminders_sent_count +=1
                    current_app.logger.info(f"Sent overdue reminder for task ID {task.id} to {task.assignee.email}")
                except Exception as e:
                    current_app.logger.error(f"Error sending overdue reminder for task {task.id}: {e}")
            else:
                current_app.logger.warning(f"Task ID {task.id} (overdue) has no assignee or assignee email.")
        
        if reminders_sent_count > 0:
            current_app.logger.info(f"Scheduler: Sent {reminders_sent_count} task reminders.")
        else:
            current_app.logger.info("Scheduler: No task reminders needed to be sent.")
        current_app.logger.info("Scheduler: Finished send_task_reminders job.")
