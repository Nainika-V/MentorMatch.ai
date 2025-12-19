from database.db import messages, users
from bson.objectid import ObjectId
import datetime

PAGE_SIZE = 20


def send_message(sender_id, receiver_id, content, meta=None, message_type="user", participants_override=None):
    message = {
        'sender_id': sender_id,
        'receiver_id': receiver_id,
        'participants': sorted([str(x) for x in participants_override]) if participants_override else sorted([str(sender_id), str(receiver_id)]),
        'content': content,
        'type': message_type,
        'meta': meta or {},
        'timestamp': datetime.datetime.utcnow()
    }
    result = messages.insert_one(message)
    message['_id'] = str(result.inserted_id)
    return message


def get_chats(user_id, other_id, page=1):
    # Get messages where (sender==user and receiver==other) OR (sender==other and receiver==user)
    # OR system messages where participants contains both users
    query = {
        '$or': [
            {'sender_id': user_id, 'receiver_id': other_id},
            {'sender_id': other_id, 'receiver_id': user_id},
            {'participants': {'$all': [str(user_id), str(other_id)]}}
        ]
    }

    skip = (page - 1) * PAGE_SIZE
    cursor = messages.find(query).sort(
        'timestamp', -1).skip(skip).limit(PAGE_SIZE + 1)
    msgs = list(cursor)
    
    # Get usernames for display, excluding 'system'
    user_ids_set = {msg['sender_id'] for msg in msgs} | {msg['receiver_id'] for msg in msgs}
    valid_user_ids = [uid for uid in user_ids_set if uid != 'system']
    
    user_map = {str(u['_id']): u.get('username', '') for u in users.find(
        {'_id': {'$in': [ObjectId(uid) for uid in valid_user_ids]}})}

    for msg in msgs:
        if msg['sender_id'] == 'system':
            msg['sender'] = 'System'
        else:
            msg['sender'] = user_map.get(msg['sender_id'], 'Unknown')
            
        msg['receiver'] = user_map.get(msg['receiver_id'], 'Unknown')
        msg['_id'] = str(msg['_id'])
        msg['timestamp'] = msg['timestamp'].isoformat()
        
    is_last_page = len(msgs) <= PAGE_SIZE
    # Only reverse the page slice, not the whole result set
    page_msgs = msgs[:PAGE_SIZE][::-1]
    return {
        'messages': page_msgs,  # Oldest first for this page, but latest messages overall
        'isLastPage': is_last_page
    }


def get_chat_history(mentor_id, mentee_id):
    """Get complete chat history between mentor and mentee for AI processing"""
    try:
        print(
            f"Getting chat history for mentor {mentor_id} and mentee {mentee_id}")

        # Get all messages between mentor and mentee (no pagination)
        # FIXED: Use 'messages' collection instead of 'chats'
        chat_messages = list(messages.find({
            '$or': [
                {'sender_id': mentor_id, 'receiver_id': mentee_id},
                {'sender_id': mentee_id, 'receiver_id': mentor_id}
            ]
        }).sort('timestamp', 1))  # Sort by timestamp ascending

        print(f"Found {len(chat_messages)} messages")

        conversation = []
        for msg in chat_messages:
            sender_role = "mentor" if msg['sender_id'] == mentor_id else "mentee"

            # Handle timestamp - ensure it's in the right format
            timestamp = msg['timestamp']
            if hasattr(timestamp, 'isoformat'):
                # If it's a datetime object
                timestamp_str = timestamp.isoformat()
                if not timestamp_str.endswith('Z'):
                    timestamp_str += 'Z'
            else:
                # If it's already a string, ensure it ends with Z
                timestamp_str = str(timestamp)
                if not timestamp_str.endswith('Z'):
                    timestamp_str += 'Z'

            conversation_item = {
                "timestamp": timestamp_str,
                "sender": sender_role,
                "message": msg['content']
            }
            conversation.append(conversation_item)
            print(f"Added conversation item: {conversation_item}")

        result = {
            "mentee_id": mentee_id,
            "conversation": conversation
        }

        print(f"Final chat history result: {result}")
        return result

    except Exception as e:
        print(f"Error getting chat history: {e}")
        import traceback
        traceback.print_exc()
        return {"mentee_id": mentee_id, "conversation": []}
