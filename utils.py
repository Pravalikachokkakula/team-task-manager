import smtplib
from email.message import EmailMessage
import os
import threading

def _send_task_notification_sync(user_email, task_title, project_name, due_date):
    """
    Sends an email notification to the user when a task is assigned.
    If no SMTP credentials are provided, it mocks the email by printing to the console.
    """
    try:
        sender_email = os.environ.get('MAIL_USERNAME')
        sender_password = os.environ.get('MAIL_PASSWORD')
        smtp_server = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.environ.get('MAIL_PORT', 587))
        
        # Mock behavior for local development if credentials aren't set
        if not sender_email or not sender_password:
            print(f"\n{'='*40}")
            print(f"MOCK EMAIL NOTIFICATION (No SMTP Config)")
            print(f"To: {user_email}")
            print(f"Subject: New Task Assigned: {task_title}")
            print(f"Body:\nHello,\nYou have been assigned a new task:\n- Task: {task_title}\n- Project: {project_name}\n- Due Date: {due_date}\n\nPlease log in to check it out.")
            print(f"{'='*40}\n")
            return

        # Real email behavior
        msg = EmailMessage()
        msg['Subject'] = f"New Task Assigned: {task_title}"
        msg['From'] = sender_email
        msg['To'] = user_email
        msg.set_content(f"""Hello,

You have been assigned a new task on Team Task Manager:

Task: {task_title}
Project: {project_name}
Due Date: {due_date}

Please log in to the platform to view more details and update your progress.

Best regards,
Task Manager Admin
""")

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
    except Exception as e:
        print(f"Failed to send email to {user_email} in background thread. Error: {e}")

def send_task_notification(user_email, task_title, project_name, due_date):
    """
    Wraps the synchronous email sender in a background thread
    so the HTTP request returns instantly and does not block the UI.
    """
    thread = threading.Thread(
        target=_send_task_notification_sync, 
        args=(user_email, task_title, project_name, due_date)
    )
    thread.daemon = True
    thread.start()
