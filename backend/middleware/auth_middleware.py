from functools import wraps
from flask import request, jsonify, g
from utils.jwt_utils import JWTUtils
from utils.custom_error import CustomError
from models.user import UserModel

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        print("--- Headers:", request.headers)
        print("--- Cookies:", request.cookies)

        # 1. Try to fetch from cookie
        if 'auth_token' in request.cookies:
            token = request.cookies.get('auth_token')

        # 2. Try Authorization header
        elif 'Authorization' in request.headers:
            auth_header = request.headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

        if not token:
            return jsonify({'error': 'Authorization token is missing'}), 401

        try:
            # Verify JWT token
            payload = JWTUtils.verify_token(token)
            user_id = payload.get('user_id')

            if not user_id:
                raise CustomError("Invalid token payload", 401)

            # Retrieve user from database
            current_user = UserModel.get_user_by_id(user_id)
            if not current_user:
                raise CustomError("User not found", 401)

            # Update last login timestamp
            UserModel.update_last_login(user_id)

            # Attach to Flask global context
            g.current_user = current_user

        except CustomError as ce:
            return jsonify({'error': ce.message}), ce.status_code
        except Exception as e:
            return jsonify({'error': 'Token verification failed', 'details': str(e)}), 401

        return f(*args, current_user=current_user, **kwargs)

    return decorated_function


def mentor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(g, 'current_user') or g.current_user.get('role') != 'mentor':
            return jsonify({'error': 'Mentor access required'}), 403
        return f(*args, **kwargs)
    return decorated_function


def mentee_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(g, 'current_user') or g.current_user.get('role') != 'mentee':
            return jsonify({'error': 'Mentee access required'}), 403
        return f(*args, **kwargs)
    return decorated_function


def get_current_user():
    """Get current user object from Flask context."""
    if hasattr(g, 'current_user'):
        return g.current_user
    raise CustomError("User not authenticated", 401)