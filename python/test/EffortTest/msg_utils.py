import json
import time

# Convert a message dict to a JSON string, 
# automatically adding a timestamp if not already present
def to_json(msg: dict) -> str:
    if "timestamp" not in msg:
        msg["timestamp"] = time.time()
    return json.dumps(msg)
