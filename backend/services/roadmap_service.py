from models.roadmap import RoadmapModel
from services.ai_service import update_roadmap
import json

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
            updated_roadmap_data = update_roadmap(json.dumps(roadmap),instructions)
            # Replace the old roadmap with the new one
            RoadmapModel.replace_roadmap_by_id(roadmap_id, updated_roadmap_data)
            return updated_roadmap_data, "Roadmap updated based on assessment performance."
   
         except Exception as e:
            print(f"Error suggesting roadmap update: {e}")
            return None, str(e)


    
