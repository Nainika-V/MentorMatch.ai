from flask import Blueprint, request, jsonify, g
import datetime
from bson.objectid import ObjectId
from bson.errors import InvalidId

from agents.scheduling_agent import SchedulingAgent
from database.db import roadmaps, users, notifications
from middleware.auth_middleware import token_required
from services.ai_service import generate_roadmap
from services.assessment_service import get_assessment, submit_score
from models.roadmap import RoadmapModel

roadmap_bp = Blueprint('roadmaps', __name__)

scheduling_agent = SchedulingAgent()


@roadmap_bp.route('/', methods=['POST'])
@token_required
def create_roadmap(current_user):
    data = request.get_json()

    mentor_id = data.get('mentor_id')
    mentee_id = data.get('mentee_id')
    title = data.get('title', 'Learning Roadmap')
    description = data.get('description', '')
    skill = data.get('skill', '')

    if not mentor_id or not mentee_id or not skill:
        return jsonify({'message': 'Mentor ID, mentee ID, and skill are required'}), 400

    try:
        # Check if mentor and mentee exist
        mentor = users.find_one({'_id': ObjectId(mentor_id), 'role': 'mentor'})
        mentee = users.find_one({'_id': ObjectId(mentee_id), 'role': 'mentee'})

        if not mentor or not mentee:
            return jsonify({'message': 'Mentor or mentee not found'}), 404

        # Check if current user is either the mentor or mentee
        if str(current_user['_id']) != mentor_id and str(current_user['_id']) != mentee_id:
            return jsonify({'message': 'Unauthorized'}), 403

        # Generate roadmap using AI
        roadmap_content = generate_roadmap(
            skill, mentee['profile'].get('experience_level', 'beginner'))

        # Create roadmap
        new_roadmap = {
            'mentor_id': mentor_id,
            'mentee_id': mentee_id,
            'title': title,
            'description': description,
            'skill': skill,
            'modules': roadmap_content['modules'],
            'created_at': datetime.datetime.utcnow(),
            'updated_at': datetime.datetime.utcnow(),
            'status': 'active'
        }

        result = roadmaps.insert_one(new_roadmap)

        # Create notification for the other user
        notification_to = mentor_id if str(
            current_user['_id']) == mentee_id else mentee_id

        notification = {
            'type': 'roadmap_created',
            'from_user_id': str(current_user['_id']),
            'to_user_id': notification_to,
            'from_username': current_user['username'],
            'roadmap_id': str(result.inserted_id),
            'roadmap_title': title,
            'created_at': datetime.datetime.utcnow(),
            'read': False
        }

        notifications.insert_one(notification)

        return jsonify({
            'message': 'Roadmap created successfully',
            'roadmap_id': str(result.inserted_id)
        }), 201
    except Exception as e:
        return jsonify({'message': f'Error creating roadmap: {str(e)}'}), 500


@roadmap_bp.route('/', methods=['GET'])
@token_required
def get_roadmaps(current_user):
    user_id = str(current_user['_id'])
    role = current_user['role']

    # Get roadmaps based on role
    if role == 'mentor':
        roadmap_list = list(roadmaps.find({'mentor_id': user_id}))
    else:
        roadmap_list = list(roadmaps.find({'mentee_id': user_id}))

    # Convert ObjectId to string
    for roadmap in roadmap_list:
        roadmap['_id'] = str(roadmap['_id'])

    return jsonify(roadmap_list), 200


