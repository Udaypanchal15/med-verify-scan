"""
Database models and helper functions
"""
from datetime import datetime, timezone
import uuid
from typing import Optional, Dict, Any
from . import get_db, execute_query

class User:
    """User model"""
    
    @staticmethod
    def create(email: str, password_hash: str, role: str = 'user', timezone: str = 'UTC') -> Dict[str, Any]:
        """Create a new user"""
        # Normalize email to lowercase for consistency
        email = email.lower().strip()
        query = """
            INSERT INTO users (email, password_hash, role, timezone)
            VALUES (%s, %s, %s, %s)
            RETURNING id, email, role, timezone, created_at
        """
        result = execute_query(query, (email, password_hash, role, timezone), fetch_one=True)
        return dict(result) if result else None
    
    @staticmethod
    def get_by_email(email: str) -> Optional[Dict[str, Any]]:
        """Get user by email (case-insensitive)"""
        # Normalize email to lowercase for case-insensitive lookup
        email = email.lower().strip()
        query = "SELECT * FROM users WHERE LOWER(email) = %s"
        result = execute_query(query, (email,), fetch_one=True)
        return dict(result) if result else None
    
    @staticmethod
    def get_by_id(user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        query = "SELECT * FROM users WHERE id = %s"
        result = execute_query(query, (user_id,), fetch_one=True)
        return dict(result) if result else None
    
    @staticmethod
    def update_last_login(user_id: str):
        """Update last login timestamp"""
        query = "UPDATE users SET last_login = %s WHERE id = %s"
        execute_query(query, (datetime.now(timezone.utc), user_id))

class Seller:
    """Seller model"""
    
    @staticmethod
    def create(user_id: str, company_name: str, license_number: str,
               license_type: str = None, license_expiry: str = None,
               gstin: str = None, address: str = None,
               authorized_person: str = None, authorized_person_contact: str = None,
               email: str = None, company_website: str = None,
               documents: Dict = None, document_checksums: Dict = None) -> Dict[str, Any]:
        """Create a new seller application with all available fields"""
        import json

        # Insert all available fields
        query = """
            INSERT INTO sellers (
                user_id, company_name, license_number, license_type, 
                license_expiry, gstin, address, authorized_person,
                authorized_person_contact, email, company_website, 
                documents, document_checksums, status
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'pending')
            RETURNING id, user_id, company_name, license_number, license_type,
                      license_expiry, gstin, address, authorized_person,
                      authorized_person_contact, email, company_website,
                      status, created_at
        """
        
        # Convert documents dict to JSON if provided
        documents_json = json.dumps(documents) if documents else None
        checksums_json = json.dumps(document_checksums) if document_checksums else None
        
        result = execute_query(query, (
            user_id, company_name, license_number, license_type,
            license_expiry, gstin, address, authorized_person,
            authorized_person_contact, email, company_website,
            documents_json, checksums_json
        ), fetch_one=True)
        return dict(result) if result else None
    
    @staticmethod
    def get_by_user_id(user_id: str) -> Optional[Dict[str, Any]]:
        """Get seller by user ID"""
        query = "SELECT * FROM sellers WHERE user_id = %s"
        result = execute_query(query, (user_id,), fetch_one=True)
        return dict(result) if result else None
    
    @staticmethod
    def update_status(seller_id: str, status: str, approved_by: str = None):
        """Update seller status"""
        query = """
            UPDATE sellers 
            SET status = %s, approved_by = %s, approved_at = %s
            WHERE id = %s
        """
        approved_at = datetime.now(timezone.utc) if status == 'approved' else None
        execute_query(query, (status, approved_by, approved_at, seller_id))
    
    @staticmethod
    def update_public_key(seller_id: str, public_key: str):
        """Update seller's public key"""
        query = "UPDATE sellers SET public_key = %s WHERE id = %s"
        execute_query(query, (public_key, seller_id))
    
    @staticmethod
    def get_all_pending():
        """Get all pending seller applications"""
        query = "SELECT * FROM sellers WHERE status = 'pending' ORDER BY created_at DESC"
        results = execute_query(query, fetch_all=True)
        return [dict(r) for r in results] if results else []
    
    @staticmethod
    def get_by_id(seller_id: str) -> Optional[Dict[str, Any]]:
        """Get seller by ID"""
        query = "SELECT * FROM sellers WHERE id = %s"
        result = execute_query(query, (seller_id,), fetch_one=True)
        return dict(result) if result else None
    
    @staticmethod
    def get_all_approved():
        """Get all approved sellers"""
        query = "SELECT * FROM sellers WHERE status = 'approved' ORDER BY created_at DESC"
        results = execute_query(query, fetch_all=True)
        return [dict(r) for r in results] if results else []

class Medicine:
    """Medicine model"""
    
    @staticmethod
    def create(seller_id: str, name: str, batch_no: str, mfg_date: str, 
               expiry_date: str, dosage: str = None, strength: str = None,
               category: str = None, description: str = None, image_url: str = None,
               stock_quantity: int = 0, delivery_status: str = 'in_stock') -> Dict[str, Any]:
        """Create a new medicine"""
        query = """
            INSERT INTO medicines (seller_id, name, batch_no, mfg_date, expiry_date, 
                                 dosage, strength, category, description, image_url,
                                 stock_quantity, delivery_status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, seller_id, name, batch_no, mfg_date, expiry_date, stock_quantity, delivery_status, created_at
        """
        result = execute_query(query, (seller_id, name, batch_no, mfg_date, expiry_date,
                                      dosage, strength, category, description, image_url,
                                      stock_quantity, delivery_status), fetch_one=True)
        return dict(result) if result else None
    
    @staticmethod
    def get_by_id(medicine_id: str) -> Optional[Dict[str, Any]]:
        """Get medicine by ID"""
        query = "SELECT * FROM medicines WHERE id = %s"
        result = execute_query(query, (medicine_id,), fetch_one=True)
        return dict(result) if result else None
    
    @staticmethod
    def get_by_seller(seller_id: str):
        """Get all medicines for a seller"""
        query = "SELECT * FROM medicines WHERE seller_id = %s ORDER BY created_at DESC"
        results = execute_query(query, (seller_id,), fetch_all=True)
        return [dict(r) for r in results] if results else []
    
    @staticmethod
    def get_all():
        """Get all medicines from all sellers"""
        query = "SELECT * FROM medicines ORDER BY created_at DESC"
        results = execute_query(query, fetch_all=True)
        return [dict(r) for r in results] if results else []
    
    @staticmethod
    def update(medicine_id: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Update medicine details"""
        allowed_fields = ['name', 'batch_no', 'mfg_date', 'expiry_date', 'dosage',
                         'strength', 'category', 'description', 'usage', 'manufacturer',
                         'stock_quantity', 'delivery_status']

        # Filter out None values and non-allowed fields
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields and v is not None}

        if not updates:
            return None

        # Build dynamic UPDATE query
        set_clause = ', '.join([f"{field} = %s" for field in updates.keys()])
        query = f"UPDATE medicines SET {set_clause} WHERE id = %s RETURNING *"

        values = list(updates.values()) + [medicine_id]
        result = execute_query(query, tuple(values), fetch_one=True)
        return dict(result) if result else None

    @staticmethod
    def update_stock(medicine_id: str, stock_quantity: int):
        """Update medicine stock quantity"""
        query = "UPDATE medicines SET stock_quantity = %s WHERE id = %s"
        execute_query(query, (stock_quantity, medicine_id))

    @staticmethod
    def update_delivery_status(medicine_id: str, delivery_status: str):
        """Update medicine delivery status"""
        query = "UPDATE medicines SET delivery_status = %s WHERE id = %s"
        execute_query(query, (delivery_status, medicine_id))
    
    @staticmethod
    def get_all_pending():
        """Get all pending medicines"""
        query = "SELECT m.*, s.company_name, s.user_id as seller_user_id FROM medicines m JOIN sellers s ON m.seller_id = s.id WHERE m.approval_status = 'pending' ORDER BY m.created_at DESC"
        results = execute_query(query, fetch_all=True)
        return [dict(r) for r in results] if results else []
    
    @staticmethod
    def get_all_approved():
        """Get all approved medicines"""
        query = "SELECT m.*, s.company_name FROM medicines m JOIN sellers s ON m.seller_id = s.id WHERE m.approval_status = 'approved' ORDER BY m.created_at DESC"
        results = execute_query(query, fetch_all=True)
        return [dict(r) for r in results] if results else []
    
    @staticmethod
    def update_approval_status(medicine_id: str, status: str, approved_by: str = None):
        """Update medicine approval status"""
        query = """
            UPDATE medicines 
            SET approval_status = %s, approved_by = %s, approved_at = %s
            WHERE id = %s
        """
        approved_at = datetime.now(timezone.utc) if status == 'approved' else None
        execute_query(query, (status, approved_by, approved_at, medicine_id))

class QRCode:
    """QR Code model"""
    
    @staticmethod
    def create(medicine_id: str, payload_json: Dict, signature: str, 
               blockchain_tx: str = None, issued_by: str = None) -> Dict[str, Any]:
        """Create a new QR code"""
        import json
        query = """
            INSERT INTO qr_codes (medicine_id, payload_json, signature, blockchain_tx, issued_by)
            VALUES (%s, %s::jsonb, %s, %s, %s)
            RETURNING id, medicine_id, issued_at, blockchain_tx
        """
        result = execute_query(query, (medicine_id, json.dumps(payload_json), signature, 
                                      blockchain_tx, issued_by), fetch_one=True)
        return dict(result) if result else None
    
    @staticmethod
    def get_by_id(qr_id: str) -> Optional[Dict[str, Any]]:
        """Get QR code by ID"""
        query = "SELECT * FROM qr_codes WHERE id = %s"
        result = execute_query(query, (qr_id,), fetch_one=True)
        return dict(result) if result else None
    
    @staticmethod
    def revoke(qr_id: str, reason: str = None):
        """Revoke a QR code"""
        query = """
            UPDATE qr_codes 
            SET revoked = TRUE, revoked_at = %s, revoked_reason = %s
            WHERE id = %s
        """
        execute_query(query, (datetime.now(timezone.utc), reason, qr_id))
    
    @staticmethod
    def is_revoked(qr_id: str) -> bool:
        """Check if QR code is revoked"""
        query = "SELECT revoked FROM qr_codes WHERE id = %s"
        result = execute_query(query, (qr_id,), fetch_one=True)
        if result:
            return dict(result).get('revoked', False)
        return False

class Reminder:
    """Reminder model"""
    
    @staticmethod
    def create(user_id: str, title: str, description: str, channel_json: Dict,
               recurrence_rule: str, start_time: datetime, timezone: str = 'UTC',
               medicine_id: str = None, next_run: datetime = None) -> Dict[str, Any]:
        """Create a new reminder"""
        import json
        if next_run is None:
            next_run = start_time
        
        query = """
            INSERT INTO reminders (user_id, medicine_id, title, description, channel_json, 
                                 recurrence_rule, start_time, timezone, next_run)
            VALUES (%s, %s, %s, %s, %s::jsonb, %s, %s, %s, %s)
            RETURNING id, user_id, title, next_run, active
        """
        result = execute_query(query, (user_id, medicine_id, title, description, 
                                      json.dumps(channel_json), recurrence_rule,
                                      start_time, timezone, next_run), fetch_one=True)
        return dict(result) if result else None
    
    @staticmethod
    def get_by_user(user_id: str, active_only: bool = False):
        """Get all reminders for a user"""
        query = "SELECT * FROM reminders WHERE user_id = %s"
        if active_only:
            query += " AND active = TRUE"
        query += " ORDER BY next_run ASC"
        results = execute_query(query, (user_id,), fetch_all=True)
        return [dict(r) for r in results] if results else []
    
    @staticmethod
    def update_next_run(reminder_id: str, next_run: datetime):
        """Update reminder's next run time"""
        query = "UPDATE reminders SET next_run = %s WHERE id = %s"
        execute_query(query, (next_run, reminder_id))
    
    @staticmethod
    def get_due_reminders():
        """Get all reminders that are due for execution"""
        query = """
            SELECT * FROM reminders 
            WHERE active = TRUE AND next_run <= %s
            ORDER BY next_run ASC
        """
        results = execute_query(query, (datetime.now(timezone.utc),), fetch_all=True)
        return [dict(r) for r in results] if results else []

class ScanLog:
    """Scan log model"""
    
    @staticmethod
    def create(user_id: str, qr_id: str, raw_payload: str, result: str,
               details: Dict = None, ip_address: str = None, user_agent: str = None) -> Dict[str, Any]:
        """Create a new scan log"""
        import json
        query = """
            INSERT INTO scan_logs (user_id, qr_id, raw_payload, result, details, ip_address, user_agent)
            VALUES (%s, %s, %s, %s, %s::jsonb, %s, %s)
            RETURNING id, scanned_at, result
        """
        result = execute_query(query, (user_id, qr_id, raw_payload, result,
                                      json.dumps(details) if details else None,
                                      ip_address, user_agent), fetch_one=True)
        return dict(result) if result else None
    
    @staticmethod
    def get_by_user(user_id: str, limit: int = 50):
        """Get scan history for a user"""
        query = """
            SELECT * FROM scan_logs 
            WHERE user_id = %s 
            ORDER BY scanned_at DESC 
            LIMIT %s
        """
        results = execute_query(query, (user_id, limit), fetch_all=True)
        return [dict(r) for r in results] if results else []

class RevokedKeys:
    """Revoked keys model"""
    
    @staticmethod
    def create(seller_id: str, public_key: str, reason: str = None, revoked_by: str = None) -> Dict[str, Any]:
        """Create a revoked key record"""
        query = """
            INSERT INTO revoked_keys (seller_id, public_key, reason, revoked_by)
            VALUES (%s, %s, %s, %s)
            RETURNING id, seller_id, revoked_at
        """
        result = execute_query(query, (seller_id, public_key, reason, revoked_by), fetch_one=True)
        return dict(result) if result else None
    
    @staticmethod
    def is_revoked(public_key: str) -> bool:
        """Check if a public key is revoked"""
        query = "SELECT COUNT(*) as count FROM revoked_keys WHERE public_key = %s"
        result = execute_query(query, (public_key,), fetch_one=True)
        return result['count'] > 0 if result else False

class DeviceTokens:
    """Device tokens model for push notifications"""
    
    @staticmethod
    def create(user_id: str, token: str, platform: str = 'web') -> Dict[str, Any]:
        """Create or update device token"""
        query = """
            INSERT INTO device_tokens (user_id, token, platform, last_used_at)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (user_id, token) 
            DO UPDATE SET last_used_at = %s, platform = %s
            RETURNING id, user_id, token, platform
        """
        now = datetime.now(timezone.utc)
        result = execute_query(query, (user_id, token, platform, now, now, platform), fetch_one=True)
        return dict(result) if result else None
    
    @staticmethod
    def get_by_user(user_id: str):
        """Get all device tokens for user"""
        query = "SELECT * FROM device_tokens WHERE user_id = %s"
        results = execute_query(query, (user_id,), fetch_all=True)
        return [dict(r) for r in results] if results else []

class NotificationLogs:
    """Notification logs model"""
    
    @staticmethod
    def create(reminder_id: Optional[str], user_id: str, channel: str,
              status: str, error_message: str = None) -> Dict[str, Any]:
        """Create notification log"""
        query = """
            INSERT INTO notification_logs (reminder_id, user_id, channel, status, error_message)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, sent_at
        """
        result = execute_query(query, (reminder_id, user_id, channel, status, error_message), fetch_one=True)
        return dict(result) if result else None
