from bson.objectid import ObjectId
from datetime import datetime
from database.db import roadmaps

class RoadmapModel:
    @staticmethod
    def create_roadmap(mentee_id, mentor_id, duration_weeks, modules,
                       interview_type="progress_based", trigger_point="50%") -> dict:
        now = datetime.utcnow()
        roadmap_doc = {
            "menteeId": ObjectId(mentee_id),
            "status": "in-progress",
            "durationWeeks": duration_weeks,
            "approvalStatus": {
                "mentorId": ObjectId(mentor_id),
                "status": "pending",
                "comments": ""
            },
            "interviewTrigger": {
                "type": interview_type,
                "triggerPoint": trigger_point
            },
            "modules": modules,
            "created_at": now,
            "updated_at": now,
            "last_module_completed_at": now  # Initialize on creation
        }

        result = roadmaps.insert_one(roadmap_doc)
        return roadmaps.find_one({"_id": result.inserted_id})

    @staticmethod
    def update_last_module_completed(roadmap_id):
        """Update the last_module_completed_at timestamp for a roadmap"""
        return roadmaps.update_one(
            {"_id": ObjectId(roadmap_id)},
            {"$set": {"last_module_completed_at": datetime.utcnow()}}
        )

    @staticmethod
    def get_roadmaps_by_mentee(mentee_id):
        return list(roadmaps.find({"menteeId": ObjectId(mentee_id)}))


    @staticmethod
    def update_roadmap_status(roadmap_id, new_status):
        return roadmaps.update_one(
            {"_id": ObjectId(roadmap_id)},
            {"$set": {"status": new_status, "updated_at": datetime.utcnow()}}
        )
    
    @staticmethod
    def set_interview_theme_1(roadmap_id, theme_value):
        return roadmaps.update_one(
            {"_id": ObjectId(roadmap_id)},
            {
                "$set": {
                    "interview_theme_1": theme_value,
                    "updated_at": datetime.utcnow()
                }
            }
        )
    
    @staticmethod
    def set_feedback_interview_1(roadmap_id, feedback):
        return roadmaps.update_one(
            {"_id": ObjectId(roadmap_id)},
            {
                "$set": {
                    "interview_feedback_1": feedback,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        

    @staticmethod
    def set_feedback_interview_2(roadmap_id, feedback):
        return roadmaps.update_one(
            {"_id": ObjectId(roadmap_id)},
            {
                "$set": {
                    "interview_feedback_2": feedback,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        

    
    @staticmethod
    def set_interview_theme_2(roadmap_id, theme_value):
        return roadmaps.update_one(
            {"_id": ObjectId(roadmap_id)},
            {
                "$set": {
                    "interview_theme_2": theme_value,
                    "updated_at": datetime.utcnow()
                }
            }
        )
    
    @staticmethod
    def get_interview_1(roadmap_id):
        result = roadmaps.find_one(
            {"_id": ObjectId(roadmap_id)},
            {"_id": 0, "interview_theme_1": 1, "goal": 1}
        )
        return result


    @staticmethod
    def get_interview_2(roadmap_id):
        result = roadmaps.find_one(
            {"_id": ObjectId(roadmap_id)},
            {"_id": 0, "interview_theme_2": 1, "goal": 1}
        )
        return result
    
    @staticmethod
    def replace_roadmap_by_id(roadmap_id, updated_roadmap_data: dict):
        try:
            updated_roadmap_data['_id'] = ObjectId(roadmap_id)
            updated_roadmap_data['updated_at'] = datetime.utcnow()

            existing = roadmaps.find_one({"_id": ObjectId(roadmap_id)})
            if existing and 'created_at' in existing:
                updated_roadmap_data['created_at'] = existing['created_at']
            else:
                updated_roadmap_data['created_at'] = datetime.utcnow()

            # Replace document
            result = roadmaps.replace_one({"_id": ObjectId(roadmap_id)}, updated_roadmap_data)
            return result.modified_count > 0

        except Exception as e:
            print(f"Error replacing roadmap: {e}")
            return False

    @staticmethod
    def get_roadmap_as_dict_for_update(roadmap_id):
        try:
            roadmap = roadmaps.find_one({"_id": ObjectId(roadmap_id)})
            if not roadmap:
                return None

            roadmap.pop('_id', None)
            return roadmap

        except Exception as e:
            print(f"Error fetching roadmap: {e}")
            return None
    
    @staticmethod
    def set_mentee_feedback(roadmap_id, feedback):
        """Mentor gives feedback about mentee"""
        return roadmaps.update_one(
            {"_id": ObjectId(roadmap_id)},
            {"$set": {
                "feedback.mentor_to_mentee": feedback,
                "updated_at": datetime.utcnow()
            }}
        )

    @staticmethod
    def set_mentor_feedback(roadmap_id, feedback):
        """Mentee gives feedback about mentor"""
        return roadmaps.update_one(
            {"_id": ObjectId(roadmap_id)},
            {"$set": {
                "feedback.mentee_to_mentor": feedback,
                "updated_at": datetime.utcnow()
            }}
        )