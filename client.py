import json
import requests

from biosinfo import SystemInformation

SERVER_URL = "http://192.168.45.13:55127/data"  

try:
    system_info = SystemInformation()
    combined_info = system_info.get_combined_system_info()

    json_data = json.dumps(combined_info)
    response = requests.post(SERVER_URL, json=json_data)

    if response.status_code == 200:
        print("Data sent successfully!")
    else:
        print(f"Error sending data: {response.status_code} - {response.text}")
except Exception as e:
    print("An error occurred:", e)
    

