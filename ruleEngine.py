from flask import Flask, request, Response
from pymongo import MongoClient
from services import notify_callback, find_oldest_matching_rule, rule_matches_current_orders, queue_a, results_queue, rule_queue
import threading
from flask_cors import CORS
import re
app = Flask(__name__)
CORS(app)


def process_rule_in_background(regex, callback_url):
    matching_old_rule = find_oldest_matching_rule()
    if matching_old_rule:
        if rule_matches_current_orders(matching_old_rule['regex']):
            rule_queue.delete_one({"_id": matching_old_rule['_id']})
            rule_queue.insert_one({"regex": regex.pattern, "callback_url": callback_url})
            notify_callback(callback_url, {"regex": matching_old_rule['regex']})
            return

    if rule_matches_current_orders(regex):
        matched_orders = [order for order in queue_a.find() if 'content' in order and re.fullmatch(regex, order['content'])]
        for order in matched_orders:
            queue_a.delete_one({'_id': order['_id']})

        results_queue.insert_one({
            'rule': regex.pattern,
            'matched_orders': matched_orders
        })
        return 200
    else:
        rule_queue.insert_one({"regex": regex.pattern, "callback_url": callback_url})
        return 200


@app.route('/apply_rule', methods=["POST"])
def apply_rule():
    regex_str = request.form.get('regex')
    callback_url = request.headers.get('CPEE-CALLBACK')
    response = Response()

    try:
        regex = re.compile(regex_str)
    except re.error:
        return "Invalid regex", 400

    response.headers['CPEE-CALLBACK'] = 'false' if rule_matches_current_orders(regex_str) else 'true' 
    response.status_code = 200

    thread = threading.Thread(target=process_rule_in_background, args=(regex, callback_url))
    thread.start()
    return response


if __name__ == "__main__":
    app.run(host="::", port=22996)
