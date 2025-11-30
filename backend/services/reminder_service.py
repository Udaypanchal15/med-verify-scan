"""
Reminder Service for managing medicine reminders
"""
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from database.models import Reminder
from dateutil.rrule import rrule, DAILY, WEEKLY, MONTHLY, YEARLY, HOURLY
import pytz

class ReminderService:
    """Service for reminder management"""
    
    def create_reminder(self, user_id: str, title: str, description: str,
                       channel_json: Dict, recurrence_rule: Optional[str],
                       start_time: datetime, timezone: str = 'UTC',
                       medicine_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new reminder with recurrence rule
        recurrence_rule: RFC 5545 format (e.g., "FREQ=DAILY;INTERVAL=1")
        """
        # Calculate next run time
        next_run = start_time
        
        # If recurrence rule provided, calculate next occurrence
        if recurrence_rule:
            try:
                # Parse recurrence rule
                rule = self._parse_recurrence_rule(recurrence_rule, start_time, timezone)
                # Get next occurrence
                occurrences = list(rule)
                if occurrences:
                    next_run = occurrences[0]
            except Exception as e:
                print(f"Error parsing recurrence rule: {e}")
                # Use start_time as fallback
                next_run = start_time
        
        # Create reminder
        reminder = Reminder.create(
            user_id=user_id,
            title=title,
            description=description,
            channel_json=channel_json,
            recurrence_rule=recurrence_rule,
            start_time=start_time,
            timezone=timezone,
            medicine_id=medicine_id,
            next_run=next_run
        )
        
        return reminder
    
    def _parse_recurrence_rule(self, rule_str: str, dtstart: datetime, timezone: str):
        """
        Parse RFC 5545 recurrence rule
        Returns rrule object
        """
        # Parse rule string
        # Format: "FREQ=DAILY;INTERVAL=1;COUNT=10"
        rule_dict = {}
        for part in rule_str.split(';'):
            if '=' in part:
                key, value = part.split('=', 1)
                rule_dict[key] = value
        
        # Get frequency
        freq_map = {
            'DAILY': DAILY,
            'WEEKLY': WEEKLY,
            'MONTHLY': MONTHLY,
            'YEARLY': YEARLY,
            'HOURLY': HOURLY
        }
        freq = freq_map.get(rule_dict.get('FREQ', 'DAILY'), DAILY)
        
        # Get interval
        interval = int(rule_dict.get('INTERVAL', 1))
        
        # Get count (optional)
        count = int(rule_dict.get('COUNT')) if 'COUNT' in rule_dict else None
        
        # Get until (optional)
        until = None
        if 'UNTIL' in rule_dict:
            until = datetime.fromisoformat(rule_dict['UNTIL'].replace('Z', '+00:00'))
        
        # Create rrule
        rule = rrule(
            freq=freq,
            interval=interval,
            dtstart=dtstart,
            count=count,
            until=until
        )
        
        return rule
    
    def get_next_run(self, reminder: Dict[str, Any]) -> Optional[datetime]:
        """Calculate next run time for reminder"""
        if not reminder.get('recurrence_rule'):
            return None
        
        try:
            start_time = reminder['start_time']
            if isinstance(start_time, str):
                start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            
            rule = self._parse_recurrence_rule(
                reminder['recurrence_rule'],
                start_time,
                reminder.get('timezone', 'UTC')
            )
            
            # Get next occurrence after current next_run
            current_next = reminder.get('next_run')
            if isinstance(current_next, str):
                current_next = datetime.fromisoformat(current_next.replace('Z', '+00:00'))
            
            occurrences = list(rule.after(current_next, inc=False))
            if occurrences:
                return occurrences[0]
            
            return None
        except Exception as e:
            print(f"Error calculating next run: {e}")
            return None
