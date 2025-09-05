import argparse
import json
import re
from datetime import datetime, timezone

from config import JSON_FILE, SQL_FILE
from generator import Generator


def extract_pushup_count(activity):
    """
    Extract pushup count from activity name, description, or notes.
    Returns the number of pushups found, or 0 if none found.
    """
    # Common patterns to look for pushups in text
    patterns = [
        r'(\d+)\s*push[\s-]*ups?',
        r'push[\s-]*ups?\s*[:\-]?\s*(\d+)',
        r'(\d+)\s*俯卧撑',  # Chinese
        r'俯卧撑\s*[:\-]?\s*(\d+)',
        r'pushup[s]?\s*[:\-]?\s*(\d+)',
        r'(\d+)\s*pushup[s]?',
    ]
    
    # Combine all text sources
    text_sources = []
    if hasattr(activity, 'name') and activity.name:
        text_sources.append(activity.name.lower())
    if hasattr(activity, 'description') and activity.description:
        text_sources.append(activity.description.lower())
    
    combined_text = ' '.join(text_sources)
    
    # Try each pattern
    for pattern in patterns:
        matches = re.findall(pattern, combined_text, re.IGNORECASE)
        if matches:
            # Return the first numeric match found
            try:
                return int(matches[0])
            except (ValueError, IndexError):
                continue
    
    return 0


def run_pushup_sync(client_id, client_secret, refresh_token):
    """
    Sync pushup activities from Strava.
    Looks for WeightTraining, Workout, and CrossTraining activities
    and extracts pushup counts from their descriptions.
    """
    generator = Generator(SQL_FILE)
    generator.set_strava_config(client_id, client_secret, refresh_token)
    
    # Override the sync method to only get strength training activities
    generator.check_access()
    
    print("Start syncing pushup activities")
    
    # Get recent activities
    activities_list = []
    pushup_activities = []
    
    for activity in generator.client.get_activities():
        # Only process strength training related activities
        if activity.type in ['WeightTraining', 'Workout', 'CrossTraining']:
            pushup_count = extract_pushup_count(activity)
            
            if pushup_count > 0:
                print(f"Found {pushup_count} pushups in activity: {activity.name}")
                
                # Create a modified activity object for pushups
                pushup_activity = type('obj', (object,), {
                    'id': activity.id,
                    'name': activity.name or f"Pushups - {pushup_count} reps",
                    'distance': pushup_count,  # Use pushup count as "distance"
                    'moving_time': activity.moving_time or 0,
                    'elapsed_time': activity.elapsed_time or 0,
                    'type': 'Pushup',  # Custom type for pushups
                    'subtype': 'Pushup',
                    'start_date': str(activity.start_date) if activity.start_date else str(datetime.now(timezone.utc)),
                    'start_date_local': str(activity.start_date_local) if activity.start_date_local else str(datetime.now()),
                    'location_country': getattr(activity, 'location_country', ''),
                    'summary_polyline': '',  # No route for pushups
                    'average_heartrate': getattr(activity, 'average_heartrate', None),
                    'average_speed': 0,  # No speed for pushups
                    'elevation_gain': 0,  # No elevation for pushups
                    'total_elevation_gain': 0,
                })()
                
                pushup_activities.append(pushup_activity)
    
    # Use the generator's sync_from_app method to save pushup activities
    if pushup_activities:
        print(f"Found {len(pushup_activities)} pushup activities")
        # Convert to the format expected by sync_from_app
        app_tracks = []
        for activity in pushup_activities:
            track_data = {
                'run_id': int(activity.id),
                'name': activity.name,
                'distance': float(activity.distance),
                'moving_time': activity.moving_time,
                'elapsed_time': activity.elapsed_time,
                'type': activity.type,
                'subtype': activity.subtype,
                'start_date': activity.start_date,
                'start_date_local': activity.start_date_local,
                'location_country': activity.location_country,
                'summary_polyline': activity.summary_polyline,
                'average_heartrate': activity.average_heartrate,
                'average_speed': activity.average_speed,
                'elevation_gain': activity.elevation_gain,
            }
            app_tracks.append(track_data)
        
        generator.sync_from_app(app_tracks)
    else:
        print("No pushup activities found")
    
    # Load all activities and save to JSON
    activities_list = generator.load()
    with open(JSON_FILE, "w") as f:
        json.dump(activities_list, f)
    
    print(f"Saved {len(activities_list)} activities to {JSON_FILE}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("client_id", help="strava client id")
    parser.add_argument("client_secret", help="strava client secret") 
    parser.add_argument("refresh_token", help="strava refresh token")
    
    options = parser.parse_args()
    run_pushup_sync(
        options.client_id,
        options.client_secret,
        options.refresh_token,
    )