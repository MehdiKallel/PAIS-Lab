from dotenv import load_dotenv
import os
import discord
from discord.ext import commands
load_dotenv()  # This loads the environment variables from the .env file




intents = discord.Intents.all()
client = discord.Client(intents=intents)
client.run('MTEyMDA3MzU0MjM2NTYxNDE0MQ.GciZHy.nqOLWGfiFcqMd3Uutn3mM_qIFJpd5DdoMSgcFE')