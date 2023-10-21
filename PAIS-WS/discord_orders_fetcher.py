from pymongo import MongoClient
import os
import discord
import requests
from dotenv import load_dotenv
import re
load_dotenv()
intents = discord.Intents.all()
client = discord.Client(intents=intents)

mongo_client = MongoClient(os.getenv('MONGODB_URI'))
queue_a = mongo_client['queue_a_db']['orders']
rule_queue = mongo_client['rule_queue_db']['rules']
results_queue = mongo_client['results_db']['results']

def notify_callback(url, data):
    try:
        response = requests.put(url, data, headers={'content-type':'application/json'})
        print(f"Getting final response as follows: {response}")
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

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    print(f"Received a message: {message.content}")
    if message.channel.name == 'orders':
        print("received order from client" + str(message.author.name))
        inserted_document = queue_a.insert_one({
            'content': message.content,
            'author_id': str(message.author.id),
            'author_name': str(message.author.name),
            'author_tag': str(message.author.discriminator)
        })
        print(f"Added new order with ID: {inserted_document.inserted_id}")

    matching_old_rule = find_oldest_matching_rule()
    print(matching_old_rule)
    if matching_old_rule:
        stored_regex = re.compile(matching_old_rule['regex'])
        if rule_matches_current_orders(stored_regex):
            print(f"Found a rule that can be applied with the current order queue state: {matching_old_rule}")
            matched_orders = []
            regex = matching_old_rule['regex']
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
            rule_queue.delete_one({"_id": matching_old_rule['_id']})
            notify_callback(matching_old_rule['callback_url'], {"regex": matching_old_rule['regex']})
            return

client.run(os.getenv('DISCORD_BOT_TOKEN'))
