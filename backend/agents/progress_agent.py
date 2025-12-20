import os
import sys
from datetime import datetime, timedelta

# --- Path Correction for Direct Execution ---
# This allows the script to be run directly from the project root for testing
if __name__ == '__main__':
    # Get the absolute path of the script's directory (e.g., /path/to/backend/agents)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Get the path to the 'backend' directory (one level up)
    backend_dir = os.path.dirname(script_dir)
    # Add the backend directory to the Python path
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)

from services import progress_service


# --- Agent Configuration ---
INACTIVITY_THRESHOLD_DAYS = 5
STAGNATION_THRESHOLD_DAYS = 7
MILESTONE_CHECK_HOURS = 24


# --- Notification Templates ---
TEMPLATES = {
    "inactivity": "Hi {mentee_name}, we've missed you! Just a friendly nudge to check back in on your roadmap when you have a moment.",
    "stagnation": "Hi {mentee_name}, it's been a little while since you completed a module. Is there anything we can help with to get you started on '{next_module_title}'?",
    "milestone": "Great job, {mentee_name}! You've just completed the module: '{module_title}'. Keep up the fantastic momentum!"
}

def get_next_incomplete_module(roadmap):
    """Finds the first module in a roadmap that is not marked as complete."""
    for module in roadmap.get('modules', []):
        if not module.get('completed', False):
            return module
    return None

def check_all_mentees_progress():
    """
    The main function for the Progress & Accountability Agent.
    It checks all active mentees for inactivity, stagnation, and recent milestones.
    """
    print(f"[{datetime.utcnow()}] Running Progress & Accountability Agent...")
    
    try:
        active_mentees = progress_service.get_active_mentees_with_roadmaps()
        print(f"Found {len(active_mentees)} active mentees with roadmaps.")

        for mentee in active_mentees:
            mentee_name = mentee.get('name', 'there')
            mentee_id = mentee['_id']
            roadmap = mentee.get('roadmap_info', {})

            # 1. Inactivity Check
            print(f"\n--- Checking Inactivity for user: {mentee.get('name')} ---")
            last_login = mentee.get('last_login_at')
            print(f"   - Found last_login_at value: {last_login}")

            if last_login:
                time_since_login = datetime.utcnow() - last_login
                threshold = timedelta(days=INACTIVITY_THRESHOLD_DAYS)
                print(f"   - Time since last login: {time_since_login}")
                print(f"   - Inactivity threshold:  {threshold}")
                
                if time_since_login > threshold:
                    print("   - CONDITION MET. Sending inactivity notification.")
                    message = TEMPLATES['inactivity'].format(mentee_name=mentee_name)
                    progress_service.create_notification(mentee_id, message)
                    print(f"   - Sent inactivity nudge to {mentee_name}.")
                    # Skip other checks if user is inactive
                    continue
                else:
                    print("   - Condition NOT met.")
            else:
                print("   - No last_login_at field found for this user.")

            # 2. Stagnation Check
            last_completion = roadmap.get('last_module_completed_at')
            if last_completion and (datetime.utcnow() - last_completion) > timedelta(days=STAGNATION_THRESHOLD_DAYS):
                next_module = get_next_incomplete_module(roadmap)
                if next_module:
                    message = TEMPLATES['stagnation'].format(
                        mentee_name=mentee_name,
                        next_module_title=next_module.get('title', 'the next module')
                    )
                    progress_service.create_notification(mentee_id, message)
                    print(f"   - Sent stagnation nudge to {mentee_name}.")

            # 3. Milestone Check
            # Note: This check relies on the `complete_module` endpoint setting `completed_at`.
            recently_completed = progress_service.get_recently_completed_modules(roadmap, since_hours=MILESTONE_CHECK_HOURS)
            for module in recently_completed:
                message = TEMPLATES['milestone'].format(
                    mentee_name=mentee_name,
                    module_title=module.get('title', 'a module')
                )
                progress_service.create_notification(mentee_id, message)
                print(f"   - Sent milestone congratulations to {mentee_name} for '{module.get('title')}'.")

    except Exception as e:
        print(f"Error in Progress & Accountability Agent: {e}")

    print(f"[{datetime.utcnow()}] Agent run finished.")

if __name__ == '__main__':
    # This allows for manual execution for testing purposes
    print("Running a manual test of the Progress & Accountability Agent...")
    check_all_mentees_progress()
