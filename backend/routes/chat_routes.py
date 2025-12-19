from flask import Blueprint, request, jsonify, g
from middleware.auth_middleware import token_required
from services.chat_service import send_message, get_chats, get_chat_history
from agents.scheduling_agent import SchedulingAgent
from database.db import users
from bson.objectid import ObjectId

chat_bp = Blueprint('chat', __name__)

# Create ONE scheduling agent instance
scheduling_agent = SchedulingAgent()


@chat_bp.route('/send', methods=['POST'])
@token_required
def send_chat_message(current_user):
    data = request.get_json()
    if not data:
        return jsonify({'message': 'Invalid request body'}), 400
    receiver_id = data.get('receiver_id')
    content = data.get('content')
    sender_id = str(current_user['_id'])
    if not receiver_id or not content:
        return jsonify({'message': 'receiver_id and content are required'}), 400
    try:
        message = send_message(
            sender_id=sender_id,
            receiver_id=receiver_id,
            content=content
        )
    except Exception as e:
        print("Chat send failed:", e)
        return jsonify({"error": "Failed to send message"}), 500

    return jsonify({'message': 'Message sent', 'data': message}), 201


@chat_bp.route('/get/<other_id>/<int:page>', methods=['GET'])
@token_required
def get_chat_messages(current_user, other_id, page):
    user_id = str(current_user['_id'])
    data = get_chats(user_id, other_id, page)
    return jsonify(data), 200


@chat_bp.route('/history/<mentee_id>', methods=['GET'])
@token_required
def get_chat_history_api(current_user, mentee_id):
    if current_user['role'] != 'mentor':
        return jsonify({'message': 'Only mentors can access chat history'}), 403

    mentor_id = str(current_user['_id'])
    history = get_chat_history(mentor_id, mentee_id)
    return jsonify(history), 200
