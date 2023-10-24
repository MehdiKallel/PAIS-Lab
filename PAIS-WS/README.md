# Discord correlator

## Description

The correlator is running two services that interact with MongoDB and the CPEE Engine. The discord orders fetcher service will apply stored rules on the incoming messages and if there is no corresponding match then the order is stored. The apply rule service will directly perform rule matching on incoming regex rules and in the case the rule cant be applied, it is stored for future use. In this case the callback URLs when specific conditions are met. The project uses the Flask web framework to create a web service that allows users to submit rules and receive notifications.

## Prerequisites

- Python 3.x
- MongoDB
- Flask
- dotenv
- requests

## Usage	
 Clone the repository:
1. git clone https://github.com/MehdiKallel/PAIS-Lab.git
2. pip install -r requirements.txt
3. Set up environment variables by creating a .env file in the project root and populating it with the required values. For example: 
MONGODB_URI=your-mongodb-uri
DISCORD_BOT_TOKEN=your-discord-bot-token

Script 1: DiscordOrdersHandler
This script listens for incoming messages on a Discord channel, processes orders, and checks for matching rules. When a matching rule is found, it processes the order and sends a notification to a callback URL.

Script 2: RuleEngine
This script sets up a Flask web service that allows users to submit rules for processing. It checks for matching rules and processes orders in the background. When a matching rule is found, it sends a notification to a pending task from another instance using its callback url.

Before running the correlator, it is required to set up a discord bot via the developers portal of discord, create a new server and invite your bot to it. 

## Setting Up a Discord Bot
1. Log in to your Discord account.
2. Go to the Discord Developer Portal.
3. Click on "New Application" to create a new Discord application.
4. Under the "Settings" tab, navigate to "Bot" on the left sidebar.
5. Click the "Add Bot" button to create a bot user for your application.
6. Copy the bot's token (DISCORD_BOT_TOKEN) and set it in your .env file.

## Create a Discord Server
1. In Discord, click on the "+" button on the left sidebar to create a new server.
2. Choose a server name, icon, and region.
3. Customize your server by adding channels, roles, and permissions as needed.
4. Invite your bot to the server using its OAuth2 URL generated in the Discord Developer Portal.
