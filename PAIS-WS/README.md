# Discord correlator

## Description

The correlator is running two services that interact with MongoDB and the CPEE Engine. The discord orders fetcher service will apply stored rules on the incoming messages and if there is no corresponding match then the order is stored. The apply rule service will directly perform rule matching on incoming data but will check if stored rules can be applied beofrehand. In this case the callback URLs when specific conditions are met. The project uses the Flask web framework to create a web service that allows users to submit rules and receive notifications.

## Prerequisites

- Python 3.x
- MongoDB
- Flask
- dotenv
- requests

## Usage	
 Clone the repository:

```bash
1.   git clone
2. pip install -r requirements.txt
3. Set up environment variables by creating a .env file in the project root and populating it with the required values. For example: 
MONGODB_URI=your-mongodb-uri
DISCORD_BOT_TOKEN=your-discord-bot-token

Script 1: script1.py
This script listens for incoming messages on a Discord channel, processes orders, and checks for matching rules. When a matching rule is found, it processes the order and sends a notification to a callback URL.

Script 2: script2.py
This script sets up a Flask web service that allows users to submit rules for processing. It checks for matching rules and processes orders in the background. When a matching rule is found, it sends a notification to a pending task from another instance using its callback url.




