from datetime import datetime
import requests
import pytz

def perform_get_request(url):
    import json
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for non-2xx status codes
        return json.loads(response.text)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None
    
def convert_to_utc(timestamp, format):
    # Parse the datetime string
    dt = datetime.strptime(timestamp, format)
    
    # Set the input datetime as UTC timezone-aware
    dt = pytz.utc.localize(dt)
    
    # Convert the datetime to UTC timezone
    dt_utc = dt.astimezone(pytz.utc)
    
    # Convert UTC datetime to timestamp
    timestamp_utc = dt_utc.timestamp()
    
    return int(timestamp_utc)

