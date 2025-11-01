from ai_wayang_simple.config.settings import WAYANG_CONFIG
import requests
import json

class WayangExecutor:
    def __init__(self, url: str | None = None):
        self.url = url or WAYANG_CONFIG.get("server_url")

    def execute_plan(self, plan):
        try:
            # Send plan to Wayang server and return output (both success and errors)
            response = requests.post(url=self.url, json=plan)

            # Return status code and body
            return response.status_code, response.text

        # Handle request errors
        except requests.exceptions.RequestException as e:
            raise Exception(e)
    