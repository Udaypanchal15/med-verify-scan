"""
Notification Service for sending email, push, and SMS notifications
"""
import os
import json
from typing import Dict, Any, Optional
from datetime import datetime
from database.models import NotificationLogs
from database import execute_query

class NotificationService:
    """Service for sending notifications"""
    
    def __init__(self):
        """Initialize notification service"""
        self.email_service = EmailService()
        self.push_service = PushService()
        self.sms_service = SMSService()
    
    def send_notification(self, user_id: str, reminder_id: Optional[str],
                         channels: Dict[str, bool], title: str, message: str,
                         user_email: str = None, device_token: str = None,
                         phone_number: str = None) -> Dict[str, Any]:
        """
        Send notification through specified channels
        Returns notification results
        """
        results = {
            "email": None,
            "push": None,
            "sms": None
        }
        
        # Send email
        if channels.get('email') and user_email:
            try:
                email_result = self.email_service.send_email(
                    to_email=user_email,
                    subject=title,
                    body=message
                )
                results["email"] = email_result
                
                # Log notification
                self._log_notification(reminder_id, user_id, 'email', email_result.get('status', 'sent'))
            except Exception as e:
                print(f"Email notification error: {e}")
                results["email"] = {"status": "failed", "error": str(e)}
                self._log_notification(reminder_id, user_id, 'email', 'failed', error_message=str(e))
        
        # Send push notification
        if channels.get('push') and device_token:
            try:
                push_result = self.push_service.send_push(
                    device_token=device_token,
                    title=title,
                    body=message
                )
                results["push"] = push_result
                
                # Log notification
                self._log_notification(reminder_id, user_id, 'push', push_result.get('status', 'sent'))
            except Exception as e:
                print(f"Push notification error: {e}")
                results["push"] = {"status": "failed", "error": str(e)}
                self._log_notification(reminder_id, user_id, 'push', 'failed', error_message=str(e))
        
        # Send SMS
        if channels.get('sms') and phone_number:
            try:
                sms_result = self.sms_service.send_sms(
                    phone_number=phone_number,
                    message=message
                )
                results["sms"] = sms_result
                
                # Log notification
                self._log_notification(reminder_id, user_id, 'sms', sms_result.get('status', 'sent'))
            except Exception as e:
                print(f"SMS notification error: {e}")
                results["sms"] = {"status": "failed", "error": str(e)}
                self._log_notification(reminder_id, user_id, 'sms', 'failed', error_message=str(e))
        
        return results
    
    def _log_notification(self, reminder_id: Optional[str], user_id: str,
                         channel: str, status: str, error_message: str = None):
        """Log notification to database"""
        try:
            query = """
                INSERT INTO notification_logs (reminder_id, user_id, channel, status, error_message)
                VALUES (%s, %s, %s, %s, %s)
            """
            execute_query(query, (reminder_id, user_id, channel, status, error_message))
        except Exception as e:
            print(f"Error logging notification: {e}")

class EmailService:
    """Email notification service"""
    
    def __init__(self):
        """Initialize email service"""
        self.smtp_host = os.getenv('SMTP_HOST', 'smtp.sendgrid.net')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.smtp_user = os.getenv('SMTP_USER', 'apikey')
        self.smtp_pass = os.getenv('SMTP_PASS') or os.getenv('SENDGRID_API_KEY')
        self.from_email = os.getenv('SMTP_FROM_EMAIL', 'noreply@medverify.com')
    
    def send_email(self, to_email: str, subject: str, body: str) -> Dict[str, Any]:
        """Send email using SMTP or SendGrid"""
        try:
            # Try SendGrid first if API key is available
            sendgrid_key = os.getenv('SENDGRID_API_KEY')
            if sendgrid_key:
                return self._send_via_sendgrid(to_email, subject, body)
            
            # Fallback to SMTP
            return self._send_via_smtp(to_email, subject, body)
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    def _send_via_sendgrid(self, to_email: str, subject: str, body: str) -> Dict[str, Any]:
        """Send email via SendGrid API"""
        try:
            import sendgrid
            from sendgrid.helpers.mail import Mail
            
            sg = sendgrid.SendGridAPIClient(api_key=os.getenv('SENDGRID_API_KEY'))
            message = Mail(
                from_email=self.from_email,
                to_emails=to_email,
                subject=subject,
                html_content=body
            )
            response = sg.send(message)
            
            return {
                "status": "sent",
                "provider": "sendgrid",
                "status_code": response.status_code
            }
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    def _send_via_smtp(self, to_email: str, subject: str, body: str) -> Dict[str, Any]:
        """Send email via SMTP"""
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'html'))
            
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()
            server.login(self.smtp_user, self.smtp_pass)
            server.send_message(msg)
            server.quit()
            
            return {"status": "sent", "provider": "smtp"}
        except Exception as e:
            return {"status": "failed", "error": str(e)}

class PushService:
    """Push notification service using FCM"""
    
    def __init__(self):
        """Initialize push service"""
        self.fcm_server_key = os.getenv('FCM_SERVER_KEY')
        self.fcm_project_id = os.getenv('FCM_PROJECT_ID')
    
    def send_push(self, device_token: str, title: str, body: str) -> Dict[str, Any]:
        """Send push notification via FCM"""
        try:
            if not self.fcm_server_key:
                return {"status": "failed", "error": "FCM server key not configured"}
            
            from pyfcm import FCMNotification
            
            push_service = FCMNotification(api_key=self.fcm_server_key)
            
            result = push_service.notify_single_device(
                registration_id=device_token,
                message_title=title,
                message_body=body
            )
            
            return {
                "status": "sent" if result.get('success') else "failed",
                "provider": "fcm",
                "result": result
            }
        except Exception as e:
            return {"status": "failed", "error": str(e)}

class SMSService:
    """SMS notification service using Twilio"""
    
    def __init__(self):
        """Initialize SMS service"""
        self.twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.twilio_phone = os.getenv('TWILIO_PHONE_NUMBER')
    
    def send_sms(self, phone_number: str, message: str) -> Dict[str, Any]:
        """Send SMS via Twilio"""
        try:
            if not all([self.twilio_account_sid, self.twilio_auth_token, self.twilio_phone]):
                return {"status": "failed", "error": "Twilio not configured"}
            
            from twilio.rest import Client
            
            client = Client(self.twilio_account_sid, self.twilio_auth_token)
            
            message = client.messages.create(
                body=message,
                from_=self.twilio_phone,
                to=phone_number
            )
            
            return {
                "status": "sent",
                "provider": "twilio",
                "message_sid": message.sid
            }
        except Exception as e:
            return {"status": "failed", "error": str(e)}



