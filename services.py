from pymongo import MongoClient
import os
import re
import requests
from dotenv import load_dotenv

load_dotenv()

mongo_client = MongoClient(os.getenv('MONGODB_URI'))
queue_a = mongo_client['queue_a_db']['orders']
rule_queue = mongo_client['rule_queue_db']['rules']
results_queue = mongo_client['results_db']['results']


def notify_callback(url, data):
    try:
        response = requests.put(url, data, headers={'content-type':'application/json'})
        print(f"Notification status: {response}")
        return response
    except requests.RequestException as e:
        print(f"Failed to notify callback. Error: {e}")
        return None


def find_oldest_matching_rule():
    all_rules = list(rule_queue.find().sort("_id", 1))
    for stored_rule in all_rules:
        stored_regex = re.compile(stored_rule['regex'])
        for order in queue_a.find():
            if 'content' in order and isinstance(order['content'], str):
                if re.fullmatch(stored_regex, order['content']):
                    return stored_rule
    return None


def rule_matches_current_orders(regex):
    for order in queue_a.find():
        if 'content' in order and isinstance(order['content'], str):
            if re.fullmatch(regex, order['content']):
                return True
    return False


