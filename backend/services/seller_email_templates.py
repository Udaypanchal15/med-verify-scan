"""
Email templates for seller onboarding and notifications
"""
from datetime import datetime

class SellerEmailTemplates:
    """Email templates for seller onboarding notifications"""
    
    @staticmethod
    def on_submission(seller_name: str, application_date: str, support_email: str = 'support@medverify.com') -> dict:
        """Email when seller submits application"""
        return {
            "subject": "Seller Application Received - MedVerify",
            "body": f"""
            <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #2563eb;">Application Received</h2>
                    
                    <p>Dear {seller_name},</p>
                    
                    <p>Thank you for submitting your seller application to MedVerify. We have received your KYC documents and application details on <strong>{application_date}</strong>.</p>
                    
                    <p>Your application is now in our system and will be reviewed by our admin team. You can check the status of your application anytime by logging into your account and visiting the <strong>Application Status</strong> page.</p>
                    
                    <div style="background-color: #f0f9ff; border-left: 4px solid #2563eb; padding: 15px; margin: 20px 0;">
                        <p><strong>What's Next?</strong></p>
                        <ul>
                            <li>Our team will review your documents and information</li>
                            <li>We will verify your credentials and KYC details</li>
                            <li>You will receive an update via email once the review is complete</li>
                        </ul>
                    </div>
                    
                    <p>If you have any questions or need to update your information, please contact us at <strong>{support_email}</strong>.</p>
                    
                    <p>Best regards,<br/>
                    <strong>MedVerify Team</strong></p>
                </div>
            </body>
            </html>
            """
        }
    
    @staticmethod
    def on_viewed(seller_name: str, company_name: str) -> dict:
        """Email when admin marks application as viewed"""
        return {
            "subject": "Application Status Update - Under Review",
            "body": f"""
            <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #2563eb;">Application Status Update</h2>
                    
                    <p>Dear {seller_name},</p>
                    
                    <p>Good news! Your application for <strong>{company_name}</strong> has been reviewed by our admin team.</p>
                    
                    <p style="background-color: #dbeafe; padding: 10px; border-radius: 4px; border-left: 4px solid #2563eb;">
                        <strong>Current Status:</strong> Under Review
                    </p>
                    
                    <p>Our team is now verifying your documents and information. This process typically takes 2-5 business days.</p>
                    
                    <p>You can check the detailed status of your application in your account dashboard.</p>
                    
                    <p>Best regards,<br/>
                    <strong>MedVerify Team</strong></p>
                </div>
            </body>
            </html>
            """
        }
    
    @staticmethod
    def on_verifying(seller_name: str, company_name: str) -> dict:
        """Email when admin sets application status to verifying"""
        return {
            "subject": "Application Status Update - In Verification",
            "body": f"""
            <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #2563eb;">Application Status Update</h2>
                    
                    <p>Dear {seller_name},</p>
                    
                    <p>Your application for <strong>{company_name}</strong> is now in the verification stage.</p>
                    
                    <p style="background-color: #dbeafe; padding: 10px; border-radius: 4px; border-left: 4px solid #2563eb;">
                        <strong>Current Status:</strong> In Verification
                    </p>
                    
                    <p>Our team is actively verifying your credentials and documents. We will notify you as soon as the verification process is complete.</p>
                    
                    <p>If we need any additional information from you, we will contact you directly.</p>
                    
                    <p>Best regards,<br/>
                    <strong>MedVerify Team</strong></p>
                </div>
            </body>
            </html>
            """
        }
    
    @staticmethod
    def on_approved(seller_name: str, company_name: str, dashboard_url: str = 'https://medverify.com/seller/dashboard', support_email: str = 'support@medverify.com') -> dict:
        """Email when seller application is approved"""
        return {
            "subject": "Seller Application Approved - Welcome to MedVerify!",
            "body": f"""
            <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #16a34a;">Congratulations! Your Application is Approved</h2>
                    
                    <p>Dear {seller_name},</p>
                    
                    <p>Excellent news! Your seller application for <strong>{company_name}</strong> has been <strong style="color: #16a34a;">APPROVED</strong>.</p>
                    
                    <p style="background-color: #f0fdf4; padding: 15px; border-radius: 4px; border-left: 4px solid #16a34a;">
                        <strong style="color: #16a34a;">Status: Approved</strong><br/>
                        You can now access all seller features and start managing your medicines.
                    </p>
                    
                    <p><strong>Next Steps:</strong></p>
                    <ol>
                        <li>Log in to your account</li>
                        <li>Visit the Seller Dashboard to manage your medicines</li>
                        <li>Generate QR codes for your medicine batches</li>
                        <li>Start selling on MedVerify</li>
                    </ol>
                    
                    <p>
                        <a href="{dashboard_url}" style="display: inline-block; background-color: #2563eb; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px; margin-top: 10px;">
                            Go to Seller Dashboard
                        </a>
                    </p>
                    
                    <p>If you have any questions or need assistance, please contact us at <strong>{support_email}</strong>.</p>
                    
                    <p>Best regards,<br/>
                    <strong>MedVerify Team</strong></p>
                </div>
            </body>
            </html>
            """
        }
    
    @staticmethod
    def on_changes_required(seller_name: str, company_name: str, required_changes: list, dashboard_url: str = 'https://medverify.com/seller/status') -> dict:
        """Email when seller needs to make changes"""
        changes_html = ""
        for i, change in enumerate(required_changes, 1):
            field = change.get('field', 'Unknown')
            message = change.get('message', 'Please review and update')
            changes_html += f"<li><strong>{field}:</strong> {message}</li>"
        
        return {
            "subject": "Action Required - Update Your Seller Application",
            "body": f"""
            <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #d97706;">Action Required - Please Update Your Application</h2>
                    
                    <p>Dear {seller_name},</p>
                    
                    <p>During our review of your application for <strong>{company_name}</strong>, we found some information that needs to be updated or clarified.</p>
                    
                    <p style="background-color: #fef3c7; padding: 15px; border-radius: 4px; border-left: 4px solid #d97706;">
                        <strong style="color: #d97706;">Status: Changes Required</strong><br/>
                        Please review the items below and update your application.
                    </p>
                    
                    <p><strong>Required Changes:</strong></p>
                    <ul>
                        {changes_html}
                    </ul>
                    
                    <p>Once you have made the necessary updates, you can resubmit your application from the Application Status page.</p>
                    
                    <p>
                        <a href="{dashboard_url}" style="display: inline-block; background-color: #d97706; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px; margin-top: 10px;">
                            Review and Update Application
                        </a>
                    </p>
                    
                    <p>If you have any questions about these changes, please feel free to contact our support team.</p>
                    
                    <p>Best regards,<br/>
                    <strong>MedVerify Team</strong></p>
                </div>
            </body>
            </html>
            """
        }
    
    @staticmethod
    def on_rejected(seller_name: str, company_name: str, admin_remarks: str = '', support_email: str = 'support@medverify.com') -> dict:
        """Email when seller application is rejected"""
        remarks_section = ""
        if admin_remarks:
            remarks_section = f"""
            <p><strong>Reason for Rejection:</strong></p>
            <p style="background-color: #fee2e2; padding: 10px; border-radius: 4px; border-left: 4px solid #dc2626;">
                {admin_remarks}
            </p>
            """
        
        return {
            "subject": "Seller Application Update - Unable to Approve",
            "body": f"""
            <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #dc2626;">Application Decision</h2>
                    
                    <p>Dear {seller_name},</p>
                    
                    <p>Thank you for submitting your seller application for <strong>{company_name}</strong> to MedVerify. After careful review, we regret to inform you that we are unable to approve your application at this time.</p>
                    
                    <p style="background-color: #fee2e2; padding: 15px; border-radius: 4px; border-left: 4px solid #dc2626;">
                        <strong style="color: #dc2626;">Status: Application Rejected</strong>
                    </p>
                    
                    {remarks_section}
                    
                    <p>If you believe this decision was made in error, or if you would like to discuss this further, please reach out to our support team at <strong>{support_email}</strong>.</p>
                    
                    <p>We appreciate your interest in MedVerify and encourage you to reapply in the future.</p>
                    
                    <p>Best regards,<br/>
                    <strong>MedVerify Team</strong></p>
                </div>
            </body>
            </html>
            """
        }
