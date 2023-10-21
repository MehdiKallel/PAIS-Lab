from flask import Flask, request, jsonify, make_response, Response
from pymongo import MongoClient
from bson.json_util import dumps
import re
import os
import threading
import requests
from dotenv import load_dotenv
from flask_cors import CORS, cross_origin
import json
load_dotenv()

app = Flask(__name__)
CORS(app)

try:
    mongo_client = MongoClient(os.getenv('MONGODB_URI'))
except Exception as e:
    print("Could not connect to MongoDB:", e)
    exit(1)

#raw orders queue
queue_a = mongo_client['queue_a_db']['orders']

#rules queries results
results_queue = mongo_client['results_db']['results']

#rules queue
rule_queue = mongo_client['rule_queue_db']['rules']

def notify_callback(url, data):
    try: 
        response = requests.put(url, data, headers={'content-type':'application/json'})
        print(f"Notifying callback with status: {response}")
        return response.json()
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

def process_rule_in_background(regex, callback_url):
    matching_old_rule = find_oldest_matching_rule()

    if matching_old_rule:
        stored_regex = re.compile(matching_old_rule['regex'])
        if rule_matches_current_orders(stored_regex):
            print(f"Found an overlapping older rule: {matching_old_rule}")
            rule_queue.delete_one({"_id": matching_old_rule['_id']})
            print("callback url is " + call_back_url)
            rule_queue.insert_one({"regex": regex.pattern, "callback_url": callback_url})
            notify_callback(callback_url, {"regex": matching_old_rule['regex']})
            return

    if rule_matches_current_orders(regex):
        print(f"No overlapping older rule found, applying the incoming rule")
        matched_orders = []
        for order in queue_a.find():
            if 'content' in order and isinstance(order['content'], str):
                if re.fullmatch(regex, order['content']):
                    matched_orders.append(order)
                    print(f"Match found for rule '{regex}': {order['content']}")
        
        for order in matched_orders:
            queue_a.delete_one({'_id': order['_id']})

        result_object = {
            'rule': regex,
            'matched_orders': matched_orders
        }
        results_queue.insert_one(result_object)
        return 200
    else:
        print(f"No matches for incoming rule, storing it for future use")
        rule_queue.insert_one({"regex": regex.pattern, "callback_url": callback_url })
        return 200

@app.route('/apply_rule', methods=["POST"])
def apply_rule():
    regex = request.form.get('regex')
    callback_url = request.headers.get('CPEE-CALLBACK')
    response = Response()

    try:
        compiled_regex = re.compile(regex)
    except re.error:
        response.status = 400
        return response
    if not regex:
        response.status = 400
        return response

    if rule_matches_current_orders(regex):
        response.headers['CPEE-CALLBACK'] = 'false'
        response.status = 200
        response.body = '' 
    else:
        response.headers['CPEE-CALLBACK'] = 'true'
        response.status = 200
        response.body = ''

    thread = threading.Thread(target=process_rule_in_background, args=(compiled_regex, callback_url))
    thread.start()
    return response

if __name__ == "__main__":
    app.run(host="::", port=22996)

