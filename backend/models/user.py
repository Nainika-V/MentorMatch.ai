from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from database.db import users

class UserModel:
    @staticmethod
    def create_user(user_data):
        """Create a new user in the database"""
        now = datetime.utcnow()
        user_data['created_at'] = now
        user_data['updated_at'] = now
        user_data['last_login_at'] = now  # Set last login on creation

        # Set default values based on role
        if user_data['role'] == 'mentor':
            user_data.setdefault('mentees', [])
            user_data.setdefault('profile', {
                'skills': [],
                'experience': '',
                'mentoring_style': '',
                'availability': [],
                'languages': [],
                'bio': '',
                'profile_picture': ''
            })
        else:  # mentee
            user_data.setdefault('mentors', [])
            user_data.setdefault('profile', {
                'goals': [],
                'learning_style': '',
                'availability': [],
                'languages': [],
                'bio': '',
                'profile_picture': '',
                'experience_level': 'beginner'
            })

        result = users.insert_one(user_data)
        return users.find_one({'_id': result.inserted_id})

    @staticmethod
    def update_last_login(user_id):
        """Update the last_login_at timestamp for a user"""
        return users.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'last_login_at': datetime.utcnow()}}
        )


    @staticmethod
    def get_user_by_email(email):
        """Get user by email"""
        return users.find_one({'email': email})

    @staticmethod
    def get_user_by_email_with_auth(email):
        """Get user by email including password hash"""
        return users.find_one({'email': email})

    @staticmethod
    def get_user_by_id(user_id):
        """Get user by ID"""
        try:
            return users.find_one({'_id': ObjectId(user_id)})
        except:
            return None

    @staticmethod
    def update_user(user_id, update_data):
        """Update user data"""
        update_data['updated_at'] = datetime.utcnow()
        return users.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': update_data}
        )

    @staticmethod
    def delete_user(user_id):
        """Delete user"""
        return users.delete_one({'_id': ObjectId(user_id)})
    
    @staticmethod
    def get_all_mentors():
        """Get all users with role 'mentor'"""
        return list(users.find({'role': 'mentor'}))
    
    @staticmethod
    def link_mentor_and_mentee(mentor_id: str, mentee_id: str):
        """Add a mentee to a mentor's list and a mentor to a mentee's list"""
        try:
            mentor = users.find_one({'_id': ObjectId(mentor_id), 'role': 'mentor'})
            mentee = users.find_one({'_id': ObjectId(mentee_id), 'role': 'mentee'})

            if not mentor or not mentee:
                print("Invalid mentor or mentee ID")
                return False

            # Update mentor: add mentee_id to `mentees` if not already present
            users.update_one(
                {'_id': ObjectId(mentor_id)},
                {'$addToSet': {'mentees': ObjectId(mentee_id)}, '$set': {'updated_at': datetime.utcnow()}}
            )

            # Update mentee: add mentor_id to `mentors` if not already present
            users.update_one(
                {'_id': ObjectId(mentee_id)},
                {'$addToSet': {'mentors': ObjectId(mentor_id)}, '$set': {'updated_at': datetime.utcnow()}}
            )

            return True

        except Exception as e:
            print(f"Error linking mentor and mentee: {e}")
            return False
    
    @staticmethod
    def add_roadmap_id_to_user(user_id, roadmap_id):
        """Add or update roadmap_id field in user"""
        try:
            return users.update_one(
                {'_id': ObjectId(user_id)},
                {
                    '$set': {
                        'roadmap_id': ObjectId(roadmap_id),
                        'updated_at': datetime.utcnow()
                    }
                }
            )
        except Exception as e:
            print(f"Error adding roadmap_id to user: {e}")
            return None

    @staticmethod
    def get_user_roadmap_id(user_id):
        """Fetch roadmap_id from user document if exists"""
        try:
            user = users.find_one(
                {'_id': ObjectId(user_id)},
                {'roadmap_id': 1}
            )
            return str(user.get('roadmap_id')) if user and 'roadmap_id' in user else None
        except Exception as e:
            print(f"Error fetching roadmap_id: {e}")
            return None




# Create indexes for better performance
# Indexes are now created in database/db.py
# users.create_index('email', unique=True)
# users.create_index('username', unique=True)
