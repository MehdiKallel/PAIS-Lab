from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.json_util import dumps
import re
import os
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
CORS(app)

try:
    mongo_client = MongoClient(os.getenv('MONGODB_URI'))
except Exception as e:
    print("Could not connect to MongoDB:", e)
    exit(1)

queue_a = mongo_client['queue_a_db']['orders']
results_queue = mongo_client['results_db']['results']

@app.route('/apply_rule', methods=['POST'])
def apply_rule():
    print(request.json)
    regex = request.json.get('regex')
    print(type(regex))
    try:
        compiled_regex = re.compile(regex)
    except re.error:
        return jsonify({"error": "Invalid regex"}), 400
    if not regex:
        return jsonify({"error": "Regex missing"}), 400
    matched_orders = []

    for order in queue_a.find():
        if 'content' in order and isinstance(order['content'], str):
            if re.fullmatch(compiled_regex, order['content']):
                matched_orders.append(order)
                print(f"Match found for rule '{regex}': {order['content']}")

    if not matched_orders:
        return jsonify({"error": "No orders matched"}), 404

    for order in matched_orders:
        queue_a.delete_one({'_id': order['_id']})
        
    result_object = {
        'rule': regex,
        'matched_orders': matched_orders
    }

    results_queue.insert_one(result_object)
    
    return jsonify({"success": "Rule applied successfully", "result_id": str(result_object['_id'])}), 200

if __name__ == "__main__":
    app.run()
