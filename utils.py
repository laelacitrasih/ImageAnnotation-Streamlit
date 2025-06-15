# utils.py
import os
import json

ANNOTATION_FILE = "saved/annotations.json"

def save_annotation(data):
    if not os.path.exists("saved"):
        os.makedirs("saved")
    with open(ANNOTATION_FILE, "w") as f:
        json.dump(data, f, indent=2)

def load_annotation():
    if os.path.exists(ANNOTATION_FILE):
        with open(ANNOTATION_FILE, "r") as f:
            return json.load(f)
    return []
