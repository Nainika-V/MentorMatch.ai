from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get MongoDB connection string from environment variables
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'MentorMatch')

# Create MongoDB client
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# Define collections
users = db.users
roadmaps = db.roadmaps
chats = db.chats
meetings = db.meetings
skills = db.skills
languages = db.languages
interview_questions = db.interview_questions
notifications = db.notifications
ai_learning_data = db.ai_learning_data
messages = db.messages
meeting_requests = db.meeting_requests

# Create indexes for better query performance
users.create_index('email', unique=True)
users.create_index('username', unique=True)
roadmaps.create_index([('mentor_id', 1), ('mentee_id', 1)])
chats.create_index([('mentor_id', 1), ('mentee_id', 1)])
meetings.create_index([('mentor_id', 1), ('mentee_id', 1)])
messages.create_index(
    [('sender_id', 1), ('receiver_id', 1), ('timestamp', -1)])
meeting_requests.create_index(
    [('mentor_id', 1), ('mentee_id', 1), ('status', 1)]
)
