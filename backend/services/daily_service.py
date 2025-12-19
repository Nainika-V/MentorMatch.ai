import os
import requests
import datetime

def create_daily_room():
    """
    Creates a new Daily.co room and returns its information.
    """
    DAILYCO_API_KEY = os.environ.get('DAILYCO_API_KEY')

    if not DAILYCO_API_KEY:
        raise Exception("Daily.co API key not configured")

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {DAILYCO_API_KEY}'
    }

    # Room expires in 24 hours
    one_day_from_now = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1)
    
    daily_room_data = {
        'properties': {
            'exp': int(one_day_from_now.timestamp()),
            'enable_prejoin_ui': False,
            'enable_knocking': False,
        }
    }

    try:
        daily_response = requests.post(
            f'https://api.daily.co/v1/rooms',
            headers=headers,
            json=daily_room_data
        )
        daily_response.raise_for_status()
        room_info = daily_response.json()
        return room_info
    except requests.exceptions.RequestException as e:
        # Log the error and re-raise or handle it as needed
        print(f"Error creating Daily.co room: {e}")
        # Optionally, you can parse the error response from Daily.co
        try:
            error_info = e.response.json()
            raise Exception(f"Daily.co API Error: {error_info.get('info')}") from e
        except:
            raise e

def generate_meeting_token(room_name, user_name):
    """
    Generates a meeting token for a given room and user.
    """
    DAILYCO_API_KEY = os.environ.get('DAILYCO_API_KEY')

    if not DAILYCO_API_KEY:
        raise Exception("Daily.co API key not configured")

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {DAILYCO_API_KEY}'
    }

    # Token expires in 1 hour
    one_hour_from_now = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)

    token_properties = {
        'properties': {
            'room_name': room_name,
            'user_name': user_name,
            'exp': int(one_hour_from_now.timestamp())
        }
    }

    try:
        token_response = requests.post(
            f'https://api.daily.co/v1/meeting-tokens',
            headers=headers,
            json=token_properties
        )
        token_response.raise_for_status()
        token_info = token_response.json()
        return token_info['token']
    except requests.exceptions.RequestException as e:
        print(f"Error generating Daily.co token: {e}")
        try:
            error_info = e.response.json()
            raise Exception(f"Daily.co API Error: {error_info.get('info')}") from e
        except:
            raise e
