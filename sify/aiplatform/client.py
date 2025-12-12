import requests

class AiPlatform: 
    def __init__(self):
        self.base_url = "http://localhost:5000/api/inner"

    def _send_request(self, method, endpoint, json=None, params=None):
        url = f"{self.base_url}{endpoint}"

        headers = {
            "Content-Type": "application/json"
        }

        response = requests.request(method, url, json=json, headers=headers, params=params)
        
        return response
    
    def get_current_time(self):
        return self._send_request("GET", "/current-time")