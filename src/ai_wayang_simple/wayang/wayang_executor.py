from ai_wayang_simple.config.settings import WAYANG_CONFIG
import requests
import json

class WayangExecutor:
    def __init__(self, url: str | None = None):
        self.url = url or WAYANG_CONFIG.get("server_url")


    def execute_plan(self, plan):

        response = requests.post(url=self.url, json=plan)

        print(f"[WAYANG INFO] status code: {response.status_code}")

        if response.status_code != 200:
            raise ValueError(f"Statuscode from Wayang is not 200 {response.status_code}")
        
        return response.text
    
    
    