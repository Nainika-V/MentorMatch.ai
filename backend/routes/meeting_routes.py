from flask import Blueprint, request, jsonify
import datetime
from bson.objectid import ObjectId
import uuid

from database.db import meetings, users, notifications
from middleware.auth_middleware import token_required
from services.google_meet_service import create_google_meet

meeting_bp = Blueprint('meetings', __name__)

@meeting_bp.route('/', methods=['POST'])
@token_required
def schedule_meeting(current_user):
    data = request.get_json()
    mentor_id = str(current_user['_id'])
    mentee_id = data.get('mentee_id')
    title = data.get('title')
    description = data.get('description', '')
    meeting_link = data.get('meeting_link')
    start_time = data.get('start_time')
    end_time = data.get('end_time')

    if current_user['role'] != 'mentor':
        return jsonify({'message': 'Only mentors can schedule meetings'}), 403

    if not mentee_id or not title or not meeting_link or not start_time or not end_time:
        return jsonify({'message': 'Missing required fields'}), 400

    try:
        mentee = users.find_one({'_id': ObjectId(mentee_id), 'role': 'mentee'})
        if not mentee:
            return jsonify({'message': 'Mentee not found'}), 404

        start_dt = datetime.datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        end_dt = datetime.datetime.fromisoformat(end_time.replace('Z', '+00:00'))

        meeting = {
            'mentor_id': mentor_id,
            'mentee_id': mentee_id,
            'title': title,
            'description': description,
            'meeting_link': meeting_link,
            'start_time': start_dt,
            'end_time': end_dt,
            'status': 'scheduled',
            'created_at': datetime.datetime.utcnow()
        }
        result = meetings.insert_one(meeting)

        notification = {
            'type': 'meeting_scheduled',
            'from_user_id': mentor_id,
            'to_user_id': mentee_id,
            'meeting_id': str(result.inserted_id),
            'meeting_title': title,
            'meeting_time': start_time,
            'created_at': datetime.datetime.utcnow(),
            'read': False
        }
        notifications.insert_one(notification)

        return jsonify({'message': 'Meeting scheduled successfully', 'meeting_id': str(result.inserted_id)}), 201
    except Exception as e:
        return jsonify({'message': f'Error scheduling meeting: {str(e)}'}), 500

@meeting_bp.route('/', methods=['GET'])
@token_required
def get_meetings(current_user):
    user_id = str(current_user['_id'])
    meeting_list = list(meetings.find({
        '$or': [
            {'mentor_id': user_id},
            {'mentee_id': user_id}
        ]
    }).sort('start_time', 1))

    result = []
    for meeting in meeting_list:
        if meeting['mentor_id'] == user_id:
            other_id = meeting['mentee_id']
            other = users.find_one({'_id': ObjectId(other_id)})
        else:
            other_id = meeting['mentor_id']
            other = users.find_one({'_id': ObjectId(other_id)})

        result.append({
            "meeting_id": str(meeting['_id']),
            "title": meeting.get('title', 'Scheduled Meeting'),
            "description": meeting.get('description', ''),
            "meeting_link": meeting.get('meeting_link', ''),
            "start_time": meeting['start_time'].isoformat(),
            "end_time": meeting['end_time'].isoformat(),
            "status": meeting.get('status', ''),
            "with": {
                "id": other_id,
                "name": other.get('name', '') if other else '',
                "role": other.get('role', '') if other else ''
            }
        })
    return jsonify(result), 200

@meeting_bp.route('/<meeting_id>', methods=['GET'])
@token_required
def get_meeting(current_user, meeting_id):
    user_id = str(current_user['_id'])
    
    try:
        # Get meeting
        meeting = meetings.find_one({'_id': ObjectId(meeting_id)})
        
        if not meeting:
            return jsonify({'message': 'Meeting not found'}), 404
        
        # Check if user is a participant
        if meeting['mentor_id'] != user_id and meeting['mentee_id'] != user_id:
            return jsonify({'message': 'Unauthorized'}), 403
        
        # Convert ObjectId to string and format dates
        meeting['_id'] = str(meeting['_id'])
        meeting['start_time'] = meeting['start_time'].isoformat()
        meeting['end_time'] = meeting['end_time'].isoformat()
        meeting['created_at'] = meeting['created_at'].isoformat()
        
        return jsonify(meeting), 200
    except:
        return jsonify({'message': 'Invalid meeting ID'}), 400

@meeting_bp.route('/<meeting_id>', methods=['PUT'])
@token_required
def update_meeting(current_user, meeting_id):
    user_id = str(current_user['_id'])
    data = request.get_json()

    try:
        meeting = meetings.find_one({'_id': ObjectId(meeting_id)})
        if not meeting:
            return jsonify({'message': 'Meeting not found'}), 404

        # Only mentor can update
        if meeting['mentor_id'] != user_id or current_user['role'] != 'mentor':
            return jsonify({'message': 'Only the mentor can update this meeting'}), 403

        update_data = {}
        if 'title' in data:
            update_data['title'] = data['title']
        if 'description' in data:
            update_data['description'] = data['description']
        if 'meeting_link' in data:
            update_data['meeting_link'] = data['meeting_link']
        if 'start_time' in data:
            update_data['start_time'] = datetime.datetime.fromisoformat(data['start_time'])
        if 'end_time' in data:
            update_data['end_time'] = datetime.datetime.fromisoformat(data['end_time'])
        if 'status' in data:
            update_data['status'] = data['status']

        if update_data:
            meetings.update_one({'_id': ObjectId(meeting_id)}, {'$set': update_data})

        # Notify mentee
        notification = {
            'type': 'meeting_updated',
            'from_user_id': user_id,
            'to_user_id': meeting['mentee_id'],
            'meeting_id': meeting_id,
            'meeting_title': update_data.get('title', meeting['title']),
            'created_at': datetime.datetime.utcnow(),
            'read': False
        }
        notifications.insert_one(notification)

        return jsonify({'message': 'Meeting updated successfully'}), 200
    except ValueError:
        return jsonify({'message': 'Invalid date format'}), 400
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 400

