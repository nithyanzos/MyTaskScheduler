from datetime import date, timedelta, datetime
from task_manager_app.app import db, app as current_app # Import app for app_context
from task_manager_app.app.models import Task, RecurringTaskPattern, User, Category

def calculate_next_occurrence(last_date, rule, start_date_of_pattern):
    """
    Calculates the next occurrence date based on the rule.
    :param last_date: The date from which to calculate the next one.
    :param rule: 'daily', 'weekly', 'biweekly', 'monthly_day'.
    :param start_date_of_pattern: The original start date of the pattern (for monthly_day).
    :return: The next date object.
    """
    if rule == 'daily':
        return last_date + timedelta(days=1)
    elif rule == 'weekly':
        return last_date + timedelta(weeks=1)
    elif rule == 'biweekly':
        return last_date + timedelta(weeks=2)
    elif rule == 'monthly_day':
        # Add one month. This can be tricky with end of month.
        # A simple approach:
        next_month = last_date.month + 1
        next_year = last_date.year
        if next_month > 12:
            next_month = 1
            next_year += 1
        
        # Try to use the same day, otherwise adjust (e.g., if pattern started on 31st, but next month has 30 days)
        day_to_use = start_date_of_pattern.day
        try:
            return date(next_year, next_month, day_to_use)
        except ValueError:
            # Handle cases like Feb 30th -> use last day of Feb
            import calendar
            last_day_of_month = calendar.monthrange(next_year, next_month)[1]
            return date(next_year, next_month, last_day_of_month)
    return None # Should not happen with valid rules

def generate_tasks_for_pattern(pattern_id, upto_date=None):
    """
    Generates tasks for a given recurring pattern up to a certain date.
    :param pattern_id: ID of the RecurringTaskPattern.
    :param upto_date: Generate tasks up to this date. Defaults to 30 days from now if None.
    """
    with current_app.app_context(): # Ensure we're in app context for DB operations
        pattern = RecurringTaskPattern.query.get(pattern_id)
        if not pattern:
            current_app.logger.error(f"RecurringTaskPattern with id {pattern_id} not found.")
            return

        if upto_date is None:
            upto_date = date.today() + timedelta(days=30)

        # Determine the starting point for generation
        current_next_date = pattern.last_generated_date or pattern.start_date
        if pattern.last_generated_date and pattern.last_generated_date >= pattern.start_date:
             # If tasks have been generated, start from the day after the last generated one
            current_next_date = calculate_next_occurrence(pattern.last_generated_date, pattern.recurrence_rule, pattern.start_date)
        else: # No tasks generated yet, or last_generated_date is before start_date (should not happen)
            current_next_date = pattern.start_date


        tasks_created_count = 0
        while current_next_date and current_next_date <= upto_date:
            if pattern.end_date and current_next_date > pattern.end_date:
                break # Stop if the pattern has an end date and we've passed it

            # Check if a task already exists for this pattern and due date
            # This check assumes a unique combination of title and due_date for a recurring task instance.
            # A more robust way would be to link Task to RecurringTaskPattern via a foreign key.
            existing_task = Task.query.filter_by(
                title=pattern.base_task_title, 
                due_date=datetime.combine(current_next_date, datetime.min.time()), # Assuming due_date in Task is DateTime
                # assigned_to_user_id=pattern.assigned_to_user_id # Could also check assignee
            ).first()

            if not existing_task:
                new_task = Task(
                    title=pattern.base_task_title,
                    description=pattern.base_task_description,
                    priority=pattern.base_task_priority,
                    category_id=pattern.base_task_category_id,
                    assigned_to_user_id=pattern.assigned_to_user_id,
                    created_by_user_id=pattern.created_by_user_id, # Assuming this is set on pattern
                    due_date=datetime.combine(current_next_date, datetime.min.time()), # Store as DateTime
                    status='To Do',
                    is_recurring=True 
                    # recurrence_rule could be set here if needed on Task, but it's on the pattern
                )
                db.session.add(new_task)
                tasks_created_count += 1
                current_app.logger.info(f"Generated task '{new_task.title}' for pattern {pattern.id} due on {current_next_date}")
            
            pattern.last_generated_date = current_next_date
            next_occurrence_candidate = calculate_next_occurrence(current_next_date, pattern.recurrence_rule, pattern.start_date)
            
            # Safety break if calculation doesn't advance date (e.g. bad rule or logic error)
            if next_occurrence_candidate and next_occurrence_candidate <= current_next_date:
                current_app.logger.error(f"Next occurrence calculation did not advance date for pattern {pattern.id}. Rule: {pattern.recurrence_rule}, Current: {current_next_date}")
                break
            current_next_date = next_occurrence_candidate

        if tasks_created_count > 0:
            db.session.commit()
            current_app.logger.info(f"Committed {tasks_created_count} new tasks for pattern {pattern.id}.")
        else:
            current_app.logger.info(f"No new tasks needed to be generated for pattern {pattern.id} up to {upto_date}.")


def schedule_task_generation():
    """
    Scheduled job to iterate through all active recurring patterns and generate tasks.
    """
    with current_app.app_context(): # Ensure DB operations happen within app context
        current_app.logger.info("Scheduler: Running schedule_task_generation job.")
        active_patterns = RecurringTaskPattern.query.filter(
            (RecurringTaskPattern.end_date == None) | (RecurringTaskPattern.end_date >= date.today())
        ).all()

        for pattern in active_patterns:
            current_app.logger.info(f"Scheduler: Processing pattern ID {pattern.id} ('{pattern.base_task_title}').")
            # Generate tasks for the next, e.g., 60 days from today
            generate_tasks_for_pattern(pattern.id, upto_date=date.today() + timedelta(days=60))
        
        current_app.logger.info("Scheduler: Finished schedule_task_generation job.")
