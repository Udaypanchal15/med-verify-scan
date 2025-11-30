"""
Reminder routes for medicine dosage and expiry reminders
"""
from flask import Blueprint, request, jsonify
from middleware.auth import login_required
from database.models import Reminder
from services.reminder_service import ReminderService
from datetime import datetime
import pytz

reminder_bp = Blueprint('reminder_bp', __name__, url_prefix='/reminders')

@reminder_bp.route('', methods=['POST'])
@login_required
def create_reminder(current_user, user_id):
    """Create a new reminder"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'start_time', 'channel_json']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"{field} is required"}), 400
        
        # Parse start time
        try:
            start_time = datetime.fromisoformat(data['start_time'].replace('Z', '+00:00'))
        except Exception as e:
            return jsonify({"error": f"Invalid start_time format: {str(e)}"}), 400
        
        # Get timezone
        timezone = data.get('timezone', 'UTC')
        
        # Get recurrence rule
        recurrence_rule = data.get('recurrence_rule')  # RFC 5545 format
        
        # Create reminder
        reminder_service = ReminderService()
        reminder = reminder_service.create_reminder(
            user_id=user_id,
            title=data['title'],
            description=data.get('description'),
            channel_json=data['channel_json'],
            recurrence_rule=recurrence_rule,
            start_time=start_time,
            timezone=timezone,
            medicine_id=data.get('medicine_id')
        )
        
        if not reminder:
            return jsonify({"error": "Failed to create reminder"}), 500
        
        return jsonify({
            "message": "Reminder created successfully",
            "data": reminder
        }), 201
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@reminder_bp.route('', methods=['GET'])
@login_required
def get_reminders(current_user, user_id):
    """Get all reminders for user"""
    try:
        active_only = request.args.get('active_only', 'false').lower() == 'true'
        reminders = Reminder.get_by_user(user_id, active_only=active_only)
        
        return jsonify({
            "message": "Reminders retrieved successfully",
            "data": reminders
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@reminder_bp.route('/<reminder_id>', methods=['GET'])
@login_required
def get_reminder(current_user, user_id, reminder_id):
    """Get reminder by ID"""
    try:
        # Would need get_by_id method in Reminder model
        return jsonify({"error": "Not implemented"}), 501
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@reminder_bp.route('/<reminder_id>', methods=['PUT'])
@login_required
def update_reminder(current_user, user_id, reminder_id):
    """Update reminder"""
    try:
        data = request.get_json()
        # Implement update logic
        return jsonify({"error": "Not implemented"}), 501
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@reminder_bp.route('/<reminder_id>', methods=['DELETE'])
@login_required
def delete_reminder(current_user, user_id, reminder_id):
    """Delete/cancel reminder"""
    try:
        # Implement delete logic (set active = false)
        return jsonify({"error": "Not implemented"}), 501
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@reminder_bp.route('/device-token', methods=['POST'])
@login_required
def register_device_token(current_user, user_id):
    """Register device token for push notifications"""
    try:
        data = request.get_json()
        token = data.get('token')
        platform = data.get('platform', 'web')
        
        if not token:
            return jsonify({"error": "Token is required"}), 400
        
        # Store device token
        from database.models import DeviceTokens
        DeviceTokens.create(user_id, token, platform)
        return jsonify({
            "message": "Device token registered successfully"
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
