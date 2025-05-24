from flask import render_template, current_app
from flask_mail import Message
from task_manager_app.app import mail # mail instance from __init__.py
import logging

def send_email(to, subject, template_name_or_body, **kwargs):
    """
    Sends an email.
    :param to: Recipient email address (or list of addresses).
    :param subject: Email subject.
    :param template_name_or_body: Path to the HTML template or the raw body content.
    :param kwargs: Context variables for the template.
    """
    app = current_app._get_current_object() # Get the current app instance
    
    if isinstance(to, str):
        recipients = [to]
    elif isinstance(to, list):
        recipients = to
    else:
        logging.error("Recipient 'to' must be a string or a list of strings.")
        return

    msg = Message(
        subject,
        recipients=recipients,
        sender=app.config.get('MAIL_DEFAULT_SENDER')
    )

    # Check if template_name_or_body is a template file or raw HTML/text
    if '.html' in template_name_or_body or '.txt' in template_name_or_body:
        try:
            msg.html = render_template(template_name_or_body, **kwargs)
        except Exception as e:
            logging.error(f"Error rendering template {template_name_or_body}: {e}")
            # Fallback to using template_name_or_body as raw content if template rendering fails
            msg.body = "Error rendering email template. Please contact support." # Or use template_name_or_body if it's safe
    else:
        msg.body = template_name_or_body # Assume it's raw text/HTML

    try:
        if app.debug:
            # In debug mode, print the email to console instead of sending
            print("---- EMAIL TO BE SENT ----")
            print(f"From: {msg.sender}")
            print(f"To: {msg.recipients}")
            print(f"Subject: {msg.subject}")
            print("---- BODY ----")
            print(msg.html if msg.html else msg.body)
            print("---- END EMAIL ----")
            logging.info(f"Debug mode: Email to {recipients} with subject '{subject}' printed to console.")
        else:
            mail.send(msg)
            logging.info(f"Email sent to {recipients} with subject '{subject}'")
    except Exception as e:
        logging.error(f"Error sending email to {recipients} with subject '{subject}': {e}")

# Example of how to call this (will be used in routes.py)
# send_email('test@example.com', 'Test Subject', 'email/test_email.html', user={'username': 'TestUser'})
# send_email('test@example.com', 'Test Subject Plain', 'This is a plain text email body.')
