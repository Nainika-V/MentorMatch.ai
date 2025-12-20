from models.roadmap import RoadmapModel
from services.ai_service import update_roadmap
import json
from bson import ObjectId
from datetime import datetime
from database.db import pending_roadmap_updates, roadmaps

def make_serializable(obj):
    if isinstance(obj, list):
        return [make_serializable(item) for item in obj]
    if isinstance(obj, dict):
        return {key: make_serializable(value) for key, value in obj.items()}
    if isinstance(obj, ObjectId):
        return str(obj)
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj

def suggest_roadmap_update_from_assessment(roadmap_id: str, 
      module_index: int, score: int, questions: list, answers: list):
         
         """
         If an assessment score is low, this function generates a
      suggestion
         to update the roadmap and applies it.
         """
         if score >= 80:
            return None, "Score is high, no update needed."
    
         try:
            roadmap = RoadmapModel.get_roadmap_as_dict_for_update(roadmap_id)
            if not roadmap:
                return None, "Roadmap not found."
    
            module_title = roadmap.get("modules", [])[module_index].get("title", "this module")
    
            incorrect_answers = []
            for i, question in enumerate(questions):
                if answers[i] != question.get("correct_option"):
                    incorrect_answers.append(question.get("question"))
            instructions = (f"The mentee scored {score}% on the assessment for the module '{module_title}'. "
                            f"They struggled with questions about: {', '.join(incorrect_answers)}. ""Please review the module's subtopics and resources. Add more foundational content, "
                            "or break down complex topics to help the mentee better understand these areas. ""You may add new subtopics or suggest better resources.")

             # Use the existing AI service to update the roadmap
            roadmap_serializable = make_serializable(roadmap)
            updated_roadmap_data = update_roadmap(json.dumps(roadmap_serializable),instructions)
            # Replace the old roadmap with the new one
            RoadmapModel.replace_roadmap_by_id(roadmap_id, updated_roadmap_data)
            return updated_roadmap_data, "Roadmap updated based on assessment performance."
   
         except Exception as e:
            print(f"Error suggesting roadmap update: {e}")
            return None, str(e)

def create_pending_roadmap_update(roadmap_id, suggested_changes):
    """
    Creates a new pending roadmap update record in the database.
    """
    pending_update = {
        "roadmap_id": ObjectId(roadmap_id),
        "suggested_changes": suggested_changes,
        "status": "pending",
        "created_at": datetime.utcnow()
    }
    result = pending_roadmap_updates.insert_one(pending_update)
    return result.inserted_id

def apply_roadmap_update(roadmap_id, suggested_changes):
    """
    Applies the suggested changes to the roadmap.
    """
    roadmaps.update_one(
        {'_id': ObjectId(roadmap_id)},
        {'$set': {
            'modules': suggested_changes['modules'],
            'updated_at': datetime.utcnow()
        }}
    )


    
