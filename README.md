# Discord orders correlator

## Description

This system correlates Discord messages against specified rules. It has two components:
- Rule Engine: A Flask application that allows users to input regex rules with an associated end date.
- Discord Fetcher: Monitors orders channel of the discord server, processes orders, and matches them against existing rules based on the rule's regex pattern and end date.

If an incoming message doesn't match any rule or is past the rule's end date, it's stored. If a rule can't be applied immediately, it's queued for future use.

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

4. Run both services: `python3 ruleEngine.py && python3 discordOrdersHandler.py`. If you want to check if your scripts are running, you can use: `ps aux | grep python3`. In case you want to stop one of the services, use `kill <PROCESS_ID>`  

## Key Files
- discordOrdersHandler.py
This script listens for incoming messages on a Discord channel, processes orders, and checks for matching rules. When a matching rule is found, it processes the order and sends a notification to a callback URL.

- ruleEngine.py
This script sets up a Flask web service that allows users to submit rules for processing. It checks if there are any orders from the orders queue that match the incoming rule. In this case, the orders are deleted from the orders queue and aggregated to the rule and stored in the result queue. In case there is no match, the rule is stored in the rules queue. 

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
![Alt text](./pictures/correlator_updated.png?raw=true "Flow of the Discord Correlator Services ")


### 1. Rule Engine

Allows submission of a regex rule, an end date, and a callback URL. If a rule matches any current orders before the given end date, the matched orders are removed from the orders queue and stored with the rule into the results queue.

![Alt text](./pictures/screen2.png?raw=true "Example of a result queue element")

#### Endpoints:

- **POST /apply_rule**
  - **Parameters**:
    - `regex`: A regex pattern to be applied to the current orders.
    - `end`: End date for orders.
  - **Headers**:
    - `CPEE-CALLBACK`: The callback URL to which notifications should be sent. This header is set to false in case we have an orders/rule match and to false if we have an asynchronous call and the rule needs to be stored in the rules queue. The rule may be applied in the future and the corresponding waiting task is informed using the CPEE Callback URL that the task was executed.
  - **Responses**:
    - `200 OK`: Successfully processed the rule -> Regex syntax is correct.
    - `400 Bad Request`: Invalid regex provided.
    - `CPEE-CALLBACK`: A response header indicating if there is an asynchronous call or not (`true` or `false`). It is set to true in case there is the rule has no matching orders and the task may complete in the future. It is set to false in case there is no need for an asynchronous call and the rule has matching orders.

#### Background Processing:

When a rule is submitted via the `/apply_rule` endpoint, the application:

1. If the provided rule matches current orders, the matching orders are removed from the queue and stored in the results queue.
2. If no match is found, the rule is queued for future processing.

### 2. Discord Fetcher

This component listens for messages in a specific channel on Discord, named 'orders'. When a message is received in this channel:

1. The message is logged and added to the queue with metadata such as author's ID, name, order timestamp and tag.
2. The application then checks for any matching rule from the stored rules queue.
3. If a matching rule exists and applies to the received message:
   - The corresponding orders are removed from the queue.
   - The matched orders, along with the rule, are added to the results queue.
   - A notification is sent to the waiting the task that its implementation has finished execution.

## Example:
1. **Navigate to the following url**: https://cpee.org/flow/?monitor=https://cpee.org/flow/engine/22643/
   
![Alt text](./pictures/screen3.png?raw=true)

1. **Navigate to the Graph**:
    - Select the appropriate task.
    - Inside the `regex` argument field, input your desired rule. (example: "vodka")
    - Inside the `end` argument field, input your desired end date.
    > **Example**: If you're searching for orders with the keyword "vodka" that we made before that date: 2023-10-28T11:20, enter `vodka` and `2023-10-28T11:20` (SO 8601 format).

2. **Initiate the Task**:
    - Launch the task instance.
    - **Note**: Due to the absence of queued orders, the task indicator will appear in red. This signifies it's in standby mode, awaiting a response.

![Alt text](./pictures/screen4.png?raw=true)

4. **Access Discord**:
    - Open your Discord server.
    - Head over to the `#orders` channel.

5. **Test the Rule**:
    - To verify the rule, input an order, such as:
    ```
    Sex-on-the-beach small no orange slice
    ```
    Given that the task is on the lookout for the keyword "vodka", it will maintain its red status and will not process the order you've just provided.

6. **Send a Vodka Order**:
    - Now, place an order containing the word `vodka` in the `#orders` channel.
7. **Recognize & Complete**:
    - The system will recognize the "vodka" keyword in the order, completing the task instance and ceasing its function.
    - Subsequently, the rule targeting the keyword "vodka" gets removed from the rules queue for execution.

Note: Please make sure to adjust the "end" field based on your needs. In the previous example, you could set it to a date greater to your current date.
