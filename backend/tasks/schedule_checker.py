import os
import sys
import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import users
from agents.scheduling_agent import SchedulingAgent

def check_inactivity():
    """
    Iterates through all mentee-mentor pairs and checks for inactivity.
    If a pair has been inactive for too long, it triggers the scheduling agent
    to create a new meeting request.
    """
    print("Starting inactivity check...")
    scheduling_agent = SchedulingAgent()
    
    # In this system, mentees are linked to mentors.
    # So we find all mentees who have an assigned mentor.
    mentees = users.find({"role": "mentee", "mentor_id": {"$exists": True}})
    
    for mentee in mentees:
        mentee_id = str(mentee["_id"])
        mentor_id = str(mentee["mentor_id"])
        
        print(f"Checking pair: Mentor ({mentor_id}) - Mentee ({mentee_id})")
        
        try:
            scheduling_agent.proactive_from_inactivity(
                mentor_id=mentor_id,
                mentee_id=mentee_id
            )
        except Exception as e:
            print(f"Error checking inactivity for pair {mentor_id}-{mentee_id}: {e}")
            
    print("Inactivity check finished.")

if __name__ == "__main__":
    check_inactivity()
