"""
Reminder Worker for processing due reminders
Uses APScheduler for simple scheduling or Celery for production
"""
import os
from datetime import datetime, timezone
from database.models import Reminder
from services.reminder_service import ReminderService
from services.notification_service import NotificationService
from database.models import User
from database.models import DeviceTokens
from database import execute_query

class ReminderWorker:
    """Worker for processing reminders"""
    
    def __init__(self):
        """Initialize reminder worker"""
        self.reminder_service = ReminderService()
        self.notification_service = NotificationService()
    
    def process_due_reminders(self):
        """Process all due reminders"""
        try:
            # Get due reminders
            due_reminders = Reminder.get_due_reminders()
            
            for reminder in due_reminders:
                try:
                    self.process_reminder(reminder)
                except Exception as e:
                    print(f"Error processing reminder {reminder.get('id')}: {e}")
        except Exception as e:
            print(f"Error processing due reminders: {e}")
    
    def process_reminder(self, reminder: Dict[str, Any]):
        """Process a single reminder"""
        try:
            user_id = reminder.get('user_id')
            reminder_id = reminder.get('id')
            
            # Get user information
            user = User.get_by_id(user_id)
            if not user:
                print(f"User not found: {user_id}")
                return
            
            # Get user email
            user_email = user.get('email')
            
            # Get device tokens
            device_tokens = self._get_device_tokens(user_id)
            
            # Get channels
            channel_json = reminder.get('channel_json', {})
            if isinstance(channel_json, str):
                import json
                channel_json = json.loads(channel_json)
            
            # Prepare notification
            title = reminder.get('title', 'Medicine Reminder')
            description = reminder.get('description', '')
            message = f"{title}\n\n{description}"
            
            # Send notifications
            results = self.notification_service.send_notification(
                user_id=user_id,
                reminder_id=str(reminder_id),
                channels=channel_json,
                title=title,
                message=message,
                user_email=user_email,
                device_token=device_tokens[0] if device_tokens else None
            )
            
            # Update next run time if recurring
            if reminder.get('recurrence_rule'):
                next_run = self.reminder_service.get_next_run(reminder)
                if next_run:
                    Reminder.update_next_run(str(reminder_id), next_run)
                else:
                    # No more occurrences, deactivate
                    query = "UPDATE reminders SET active = FALSE WHERE id = %s"
                    execute_query(query, (reminder_id,))
            else:
                # One-time reminder, deactivate
                query = "UPDATE reminders SET active = FALSE WHERE id = %s"
                execute_query(query, (reminder_id,))
            
            print(f"Processed reminder {reminder_id}: {results}")
        except Exception as e:
            print(f"Error processing reminder: {e}")
    
    def _get_device_tokens(self, user_id: str) -> list:
        """Get device tokens for user"""
        try:
            query = "SELECT token FROM device_tokens WHERE user_id = %s"
            results = execute_query(query, (user_id,), fetch_all=True)
            return [r['token'] for r in results] if results else []
        except Exception as e:
            print(f"Error getting device tokens: {e}")
            return []

def start_reminder_worker():
    """Start reminder worker with APScheduler"""
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        from apscheduler.triggers.interval import IntervalTrigger
        
        worker = ReminderWorker()
        
        scheduler = BackgroundScheduler()
        scheduler.add_job(
            worker.process_due_reminders,
            trigger=IntervalTrigger(seconds=60),  # Check every minute
            id='process_reminders',
            name='Process due reminders',
            replace_existing=True
        )
        
        scheduler.start()
        print("Reminder worker started")
        return scheduler
    except Exception as e:
        print(f"Error starting reminder worker: {e}")
        return None

