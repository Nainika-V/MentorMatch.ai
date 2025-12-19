from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Import routes
from routes.auth_routes import auth_bp
from routes.user_routes import user_bp
from routes.roadmap_routes import roadmap_bp
from routes.chat_routes import chat_bp
from routes.meeting_routes import meeting_bp
from routes.interview_routes import interview_bp
from routes.ai_routes import ai_bp
from routes.notification_routes import notification_bp
from routes.dashboard_routes import dashboard_bp
from routes.scheduling_routes import scheduling_bp
from tasks.schedule_checker import check_inactivity

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"], supports_credentials=True)

# Define a CLI command


@app.cli.command("check-inactivity")
def check_inactivity_command():
    """Checks for mentor-mentee inactivity and triggers scheduling agent."""
    check_inactivity()


# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(user_bp, url_prefix='/api/users')
app.register_blueprint(roadmap_bp, url_prefix='/api/roadmaps')
app.register_blueprint(chat_bp, url_prefix='/api/chat')
app.register_blueprint(meeting_bp, url_prefix='/api/meetings')
app.register_blueprint(interview_bp, url_prefix='/api/interviews')
app.register_blueprint(ai_bp, url_prefix='/api/ai')
app.register_blueprint(notification_bp, url_prefix='/api/notifications')
app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
app.register_blueprint(scheduling_bp, url_prefix="/api/scheduling")


@app.route('/')
def index():
    return jsonify({"message": "Welcome to MentorMatch.ai API"})

# Add route to serve audio files


@app.route('/ai-speech.mp3')
def serve_audio():
    # Adjust the path if your ai-speech.mp3 is saved elsewhere
    return send_from_directory('.', 'ai-speech.mp3')


if __name__ == '__main__':
    app.run(debug=os.environ.get('FLASK_DEBUG', 'True') == 'True')
