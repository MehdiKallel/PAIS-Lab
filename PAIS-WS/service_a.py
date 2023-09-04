from pymongo import MongoClient
import os
import discord
import requests
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.all()
client = discord.Client(intents=intents)

mongo_client = MongoClient(os.getenv('MONGODB_URI'))
queue_a = mongo_client['queue_a_db']['orders']

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
        print(f"Inserted a document with ID: {inserted_document.inserted_id}")

client.run(os.getenv('DISCORD_BOT_TOKEN'))
