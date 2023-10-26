# Discord correlator

## Description

The discord correlator system is composed of two primary components: a rule engine, implemented as a Flask application, and a Discord fetcher that listens for messages in specific Discord channels. The discord orders fetcher service will apply stored rules on the incoming messages and if there is no corresponding match then the order is stored. The apply rule service will directly perform rule matching on incoming regex rules and in the case the rule cant be applied, it is stored for future use. In this case the callback URLs when specific conditions are met.

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


## Files
- discordOrdersHandler.py
This script listens for incoming messages on a Discord channel, processes orders, and checks for matching rules. When a matching rule is found, it processes the order and sends a notification to a callback URL.

- ruleEngine.py
This script sets up a Flask web service that allows users to submit rules for processing. It checks for matching rules and processes orders in the background. When a matching rule is found, it sends a notification to a pending task from another instance using its callback url.

- services.py
includes some util functions used by the ruleEngine and the discordOrdersHandler:
- notify_callback: sends a put request to a specific url: used to inform a waiting task that its task has been executed.
- find_oldest_matching_rule: for a given regex rule, iterate over the stored rules and look for the oldest rule that match this regex.
- rule_matches_current_order: check if a given regex does have any match from the current orders queue.




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


## Correlator Services
![Alt text](./pictures/correlator_updated.png?raw=true "Transaction Flow of the Discord Correlator Services")


### 1. Rule Engine

The rule engine is a Flask-based web service that enables clients to submit a regex rule and a callback URL. When the provided rule matches any current orders, the corresponding orders are returned and deleted from orders queue. They are stored in a result queue with their corresponding rule
#### Endpoints:

- **POST /apply_rule**
  - **Parameters**:
    - `regex`: A regex pattern to be applied to the current orders.
  - **Headers**:
    - `CPEE-CALLBACK`: The callback URL to which notifications should be sent. This header is set to false in case we have an orders/rule match and to false if we have an asynchronous call and the rule needs to be stored in the rules queue. The rule may be applied in the future and the corresponding waiting task is informed using the CPEE Callback URL that the task was executed.
  - **Responses**:
    - `200 OK`: Successfully processed the rule -> Regex syntax is correct.
    - `400 Bad Request`: Invalid regex provided.
    - `CPEE-CALLBACK`: A response header indicating if a rule matches the current orders (`true` or `false`).

#### Background Processing:

When a rule is submitted via the `/apply_rule` endpoint, the application:

1. If the provided rule matches current orders, the matching orders are removed from the queue and stored in the results queue.
2. If no match is found, the rule is queued for future processing.

### 2. Discord Fetcher

This component listens for messages in a specific channel on Discord, named 'orders'. When a message is received in this channel:

1. The message is logged and added to the queue with metadata such as author's ID, name, and tag.
2. The application then checks for any matching rule from the stored rules queue.
3. If a matching rule exists and applies to the received message:
   - The corresponding orders are removed from the queue.
   - The matched orders, along with the rule, are added to the results queue.
   - A notification is sent to the waiting the task that its call was executed sucessfully.


### Usage example:
1. **Navigate to the following url**: https://cpee.org/flow/?monitor=https://cpee.org/flow/engine/22643/
   
![Alt text](./screen1.png?raw=true)

## Setting Up Your Rule

1. **Navigate to the Graph**:
    - Select the appropriate task.
    - Inside the `regex` argument field, input your desired rule. 
    > **Example**: If you're searching for orders with the keyword "vodka", enter `vodka`.

## Start the Task Instance

2. **Initiate the Task**:
    - Launch the task instance.
    - **Note**: Due to the absence of queued orders, the task indicator will appear in red. This signifies it's in standby mode, awaiting a response.

## Queueing an Order in Discord

3. **Access Discord**:
    - Open your Discord server.
    - Head over to the `#orders` channel.

4. **Test the Rule**:
    - To verify the rule, input an order, such as:
    ```
    Sex-on-the-beach small no orange slice
    ```
    Given that the task is on the lookout for the keyword "vodka", it will maintain its red status and will not process the order you've just provided.

5. **Send a Vodka Order**:
    - Now, place an order containing the word `vodka` in the `#orders` channel.

## Task Completion

6. **Recognize & Complete**:
    - The system will recognize the "vodka" keyword in the order, completing the task instance and ceasing its function.
    - Subsequently, the rule targeting the keyword "vodka" gets removed from the rules queue for execution.
