import discord
import os
from services import notify_callback, find_oldest_matching_rule, rule_matches_current_orders, queue_a, rule_queue, results_queue
import re

intents = discord.Intents.all()
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


@client.event
async def on_message(message):
    if message.channel.name != 'orders':
        return

    print(f"Received a message from {message.author.name}: {message.content}")

    inserted_document = queue_a.insert_one({
        'content': message.content,
        'author_id': str(message.author.id),
        'author_name': str(message.author.name),
        'author_tag': str(message.author.discriminator)
    })
    print(f"Added new order with ID: {inserted_document.inserted_id}")

    matching_old_rule = find_oldest_matching_rule()
    if not matching_old_rule:
        return

    if rule_matches_current_orders(matching_old_rule['regex']):
        matched_orders = [order for order in queue_a.find() if 'content' in order and re.fullmatch(matching_old_rule['regex'], order['content'])]
        for order in matched_orders:
            queue_a.delete_one({'_id': order['_id']})

        results_queue.insert_one({
            'rule': matching_old_rule['regex'],
            'matched_orders': matched_orders
        })
        rule_queue.delete_one({"_id": matching_old_rule['_id']})
        notify_callback(matching_old_rule['callback_url'], {"regex": matching_old_rule['regex']})


client.run(os.getenv('DISCORD_BOT_TOKEN'))

