This is a comprehensive plan to implement the functionalities of the `LearningPathAgent` and `AssessmentAndInterviewAgent` as outlined in your project documentation. The plan focuses on modifying the existing backend codebase.

---

### Part 1: `LearningPathAgent` Implementation

This agent is responsible for creating and managing personalized learning roadmaps.

**1.1. Adaptive Roadmap Adjustment on Assessment Failure (New Feature)**

This feature will notify the mentor when a mentee fails a module assessment, allowing the mentor to intervene.

*   **File to Modify:** `backend/routes/roadmap_routes.py`
*   **Function to Modify:** `submit_mcq_score`
*   **Detailed Steps:**
    1.  In the `submit_mcq_score` function, after calculating the `score`, check if the mentee failed (e.g., `score < 80`).
    2.  If the assessment is failed, a notification will be created and sent to the mentor.
    3.  To do this, you'll need the `mentor_id`. The function already retrieves the `roadmap` document, which contains the necessary IDs.
    4.  A new document will be inserted into the `notifications` collection with the following structure:
        ```python
        # Inside submit_mcq_score, if score < 80:
        
        # (Code to get mentor_id from roadmap document)
        
        notifications.insert_one({
            'type': 'assessment_failed',
            'to_user_id': mentor_id,
            'from_user_id': user_id, # mentee's ID
            'from_username': current_user['username'],
            'roadmap_id': roadmap_id,
            'module_index': module_index,
            'score': score,
            'created_at': datetime.datetime.utcnow(),
            'read': False
        })
        ```

---

### Part 2: `AssessmentAndInterviewAgent` Implementation

This agent handles mentee evaluation through assessments and mock interviews.

**2.1. Autonomous Mock Interview Enhancements**

This involves triggering interviews automatically, making question generation smarter, and providing more detailed feedback.

**2.1.1. Automatic Interview Triggering (New Feature)**

This will trigger an interview when a mentee's progress on their roadmap reaches a specific milestone.

*   **Files to Modify:**
    *   `backend/models/roadmap.py` (for schema changes)
    *   `backend/routes/roadmap_routes.py` (for the trigger logic)
*   **Detailed Steps:**
    1.  **Update Roadmap Schema:** In `backend/models/roadmap.py`, modify the `create_roadmap` method to include new boolean flags to track if an interview has been triggered.
        ```python
        # In RoadmapModel.create_roadmap, add to the roadmap_doc:
        "interview_1_triggered": False,
        "interview_2_triggered": False,
        ```
    2.  **Implement Trigger Logic:** In `backend/routes/roadmap_routes.py`, modify the `toggle_resource_completion` function. This is a good place to check progress since it's called every time a mentee completes a learning resource.
        *   After a resource is marked complete, calculate the mentee's total progress percentage (you can reuse the logic from `backend/routes/dashboard_routes.py`).
        *   Check the `interviewTrigger` field in the roadmap (e.g., `"triggerPoint": "50%"`).
        *   If progress meets the trigger point and the corresponding `interview_1_triggered` flag is `False`, update the flag to `True` in the database and create a notification for the mentor to set the interview's theme.
        ```python
        # In toggle_resource_completion, after successful update:
        # 1. Recalculate progress.
        # 2. Check if progress >= 50% and roadmap['interview_1_triggered'] == False.
        # 3. If true:
        roadmaps.update_one({'_id': ObjectId(roadmap_id)}, {'$set': {'interview_1_triggered': True}})
        notifications.insert_one({
            'type': 'set_interview_theme',
            'to_user_id': mentor_id,
            'from_user_id': user_id, # mentee's ID
            'roadmap_id': roadmap_id,
            'message': f"Your mentee {current_user['username']} has reached 50% progress and is ready for their mock interview. Please set a theme for it.",
            'created_at': datetime.datetime.utcnow(),
            'read': False
        })
        ```

**2.1.2. Adaptive Question Generation (Enhancement)**

This will make the interview questions more relevant by focusing on the mentee's weak areas.

*   **File to Create:** `backend/services/assessment_service.py` could have a new function, or logic can be added directly to the route.
*   **File to Modify:** `backend/routes/roadmap_routes.py`
*   **Function to Modify:** `add_interview`
*   **Detailed Steps:**
    1.  Create a helper function `get_mentee_weak_areas(roadmap_id)` that analyzes the `assessment_scores` within the roadmap document. It should return a list of module titles where the score is below a passing threshold (e.g., 80%).
    2.  In the `add_interview` route, before setting the interview theme, call `get_mentee_weak_areas(roadmap_id)`.
    3.  Combine the mentor-provided `context` with the identified weak areas.
    4.  Update the `interview_theme_1` or `interview_theme_2` field with this enriched context.
        ```python
        # In add_interview route
        weak_areas = get_mentee_weak_areas(roadmap_id) # New function
        weak_areas_str = ", ".join(weak_areas)
        enriched_context = f"Mentor's focus: {context}. Also, probe the mentee's weak areas which include: {weak_areas_str}."
        
        # ... update roadmap with enriched_context ...
        ```

**2.1.3. Detailed Interview Report (Enhancement)**

This will upgrade the current text-based feedback to a structured JSON object.

*   **File to Modify:** `backend/utils/interview_utils.py`
*   **Function to Modify:** `fetch_feedback`
*   **Detailed Steps:**
    1.  Modify the system prompt inside the `fetch_feedback` function to request a structured JSON output.
    2.  **New Prompt:**
        ```python
        system_prompt = f"""
        You are an expert interview coach. Based on the interview transcript, provide detailed feedback as a valid JSON object.
        The JSON object must have this exact structure:
        {{
          "overall_summary": "A brief summary of the performance.",
          "strengths": ["List of identified strengths."],
          "areas_for_improvement": ["List of areas to work on."],
          "confidence_analysis": {{
            "rating": "Low/Medium/High",
            "justification": "Explain the rating, citing examples."
          }},
          "communication_score": {{
            "rating": "1-10",
            "justification": "Rate the clarity and professionalism of their communication."
          }}
        }}

        Interview Transcript:
        {history}
        """
        ```
    3.  The `POST /api/ai/feedback` route in `ai_routes.py` will now receive this JSON. The `RoadmapModel.set_feedback_interview_1` method should be updated to store this JSON object directly instead of a plain string.

---

### Part 3: Proactive Meeting Scheduling (New Feature)

This feature will suggest that the mentor schedule a meeting after the mentee reaches a major milestone.

*   **File to Modify:** `backend/routes/roadmap_routes.py`
*   **Function to Modify:** `submit_mcq_score`
*   **Detailed Steps:**
    1.  In `submit_mcq_score`, after a user passes an assessment (`score >= 80`), determine if a "major milestone" has been reached (e.g., after completing module 4 in an 8-module roadmap).
    2.  If a milestone is reached, create a notification for the mentor suggesting they schedule a meeting.
        ```python
        # Inside submit_mcq_score, if a milestone is reached:
        notifications.insert_one({
            'type': 'milestone_reached_meeting_suggestion',
            'to_user_id': mentor_id,
            'from_user_id': user_id, # mentee's ID
            'roadmap_id': roadmap_id,
            'message': f"Your mentee {current_user['username']} has reached a major milestone. This is a great time to schedule a check-in meeting!",
            'created_at': datetime.datetime.utcnow(),
            'read': False
        })
        ```

This detailed plan provides a clear path to implementing the required features by enhancing your existing backend services and routes.
