
from bson.objectid import ObjectId
from database.db import notifications, users
from datetime import datetime

def create_notification(to_user_id, notification_type, message, from_user_id=None, roadmap_id=None, module_index=None, score=None):
    """
    Creates a notification and saves it to the database.
    """
    from_user = users.find_one({'_id': ObjectId(from_user_id)}) if from_user_id else None
    
    notification_data = {
        'to_user_id': str(to_user_id),
        'from_user_id': str(from_user_id) if from_user_id else None,
        'from_username': from_user['name'] if from_user else 'System',
        'type': notification_type,
        'message': message,
        'read': False,
        'created_at': datetime.utcnow()
    }
    
    if roadmap_id:
        notification_data['roadmap_id'] = str(roadmap_id)
    if module_index is not None:
        notification_data['module_index'] = int(module_index)
    if score is not None:
        notification_data['score'] = score
        
    result = notifications.insert_one(notification_data)
    return str(result.inserted_id)
