from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.json_util import dumps
import re
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)


try:
    mongo_client = MongoClient(os.getenv('MONGODB_URI'))
except Exception as e:
    print("Could not connect to MongoDB:", e)
    exit(1)

orders = mongo_client['queue_a_db']['orders']
results = mongo_client['results_db']['results']

@app.route('/discord_orders', methods=['POST'])
def get_queued_orders():
    return dumps(orders.find()), 200

@app.route('/discord_results', methods=['POST'])
def get_results():
    return dumps(results.find()), 200


if __name__ == "__main__":
    print("Starting orders service")
    app.run(port=5050)