import json
import os

config_path = os.path.dirname(os.path.abspath(__file__)) + "/config.json"
with open(config_path) as f:
    config = json.loads(f.read())

if __name__ == '__main__':
    print(config)