import discord
from discord.ext import commands
import re
import traceback
import json
from pymongo import MongoClient
import os
from dotenv import load_dotenv


intents = discord.Intents.all()
client = discord.Client(intents=intents)
load_dotenv()
print(os.getenv('MONGODB_URI'))
print(os.getenv('DISCORD_BOT_TOKEN'))
print (type(os.getenv('MONGODB_URI')))
print (type(os.getenv('DISCORD_BOT_TOKEN')))  

with open('rules.json', 'r') as f:
    rules = json.load(f)['rules']

# Connect to MongoDB
mongo_client = MongoClient(os.getenv(os.getenv('MONGODB_URI')))
db = mongo_client['cluster0']  
collection = db['drink_requests']

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    try:
        if message.author == client.user:
            return

        if message.channel.name == 'orders':
            print(f"Received message from {message.channel.name}: {message.content}")

            matches = []
            tokens = message.content.split()

            for token in tokens:
                for rule in rules:
                    pattern = re.compile(rule['pattern'])
                    match = pattern.fullmatch(token)
                    if match:
                        matches.append((rule['action'], match.group()))
                        print(f"Match found for rule '{rule['rule_name']}': {match.group()}")
                        break

            if len(matches) < len(rules):
                response_message = "Invalid or missing order components."
            else:
                response_message = 'Order received! '
                for match in matches:
                    response_message += f'{match[0]}: {match[1]}, '

                drink_request = {
                    'author_id': str(message.author.id),
                    'content': message.content,
                    'matches': [f'{match[0]}: {match[1]}' for match in matches]
                }
                collection.insert_one(drink_request)

            await message.channel.send(response_message[:-2])  # remove trailing comma and space
            print(f"Order received from {message.author}: {message.content}")

    except Exception as e:
        print(f"Error processing message: {e}")
        traceback.print_exc()

client.run(os.getenv('DISCORD_BOT_TOKEN'))
