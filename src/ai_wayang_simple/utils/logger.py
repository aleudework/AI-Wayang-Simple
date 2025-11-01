from ai_wayang_simple.config.settings import LOG_CONFIG
from datetime import datetime
import os
import json

class Logger:
    """
    Logger to debug and inspect the agentic architecture
    """

    def __init__(self):
        self.folder_path = LOG_CONFIG.get("log_folder")
        self.logfile = self._create_logfile() or None
    
    def _create_logfile(self):
        """
        Helper that initialize log json file
        """

        # Check if folder exists
        if not self.folder_path:
            return None
        
        # Check or create log folder if doesn't exist
        os.makedirs(self.folder_path, exist_ok=True)

        # Create path for log file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"log_{timestamp}.json"
        filepath = os.path.join(self.folder_path, filename)

        # Create file
        with open(filepath, "w", encoding="utf-8", ) as f:
            json.dump([], f, indent=4)
            
        return filepath
    
    def add_message(self, title: str, msg):
        """
        Append a message to the log
        """

        # Return if no folder path
        if not self.folder_path:
            return None
        
        # Make timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Get log
        with open(self.logfile, "r", encoding="utf-8") as f:
            logs = json.load(f)

        # Write to log
        with open(self.logfile, "w", encoding="utf-8") as f:
            # Size for ID
            size = len(logs)

            # Create new log
            new_log = {
                "id": size + 1,
                "title": title,
                "timestamp": timestamp,
                "log": msg
            }

            # Add new log
            logs.append(new_log)

            # (Over)write the log
            json.dump(logs, f, indent=4)
            
            







