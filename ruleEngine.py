from flask import Flask, request, Response
from pymongo import MongoClient
from services import notify_callback, find_oldest_matching_rule, rule_matches_current_orders, queue_a, results_queue, rule_queue
import threading
from flask_cors import CORS
import re
app = Flask(__name__)
CORS(app)


def process_rule_in_background(regex, callback_url, end):
    if rule_matches_current_orders(regex, end):
        matched_orders = [order for order in queue_a.find() if 'content' in order and re.fullmatch(regex, order['content'])]
        for order in matched_orders:
            queue_a.delete_one({'_id': order['_id']})

        results_queue.insert_one({
            'rule': regex.pattern,
            'matched_orders': matched_orders
        })
        return 200
    else:
        rule_queue.insert_one({"regex": regex.pattern, "callback_url": callback_url, "end": end})
        return 200


@app.route('/apply_rule', methods=["POST"])
def apply_rule():
    regex_str = request.form.get('regex')
    end = request.form.get('end')

    callback_url = request.headers.get('CPEE-CALLBACK')
    response = Response()

    try:
        regex = re.compile(regex_str)
    except re.error:
        return "Invalid regex", 400

    response.headers['CPEE-CALLBACK'] = 'false' if rule_matches_current_orders(regex_str, end) else 'true' 
    response.status_code = 200

    thread = threading.Thread(target=process_rule_in_background, args=(regex, callback_url, end))
    thread.start()
    return response


if __name__ == "__main__":
    app.run(host="::", port=22996)