@roadmap_bp.route('/<roadmap_id>', methods=['GET'])
@token_required
def get_roadmap(current_user, roadmap_id):
    try:
        # Validate roadmap_id format
        if not roadmap_id or roadmap_id == 'null' or roadmap_id == 'undefined':
            return jsonify({'message': 'Invalid roadmap ID'}), 400

        try:
            roadmap = roadmaps.find_one({'_id': ObjectId(roadmap_id)})
        except InvalidId:
            return jsonify({'message': 'Invalid roadmap ID format'}), 400

        if not roadmap:
            return jsonify({'message': 'Roadmap not found'}), 404

        # Check if user is authorized to access this roadmap
        user_id = str(current_user['_id'])

        # Handle both field naming conventions safely
        mentor_id = None
        mentee_id = None

        # Get mentee_id - handle multiple possible locations
        if 'mentee_id' in roadmap:
            mentee_id = str(roadmap['mentee_id'])
        elif 'menteeId' in roadmap:
            if isinstance(roadmap['menteeId'], ObjectId):
                mentee_id = str(roadmap['menteeId'])
            else:
                mentee_id = str(roadmap['menteeId'])

        # Get mentor_id from mentee's profile if not directly in roadmap
        if 'mentor_id' in roadmap:
            mentor_id = str(roadmap['mentor_id'])
        elif 'mentorId' in roadmap:
            if isinstance(roadmap['mentorId'], ObjectId):
                mentor_id = str(roadmap['mentorId'])
            else:
                mentor_id = str(roadmap['mentorId'])
        elif 'approvalStatus' in roadmap and 'mentorId' in roadmap['approvalStatus']:
            if isinstance(roadmap['approvalStatus']['mentorId'], ObjectId):
                mentor_id = str(roadmap['approvalStatus']['mentorId'])
            else:
                mentor_id = str(roadmap['approvalStatus']['mentorId'])
        else:
            # Get mentor_id from mentee's profile
            if mentee_id:
                mentee_doc = users.find_one({'_id': ObjectId(mentee_id)})
                if mentee_doc and mentee_doc.get('mentors'):
                    # Get first mentor
                    mentor_obj_id = mentee_doc['mentors'][0]
                    mentor_id = str(mentor_obj_id) if isinstance(
                        mentor_obj_id, ObjectId) else mentor_obj_id

        print(
            f"Debug: user_id={user_id}, mentor_id={mentor_id}, mentee_id={mentee_id}")

        # Check authorization - ALLOW BOTH MENTOR AND MENTEE ACCESS
        if not mentee_id:
            return jsonify({'message': 'Roadmap missing mentee ID'}), 400

        if user_id != mentor_id and user_id != mentee_id:
            return jsonify({'message': 'Unauthorized access to this roadmap'}), 403

        # Convert main _id to string
        roadmap['_id'] = str(roadmap['_id'])

        # Convert other ObjectIds to strings for consistent response
        def convert_objectids(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if isinstance(value, ObjectId):
                        obj[key] = str(value)
                    elif isinstance(value, (dict, list)):
                        convert_objectids(value)
            elif isinstance(obj, list):
                for item in obj:
                    convert_objectids(item)

        convert_objectids(roadmap)

        # Add assessment scores for each module if they exist
        if 'assessment_scores' in roadmap:
            # Convert assessment scores ObjectIds to strings
            assessment_scores = {}
            for user_id_key, scores in roadmap['assessment_scores'].items():
                assessment_scores[str(user_id_key)] = scores
            roadmap['assessment_scores'] = assessment_scores

        # Only remove questions if user is mentee (mentors can see questions for review)
        if current_user['role'] == 'mentee':
            def remove_questions(obj):
                if isinstance(obj, dict):
                    # Remove question fields but keep assessment_scores
                    obj.pop('questions', None)
                    obj.pop('mcq_questions', None)
                    obj.pop('question_list', None)
                    obj.pop('evaluation', None)  # Remove evaluation questions

                    # Recursively process nested objects
                    for key, value in obj.items():
                        if key != 'assessment_scores':  # Don't remove assessment scores
                            remove_questions(value)
                elif isinstance(obj, list):
                    for item in obj:
                        remove_questions(item)

            remove_questions(roadmap)

        return jsonify(roadmap), 200

    except Exception as e:
        print(f"Error in get_roadmap: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'message': f'Error retrieving roadmap: {str(e)}'}), 500


@roadmap_bp.route('/<roadmap_id>/resource/<resource_id>/toggle', methods=['POST'])
@token_required
def toggle_resource_completion(current_user, roadmap_id, resource_id):
    try:
        data = request.get_json()
        completed = data.get('completed', False)

        roadmap = roadmaps.find_one({'_id': ObjectId(roadmap_id)})

        if not roadmap:
            return jsonify({'message': 'Roadmap not found'}), 404

        # Check if user is authorized (only mentees can toggle resources)
        user_id = str(current_user['_id'])

        # Handle both field naming conventions for mentee_id
        mentee_id = None
        if 'mentee_id' in roadmap:
            mentee_id = str(roadmap['mentee_id'])
        elif 'menteeId' in roadmap:
            if isinstance(roadmap['menteeId'], ObjectId):
                mentee_id = str(roadmap['menteeId'])
            else:
                mentee_id = str(roadmap['menteeId'])

        if not mentee_id or user_id != mentee_id:
            return jsonify({'message': 'Only mentees can toggle resource completion'}), 403

        # Parse resource_id (format: moduleIndex-subtopicIndex-resourceIndex)
        try:
            module_idx, subtopic_idx, resource_idx = map(
                int, resource_id.split('-'))
        except ValueError:
            return jsonify({'message': 'Invalid resource ID format'}), 400

        # Validate indices
        if (module_idx >= len(roadmap['modules']) or
            subtopic_idx >= len(roadmap['modules'][module_idx].get('subtopics', [])) or
                resource_idx >= len(roadmap['modules'][module_idx]['subtopics'][subtopic_idx].get('resources', []))):
            return jsonify({'message': 'Resource not found'}), 404

        # Update the resource completion status
        roadmaps.update_one(
            {'_id': ObjectId(roadmap_id)},
            {'$set': {
                f'modules.{module_idx}.subtopics.{subtopic_idx}.resources.{resource_idx}.completed': completed,
                'updated_at': datetime.datetime.utcnow()
            }}
        )

        return jsonify({'message': 'Resource completion status updated'}), 200

    except Exception as e:
        print(f"Error in toggle_resource_completion: {str(e)}")
        return jsonify({'message': f'Error updating resource: {str(e)}'}), 500


@roadmap_bp.route('/interview/add', methods=['POST'])
@token_required
def add_interview(current_user):
    data = request.get_json()

    roadmap_id = data.get("roadmap_id")
    interview_num = int(data.get("interview_num"))
    context = data.get("context")

    if not roadmap_id or interview_num is None or context is None:
        return jsonify({"message": "roadmap_id, interview_num, and context are required"}), 400

    try:
        # Check if user is authorized (only mentors can set interview context)
        roadmap = roadmaps.find_one({'_id': ObjectId(roadmap_id)})
        if not roadmap:
            return jsonify({"message": "Roadmap not found"}), 404

        user_id = str(current_user['_id'])
        mentor_id = None

        # Get mentee_id first
        mentee_id = None
        if 'mentee_id' in roadmap:
            mentee_id = str(roadmap['mentee_id'])
        elif 'menteeId' in roadmap:
            if isinstance(roadmap['menteeId'], ObjectId):
                mentee_id = str(roadmap['menteeId'])
            else:
                mentee_id = str(roadmap['menteeId'])

        # Try to get mentor_id from roadmap first, then from mentee's profile
        if 'mentor_id' in roadmap:
            mentor_id = str(roadmap['mentor_id'])
        elif 'mentorId' in roadmap:
            if isinstance(roadmap['mentorId'], ObjectId):
                mentor_id = str(roadmap['mentorId'])
            else:
                mentor_id = str(roadmap['mentorId'])
        elif 'approvalStatus' in roadmap and 'mentorId' in roadmap['approvalStatus']:
            if isinstance(roadmap['approvalStatus']['mentorId'], ObjectId):
                mentor_id = str(roadmap['approvalStatus']['mentorId'])
            else:
                mentor_id = str(roadmap['approvalStatus']['mentorId'])
        else:
            # Get mentor_id from mentee's profile
            if mentee_id:
                mentee_doc = users.find_one({'_id': ObjectId(mentee_id)})
                if mentee_doc and mentee_doc.get('mentors'):
                    mentor_obj_id = mentee_doc['mentors'][0]
                    mentor_id = str(mentor_obj_id) if isinstance(
                        mentor_obj_id, ObjectId) else mentor_obj_id

        if not mentor_id or user_id != mentor_id:
            return jsonify({"message": "Only mentors can set interview context"}), 403

        # Set the interview theme
        if interview_num == 1:
            roadmaps.update_one(
                {'_id': ObjectId(roadmap_id)},
                {'$set': {
                    'interview_theme_1': context,
                    'updated_at': datetime.datetime.utcnow()
                }}
            )
        else:
            roadmaps.update_one(
                {'_id': ObjectId(roadmap_id)},
                {'$set': {
                    'interview_theme_2': context,
                    'updated_at': datetime.datetime.utcnow()
                }}
            )

        return jsonify({"message": "Interview theme added successfully"}), 201
    except Exception as e:
        return jsonify({"message": f"Failed to add interview theme: {str(e)}"}), 500


@roadmap_bp.route('/<roadmap_id>/<int:module_index>/assessment/get', methods=['GET'])
@token_required
def get_mcq_assessment(current_user, roadmap_id, module_index):
    """Get MCQ questions for a module assessment"""
    # Check if user has access to this roadmap
    roadmap = roadmaps.find_one({'_id': ObjectId(roadmap_id)})
    if not roadmap:
        return jsonify({"message": "Roadmap not found"}), 404

    # Verify user access (mentee or mentor)
    user_id = str(current_user['_id'])
    mentor_id = None
    mentee_id = None

    # Get mentee_id
    if 'mentee_id' in roadmap:
        mentee_id = str(roadmap['mentee_id'])
    elif 'menteeId' in roadmap:
        mentee_id = str(roadmap['menteeId']) if isinstance(
            roadmap['menteeId'], str) else str(roadmap['menteeId'])

    # Get mentor_id from roadmap or mentee's profile
    if 'mentor_id' in roadmap:
        mentor_id = str(roadmap['mentor_id'])
    elif 'mentorId' in roadmap:
        mentor_id = str(roadmap['mentorId']) if isinstance(
            roadmap['mentorId'], str) else str(roadmap['mentorId'])
    elif 'approvalStatus' in roadmap and 'mentorId' in roadmap['approvalStatus']:
        mentor_id = str(roadmap['approvalStatus']['mentorId'])
    else:
        # Get mentor_id from mentee's profile
        if mentee_id:
            mentee_doc = users.find_one({'_id': ObjectId(mentee_id)})
            if mentee_doc and mentee_doc.get('mentors'):
                mentor_obj_id = mentee_doc['mentors'][0]
                mentor_id = str(mentor_obj_id) if isinstance(
                    mentor_obj_id, ObjectId) else mentor_obj_id

    if user_id != mentor_id and user_id != mentee_id:
        return jsonify({"message": "Unauthorized"}), 403

    questions = get_assessment(roadmap_id, module_index)
    if questions is None:
        return jsonify({"message": "Assessment not found"}), 404

    # For mentees, don't return correct answers
    if current_user['role'] == 'mentee':
        for question in questions:
            question.pop('correct_option', None)

    return jsonify({"questions": questions})


@roadmap_bp.route('/<roadmap_id>/<int:module_index>/assessment/submit', methods=['POST'])
@token_required
def submit_mcq_score(roadmap_id, module_index, current_user):
    """Submit assessment answers and calculate score"""
    if current_user.get('role') != 'mentee':
        return jsonify({"message": "Only mentees can submit assessment scores"}), 403

    data = request.get_json()
    # Array of selected options
    selected_answers = data.get("selected_answers")
    user_id = str(current_user.get('_id'))

    if not selected_answers or not isinstance(selected_answers, list):
        return jsonify({"message": "Selected answers required"}), 400

    # Check if user has access to this roadmap
    roadmap = roadmaps.find_one({'_id': ObjectId(roadmap_id)})
    if not roadmap:
        return jsonify({"message": "Roadmap not found"}), 404

    # Verify mentee access
    mentee_id = None
    if 'mentee_id' in roadmap:
        mentee_id = str(roadmap['mentee_id'])
    elif 'menteeId' in roadmap:
        mentee_id = str(roadmap['menteeId']) if isinstance(
            roadmap['menteeId'], str) else str(roadmap['menteeId'])

    if user_id != mentee_id:
        return jsonify({"message": "Unauthorized"}), 403

    # Get the questions with correct answers
    questions = get_assessment(roadmap_id, module_index)
    if not questions:
        return jsonify({"message": "Assessment not found"}), 404

    if len(selected_answers) != len(questions):
        return jsonify({"message": f"Expected {len(questions)} answers, received {len(selected_answers)}"}), 400

    # Calculate score
    correct_count = 0
    for i, (question, selected_answer) in enumerate(zip(questions, selected_answers)):
        if question.get('correct_option') == selected_answer:
            correct_count += 1

    score = round((correct_count / len(questions)) * 100)

    # Submit the calculated score
    best_score = submit_score(roadmap_id, module_index, user_id, score)
    if best_score is None:
        return jsonify({"message": "Failed to submit score"}), 500
    # --- Notification Logic ---

    # Always send a notification to the mentor about the assessment result
    try:
        # Find mentor to notify
        mentor_id = None
        # Handle various ways mentor ID might be stored
        if 'mentor_id' in roadmap:
            mentor_id = str(roadmap['mentor_id'])
        elif 'approvalStatus' in roadmap and 'mentorId' in roadmap['approvalStatus']:
            mentor_id = str(roadmap['approvalStatus']['mentorId'])

        if mentor_id:
            # If score is low, trigger proactive meeting scheduling
            if score < 80:
                scheduling_agent.proactive_from_assessment(
                    mentor_id=mentor_id,
                    mentee_id=user_id,
                    score=score
                )

            module_title = roadmap.get('modules', [])[
                module_index].get('title', 'a module')
            mentee_name = current_user.get('name', 'Your mentee')

            # Customize notification based on score
            if score >= 80:
                # --- AGENT LOGIC INTEGRATION ---
                # If the user passed, mark the module as complete.
                now = datetime.datetime.utcnow()
                
                # 1. Update the specific module to set completed = True and add completion date
                roadmaps.update_one(
                    {'_id': ObjectId(roadmap_id)},
                    {'$set': {
                        f'modules.{module_index}.completed': True,
                        f'modules.{module_index}.completed_at': now,
                        'updated_at': now
                    }}
                )
                
                # 2. Update the parent roadmap document's timestamp for the stagnation check
                RoadmapModel.update_last_module_completed(roadmap_id)
                # --- END AGENT LOGIC ---

                notification_type = 'assessment_passed'
                message = f"{mentee_name} passed the assessment for '{module_title}' with a score of {score}%."
            else:
                notification_type = 'assessment_failed'
                message = f"{mentee_name} failed the assessment for '{module_title}' with {score}%. A follow-up meeting has been scheduled with your mentor."

            notifications.insert_one({
                'type': notification_type,
                'from_user_id': user_id,
                'to_user_id': mentor_id,
                'from_username': current_user.get('username', 'System'),
                'message': message,  # Generic message field for display
                'roadmap_id': roadmap_id,
                'module_index': module_index,
                'score': score,
                'created_at': datetime.datetime.utcnow(),
                'read': False
            })
    except Exception as e:
        # Log if notification fails, but don't block the response to the user
        print(f"Failed to send notification: {e}")
    # --- End of Notification Logic ---

    return jsonify({
        "message": "Assessment submitted successfully",
        "current_score": score,
        "best_score": best_score,
        "correct_answers": correct_count,
        "total_questions": len(questions),
        "passed": score >= 80
    })


@roadmap_bp.route('/user/<user_id>', methods=['GET'])
@token_required
def get_user_roadmaps(current_user, user_id):
    try:
        current_user_id = str(current_user['_id'])

        # Check authorization - users can only access their own roadmaps
        if current_user_id != user_id:
            return jsonify({'message': 'Unauthorized'}), 403

        role = current_user['role']

        # Build query based on role and handle both field naming conventions
        if role == 'mentor':
            # For mentors, find roadmaps where they are the mentor of the mentee
            # First, find all mentees where this mentor is listed
            mentee_docs = list(users.find({
                'mentors': {'$in': [ObjectId(user_id), user_id]}
            }))

            mentee_ids = [str(mentee['_id']) for mentee in mentee_docs]

            if not mentee_ids:
                return jsonify([]), 200

            # Find roadmaps for these mentees
            query = {
                '$or': [
                    {'mentee_id': {'$in': mentee_ids}},
                    {'menteeId': {'$in': mentee_ids}},
                    {'menteeId': {
                        '$in': [ObjectId(mid) for mid in mentee_ids]}}
                ]
            }
        else:  # mentee
            # Find roadmaps where user is mentee (handle both formats)
            query = {
                '$or': [
                    {'mentee_id': user_id},
                    {'menteeId': user_id},
                    {'menteeId': ObjectId(user_id)}
                ]
            }

        roadmap_list = list(roadmaps.find(query))

        # Convert ObjectIds to strings and remove evaluation questions
        for roadmap in roadmap_list:
            roadmap['_id'] = str(roadmap['_id'])

            # Convert other ObjectIds
            def convert_objectids(obj):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        if isinstance(value, ObjectId):
                            obj[key] = str(value)
                        elif isinstance(value, (dict, list)):
                            convert_objectids(value)
                elif isinstance(obj, list):
                    for item in obj:
                        convert_objectids(item)

            convert_objectids(roadmap)

            # Only remove evaluation questions for mentees
            if role == 'mentee':
                def remove_questions(obj):
                    if isinstance(obj, dict):
                        obj.pop('evaluation', None)
                        for value in obj.values():
                            remove_questions(value)
                    elif isinstance(obj, list):
                        for item in obj:
                            remove_questions(item)

                remove_questions(roadmap)

        return jsonify(roadmap_list), 200

    except Exception as e:
        print(f"Error in get_user_roadmaps: {str(e)}")
        return jsonify({'message': f'Error retrieving roadmaps: {str(e)}'}), 500

# Additional routes...


@roadmap_bp.route('/<roadmap_id>', methods=['PUT'])
@token_required
def update_roadmap(current_user, roadmap_id):
    data = request.get_json()

    try:
        roadmap = roadmaps.find_one({'_id': ObjectId(roadmap_id)})

        if not roadmap:
            return jsonify({'message': 'Roadmap not found'}), 404

        # Check if user is authorized to update this roadmap
        user_id = str(current_user['_id'])
        if roadmap['mentor_id'] != user_id:
            return jsonify({'message': 'Only mentors can update roadmaps'}), 403

        # Update roadmap fields
        update_data = {}

        if 'title' in data:
            update_data['title'] = data['title']
        if 'description' in data:
            update_data['description'] = data['description']
        if 'modules' in data:
            update_data['modules'] = data['modules']
        if 'status' in data:
            update_data['status'] = data['status']

        update_data['updated_at'] = datetime.datetime.utcnow()

        if update_data:
            roadmaps.update_one(
                {'_id': ObjectId(roadmap_id)},
                {'$set': update_data}
            )

        # Create notification for mentee
        notification = {
            'type': 'roadmap_updated',
            'from_user_id': user_id,
            'to_user_id': roadmap['mentee_id'],
            'from_username': current_user['username'],
            'roadmap_id': roadmap_id,
            'roadmap_title': roadmap['title'],
            'created_at': datetime.datetime.utcnow(),
            'read': False
        }

        notifications.insert_one(notification)

        return jsonify({'message': 'Roadmap updated successfully'}), 200
    except:
        return jsonify({'message': 'Invalid roadmap ID'}), 400


@roadmap_bp.route('/request', methods=['POST'])
@token_required
def request_roadmap(current_user):
    data = request.get_json()

    mentor_id = data.get('mentor_id')
    skill = data.get('skill')

    if not mentor_id or not skill:
        return jsonify({'message': 'Mentor ID and skill are required'}), 400

    # Check if current user is a mentee
    if current_user['role'] != 'mentee':
        return jsonify({'message': 'Only mentees can request roadmaps'}), 403

    try:
        # Check if mentor exists
        mentor = users.find_one({'_id': ObjectId(mentor_id), 'role': 'mentor'})

        if not mentor:
            return jsonify({'message': 'Mentor not found'}), 404

        # Create notification for roadmap request
        notification = {
            'type': 'roadmap_request',
            'from_user_id': str(current_user['_id']),
            'to_user_id': mentor_id,
            'from_username': current_user['username'],
            'skill': skill,
            'created_at': datetime.datetime.utcnow(),
            'read': False
        }

        notifications.insert_one(notification)

        return jsonify({'message': 'Roadmap request sent'}), 200
    except:
        return jsonify({'message': 'Invalid mentor ID'}), 400

# --- POST: Mentee gives feedback about Mentor ---


@roadmap_bp.route('/<roadmap_id>/feedback/mentor', methods=['POST'])
@token_required
def mentee_give_feedback(current_user, roadmap_id):
    """Mentee gives feedback about mentor"""
    data = request.get_json()
    rating = data.get('rating')
    text = data.get('text')
    if not rating or not text:
        return jsonify({'message': 'Rating and text are required'}), 400

    roadmap = roadmaps.find_one({'_id': ObjectId(roadmap_id)})
    if not roadmap:
        return jsonify({'message': 'Roadmap not found'}), 404

    mentee_id = str(roadmap.get('mentee_id', roadmap.get('menteeId')))
    if str(current_user['_id']) != mentee_id or current_user['role'] != 'mentee':
        return jsonify({'message': 'Only the mentee can give feedback about the mentor'}), 403

    feedback_obj = {
        'rating': rating,
        'text': text,
        'created_at': datetime.datetime.utcnow()
    }
    RoadmapModel.set_mentor_feedback(roadmap_id, feedback_obj)
    return jsonify({'message': 'Feedback submitted'}), 200

# --- POST: Mentor gives feedback about Mentee ---


@roadmap_bp.route('/<roadmap_id>/feedback/mentee', methods=['POST'])
@token_required
def mentor_give_feedback(current_user, roadmap_id):
    """Mentor gives feedback about mentee"""
    roadmap = roadmaps.find_one({'_id': ObjectId(roadmap_id)})
    if not roadmap:
        return jsonify({'message': 'Roadmap not found'}), 404

    mentee_id = str(roadmap.get('mentee_id', roadmap.get('menteeId')))
    # If not the mentee, must be the mentor
    if str(current_user['_id']) == mentee_id and current_user['role'] == 'mentee':
        return jsonify({'message': 'Only the mentor can give feedback about the mentee'}), 403

    data = request.get_json()
    rating = data.get('rating')
    text = data.get('text')
    if not rating or not text:
        return jsonify({'message': 'Rating and text are required'}), 400

    feedback_obj = {
        'rating': rating,
        'text': text,
        'created_at': datetime.datetime.utcnow()
    }
    RoadmapModel.set_mentee_feedback(roadmap_id, feedback_obj)
    return jsonify({'message': 'Feedback submitted'}), 200

# --- GET: Feedback about the mentor (what the mentee wrote) ---


@roadmap_bp.route('/<roadmap_id>/feedback/mentor', methods=['GET'])
@token_required
def get_feedback_about_mentor(current_user, roadmap_id):
    """Get feedback about the mentor (mentee's feedback)"""
    roadmap = roadmaps.find_one({'_id': ObjectId(roadmap_id)})
    if not roadmap:
        return jsonify({'message': 'Roadmap not found'}), 404

    mentee_id = str(roadmap.get('mentee_id', roadmap.get('menteeId')))
    user_id = str(current_user['_id'])
    if user_id != mentee_id and current_user['role'] != 'mentor':
        return jsonify({'message': 'Unauthorized'}), 403

    feedback = roadmap.get('feedback', {}).get('mentee_to_mentor')
    return jsonify({'feedback': feedback}), 200

# --- GET: Feedback about the mentee (what the mentor wrote) ---


@roadmap_bp.route('/<roadmap_id>/feedback/mentee', methods=['GET'])
@token_required
def get_feedback_about_mentee(current_user, roadmap_id):
    """Get feedback about the mentee (mentor's feedback)"""
    roadmap = roadmaps.find_one({'_id': ObjectId(roadmap_id)})
    if not roadmap:
        return jsonify({'message': 'Roadmap not found'}), 404

    mentee_id = str(roadmap.get('mentee_id', roadmap.get('menteeId')))
    user_id = str(current_user['_id'])
    if user_id != mentee_id and current_user['role'] != 'mentor':
        return jsonify({'message': 'Unauthorized'}), 403

    feedback = roadmap.get('feedback', {}).get('mentor_to_mentee')
    return jsonify({'feedback': feedback}), 200


@roadmap_bp.route('/roadmap-id', methods=['GET'])
@token_required
def get_roadmap_id(current_user):
    """Return the active roadmap id for the current user (mentee only)"""
    user_id = str(current_user['_id'])
    role = current_user['role']
    if role != 'mentee':
        return jsonify({'roadmap_id': None}), 200

    roadmap = roadmaps.find_one({
        '$or': [
            {'mentee_id': user_id},
            {'menteeId': user_id},
            {'menteeId': ObjectId(user_id)}
        ],
        'status': {'$in': ['active', 'in-progress']}
    })
    if roadmap:
        return jsonify({'roadmap_id': str(roadmap['_id'])}), 200
    return jsonify({'roadmap_id': None}), 200
