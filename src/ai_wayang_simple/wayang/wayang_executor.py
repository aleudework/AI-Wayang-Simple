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
    
# TODO
# - Find out why err_msg don't show up (Scala error msg may be different?)
# - Make the server part handle, so if there is an error, then make an option - or like that - to output it
# - Make joins in the operators
# - Make different input and output operators - Output first
# - Give output to the client and make sure why there is a timeout time for mcp.
    