"""
Seller onboarding notification service
Sends emails and in-app notifications on application status changes
"""
from services.notification_service import EmailService
from services.seller_email_templates import SellerEmailTemplates
from database.models import User
import os
from datetime import datetime

class SellerNotificationService:
    """Service for sending seller application status notifications"""
    
    def __init__(self):
        """Initialize seller notification service"""
        self.email_service = EmailService()
        self.templates = SellerEmailTemplates()
        self.support_email = os.getenv('SUPPORT_EMAIL', 'support@medverify.com')
        self.dashboard_url = os.getenv('DASHBOARD_URL', 'https://medverify.com')
    
    def notify_on_submission(self, seller: dict, user: dict) -> dict:
        """Send email when seller submits application"""
        try:
            seller_name = seller.get('authorized_person', 'Seller')
            company_name = seller.get('company_name', 'Your Company')
            user_email = user.get('email')
            
            if not user_email:
                return {"status": "failed", "error": "User email not found"}
            
            email_data = self.templates.on_submission(
                seller_name=seller_name,
                application_date=datetime.now().strftime('%B %d, %Y'),
                support_email=self.support_email
            )
            
            result = self.email_service.send_email(
                to_email=user_email,
                subject=email_data['subject'],
                body=email_data['body']
            )
            
            return {
                "status": "sent" if result.get('status') == 'sent' else "failed",
                "channel": "email",
                "recipient": user_email
            }
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    def notify_on_viewed(self, seller: dict, user: dict) -> dict:
        """Send email when admin marks application as viewed"""
        try:
            seller_name = seller.get('authorized_person', 'Seller')
            company_name = seller.get('company_name', 'Your Company')
            user_email = user.get('email')
            
            if not user_email:
                return {"status": "failed", "error": "User email not found"}
            
            email_data = self.templates.on_viewed(
                seller_name=seller_name,
                company_name=company_name
            )
            
            result = self.email_service.send_email(
                to_email=user_email,
                subject=email_data['subject'],
                body=email_data['body']
            )
            
            return {
                "status": "sent" if result.get('status') == 'sent' else "failed",
                "channel": "email",
                "recipient": user_email
            }
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    def notify_on_verifying(self, seller: dict, user: dict) -> dict:
        """Send email when admin sets application to verifying"""
        try:
            seller_name = seller.get('authorized_person', 'Seller')
            company_name = seller.get('company_name', 'Your Company')
            user_email = user.get('email')
            
            if not user_email:
                return {"status": "failed", "error": "User email not found"}
            
            email_data = self.templates.on_verifying(
                seller_name=seller_name,
                company_name=company_name
            )
            
            result = self.email_service.send_email(
                to_email=user_email,
                subject=email_data['subject'],
                body=email_data['body']
            )
            
            return {
                "status": "sent" if result.get('status') == 'sent' else "failed",
                "channel": "email",
                "recipient": user_email
            }
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    def notify_on_approved(self, seller: dict, user: dict) -> dict:
        """Send email when seller application is approved"""
        try:
            seller_name = seller.get('authorized_person', 'Seller')
            company_name = seller.get('company_name', 'Your Company')
            user_email = user.get('email')
            
            if not user_email:
                return {"status": "failed", "error": "User email not found"}
            
            dashboard_url = f"{self.dashboard_url}/seller/dashboard"
            
            email_data = self.templates.on_approved(
                seller_name=seller_name,
                company_name=company_name,
                dashboard_url=dashboard_url,
                support_email=self.support_email
            )
            
            result = self.email_service.send_email(
                to_email=user_email,
                subject=email_data['subject'],
                body=email_data['body']
            )
            
            return {
                "status": "sent" if result.get('status') == 'sent' else "failed",
                "channel": "email",
                "recipient": user_email
            }
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    def notify_on_changes_required(self, seller: dict, user: dict, required_changes: list) -> dict:
        """Send email when seller needs to make changes"""
        try:
            seller_name = seller.get('authorized_person', 'Seller')
            company_name = seller.get('company_name', 'Your Company')
            user_email = user.get('email')
            
            if not user_email:
                return {"status": "failed", "error": "User email not found"}
            
            status_url = f"{self.dashboard_url}/seller/status"
            
            email_data = self.templates.on_changes_required(
                seller_name=seller_name,
                company_name=company_name,
                required_changes=required_changes,
                dashboard_url=status_url
            )
            
            result = self.email_service.send_email(
                to_email=user_email,
                subject=email_data['subject'],
                body=email_data['body']
            )
            
            return {
                "status": "sent" if result.get('status') == 'sent' else "failed",
                "channel": "email",
                "recipient": user_email
            }
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    def notify_on_rejected(self, seller: dict, user: dict, admin_remarks: str = '') -> dict:
        """Send email when seller application is rejected"""
        try:
            seller_name = seller.get('authorized_person', 'Seller')
            company_name = seller.get('company_name', 'Your Company')
            user_email = user.get('email')
            
            if not user_email:
                return {"status": "failed", "error": "User email not found"}
            
            email_data = self.templates.on_rejected(
                seller_name=seller_name,
                company_name=company_name,
                admin_remarks=admin_remarks,
                support_email=self.support_email
            )
            
            result = self.email_service.send_email(
                to_email=user_email,
                subject=email_data['subject'],
                body=email_data['body']
            )
            
            return {
                "status": "sent" if result.get('status') == 'sent' else "failed",
                "channel": "email",
                "recipient": user_email
            }
        except Exception as e:
            return {"status": "failed", "error": str(e)}


# Singleton instance
_seller_notification_service = None

def get_seller_notification_service() -> SellerNotificationService:
    """Get singleton instance of seller notification service"""
    global _seller_notification_service
    if _seller_notification_service is None:
        _seller_notification_service = SellerNotificationService()
    return _seller_notification_service
