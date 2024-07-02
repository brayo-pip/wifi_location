import requests
import platform
import os
import yaml

def get_platform_specific_config_dirs():
    """Returns the platform-specific configuration directories."""
    system = platform.system()

    if system == "Windows":
        config_dir = os.path.join(os.environ['APPDATA'])
    elif system == "Darwin":  # macOS
        config_dir = os.path.join(os.environ['HOME'], 'Library', 'Application Support')
    else:  # Linux and other Unix-like systems
        config_dir = os.path.join(os.environ['HOME'], '.config')

    return config_dir

def read_api_key():
    """Reads the API key from a configuration file. Exits if the file does not exist."""
    config_dir = get_platform_specific_config_dirs()
    config_file = os.path.join(config_dir, 'wifi-location', 'config.yaml')

    try:
        with open(config_file, 'r') as file:
            config = yaml.safe_load(file)
            if config['apikey'] == 'YOUR_API_KEY':
                exit(f"Please add your Google Geolocation API key to the configuration file at {config_file}")
            return config['apikey']
    except FileNotFoundError:
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        file = open(config_file, 'x')
        file.write('apikey: YOUR_API_KEY')
        file.close()
        exit(f"Please add your Google Geolocation API key to the configuration file at {config_file}")

def get_location_from_wifi_data(mac_address, signal_strength):
    """Estimates location based on Wi-Fi data using Google Geolocation API.

    Args:
        mac_address: MAC address of a Wi-Fi access point.
        signal_strength: Signal strength of the access point (in dBm).

    Returns:
        A dictionary containing the estimated location (latitude, longitude) 
        and accuracy radius, or None if location could not be determined.
    """
    api_key = read_api_key()

    url = f'https://www.googleapis.com/geolocation/v1/geolocate?key={api_key}'
    headers = {'Content-Type': 'application/json'}
    
    data = {
        'wifiAccessPoints': [{
            'macAddress': mac_address,
            'signalStrength': signal_strength
        }]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response = requests.post(url, headers=headers)
        response.raise_for_status() 
        json_response = response.json()
        if 'location' in json_response:
            location = json_response['location']
            accuracy = json_response['accuracy']
            return {'lat': location['lat'], 'lng': location['lng'], 'accuracy': accuracy}
    except requests.exceptions.RequestException as e:
        print(f"Error requesting location: {e}")

    return None


# Replace with the MAC address and signal strength of the Wi-Fi access point
mac_address = 'aa:bb:cc:dd:ee:ff' 
signal_strength = -90  

location = get_location_from_wifi_data(mac_address, signal_strength)

if location:
    print(f"Estimated location: {location}")
else:
    print("Location could not be determined.")