@meeting_bp.route('/<meeting_id>', methods=['DELETE'])
@token_required
def cancel_meeting(current_user, meeting_id):
    user_id = str(current_user['_id'])

    try:
        meeting = meetings.find_one({'_id': ObjectId(meeting_id)})
        if not meeting:
            return jsonify({'message': 'Meeting not found'}), 404

        # Only mentor can cancel
        if meeting['mentor_id'] != user_id or current_user['role'] != 'mentor':
            return jsonify({'message': 'Only the mentor can cancel this meeting'}), 403

        meetings.update_one(
            {'_id': ObjectId(meeting_id)},
            {'$set': {'status': 'cancelled'}}
        )

        # Notify mentee
        notification = {
            'type': 'meeting_cancelled',
            'from_user_id': user_id,
            'to_user_id': meeting['mentee_id'],
            'meeting_title': meeting.get('title', 'Scheduled Meeting'),
            'meeting_id': meeting_id,
            'created_at': datetime.datetime.utcnow(),
            'read': False
        }
        notifications.insert_one(notification)

        return jsonify({'message': 'Meeting cancelled successfully'}), 200
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 400

@meeting_bp.route('/upcoming', methods=['GET'])
@token_required
def get_upcoming_meetings(current_user):
    user_id = str(current_user['_id'])
    now = datetime.datetime.utcnow()

    meetings_list = list(meetings.find({
        '$or': [
            {'mentor_id': user_id},
            {'mentee_id': user_id}
        ],
        'start_time': {'$gte': now},
        'status': 'scheduled'
    }).sort('start_time', 1))

    result = []
    for meeting in meetings_list:
        if meeting['mentor_id'] == user_id:
            other_id = meeting['mentee_id']
            other = users.find_one({'_id': ObjectId(other_id)})
        else:
            other_id = meeting['mentor_id']
            other = users.find_one({'_id': ObjectId(other_id)})

        result.append({
            "meeting_id": str(meeting['_id']),
            "title": meeting.get('title', 'Scheduled Meeting'),
            "description": meeting.get('description', ''),
            "meeting_link": meeting.get('meeting_link', ''),
            "start_time": meeting['start_time'].isoformat(),
            "end_time": meeting['end_time'].isoformat(),
            "with": {
                "id": other_id,
                "name": other.get('name', '') if other else '',
                "role": other.get('role', '') if other else ''
            }
        })

    return jsonify(result), 200

@meeting_bp.route('/past', methods=['GET'])
@token_required
def get_past_meetings(current_user):
    user_id = str(current_user['_id'])
    now = datetime.datetime.utcnow()

    meetings_list = list(meetings.find({
        '$or': [
            {'mentor_id': user_id},
            {'mentee_id': user_id}
        ],
        'end_time': {'$lt': now}
    }).sort('start_time', -1))

    result = []
    for meeting in meetings_list:
        if meeting['mentor_id'] == user_id:
            other_id = meeting['mentee_id']
            other = users.find_one({'_id': ObjectId(other_id)})
        else:
            other_id = meeting['mentor_id']
            other = users.find_one({'_id': ObjectId(other_id)})

        result.append({
            "meeting_id": str(meeting['_id']),
            "title": meeting.get('title', 'Scheduled Meeting'),
            "description": meeting.get('description', ''),
            "meeting_link": meeting.get('meeting_link', ''),
            "start_time": meeting['start_time'].isoformat(),
            "end_time": meeting['end_time'].isoformat(),
            "status": meeting.get('status', ''),
            "with": {
                "id": other_id,
                "name": other.get('name', '') if other else '',
                "role": other.get('role', '') if other else ''
            }
        })

    return jsonify(result), 200

@meeting_bp.route('/current', methods=['GET'])
@token_required
def get_current_meetings(current_user):
    user_id = str(current_user['_id'])
    now = datetime.datetime.utcnow()

    meetings_list = list(meetings.find({
        '$or': [
            {'mentor_id': user_id},
            {'mentee_id': user_id}
        ],
        'start_time': {'$lte': now},
        'end_time': {'$gte': now},
        'status': 'scheduled'
    }).sort('start_time', 1))

    result = []
    for meeting in meetings_list:
        if meeting['mentor_id'] == user_id:
            other_id = meeting['mentee_id']
            other = users.find_one({'_id': ObjectId(other_id)})
        else:
            other_id = meeting['mentor_id']
            other = users.find_one({'_id': ObjectId(other_id)})

        result.append({
            "meeting_id": str(meeting['_id']),
            "title": meeting.get('title', 'Scheduled Meeting'),
            "description": meeting.get('description', ''),
            "meeting_link": meeting.get('meeting_link', ''),
            "start_time": meeting['start_time'].isoformat(),
            "end_time": meeting['end_time'].isoformat(),
            "status": meeting.get('status', ''),
            "with": {
                "id": other_id,
                "name": other.get('name', '') if other else '',
                "role": other.get('role', '') if other else ''
            }
        })

    return jsonify(result), 200
