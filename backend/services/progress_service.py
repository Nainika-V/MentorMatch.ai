from database.db import users, roadmaps, notifications
from bson.objectid import ObjectId
from datetime import datetime, timedelta

def get_active_mentees_with_roadmaps():
    """
    Fetches all active mentees who have an 'in-progress' roadmap.
    Returns a list of user documents, each with their roadmap embedded.
    """
    pipeline = [
        {
            '$match': {
                'role': 'mentee'
            }
        },
        {
            '$lookup': {
                'from': 'roadmaps',
                'localField': 'roadmap_id',
                'foreignField': '_id',
                'as': 'roadmap_info'
            }
        },
        {
            '$unwind': '$roadmap_info'
        },
        {
            '$match': {
                'roadmap_info.status': 'in-progress'
            }
        }
    ]
    return list(users.aggregate(pipeline))

def create_notification(user_id, message):
    """
    Creates a new notification for a given user.
    """
    notification_doc = {
        "userId": ObjectId(user_id),
        "message": message,
        "read": False,
        "created_at": datetime.utcnow()
    }
    return notifications.insert_one(notification_doc)

def get_recently_completed_modules(roadmap, since_hours=24):
    """
    Checks a roadmap for modules completed within the last N hours.
    """
    recently_completed = []
    threshold = datetime.utcnow() - timedelta(hours=since_hours)
    
    for module in roadmap.get('modules', []):
        # This assumes 'completed_at' is stored when a module is marked complete.
        # We will need to ensure this is implemented where modules are updated.
        if module.get('completed') and module.get('completed_at') and module.get('completed_at') > threshold:
            recently_completed.append(module)
            
    return recently_completed
