# Norbit

A Rasa-based chatbot with the mission to assist customers to find various electronic products based on their criteria. Norbit is able to communicate with users by recognizing predefined entities and intents and responding to them according to specified rules.

## Run the bot

To get the chatbot running, to services must be ran: the chatbot server and the action server. The chatbot is then accessible through an external channel (e.g. [Slack](#through-slack)) or through an [interactive shell](#through-the-shell).

The action server allows for more complex actions such as fetching external data. It contains the logic to perform the search for products.

### Using Docker (recommended)

```
docker compose up --build
```

### Locally

1. Clone the repository
2. Set the *ACTION_ENDPOINT_HOST* variable inside the .env file (localhost for local deployment)
3. Set the environment variables: `set -a; source .env; set +a`
4. Run the bot server: `rasa run -p $RASA_BOT_PORT`
5. Run the action server: `python -m rasa_sdk --actions actions -p $ACTION_SERVER_PORT`

## Access the bot

### Through the shell

Rasa can run in the terminal interactively using `rasa shell` in place of the `rasa run` command.

### Through Slack

To allow Slack to connect to the bot, the address for event subscription and interactive components has to be set to **{BOT_SERVER_ADDRESS}/webhooks/slack/webhook**. This can be done from the [app monitoring page](https://api.slack.com/apps/). Note: local addresses cannot be used in Slack. As a workaround, a service such as [localtunnel](https://github.com/localtunnel/localtunnel) can be used to make testing easier. The command `lt --port $RASA_BOT_PORT --subdomain SUBDOMAIN` makes the bot service reachable under the address: `https://SUBDOMAIN.loca.lt`.

Three environment variables have to be set in the .env file to establish the connection: *SLACK_TOKEN*, *SLACK_CHANNEL* and *SLACK_SIGNING_SECRET*.

For more information, Rasa has great documentation on [how to connect a chatbot to Slack](https://rasa.com/docs/rasa/connectors/slack). Also check out [this guide](https://api.slack.com/authentication/basics) from Slack on how to create a Slack bot.

## Train

After any data relating to the chatbot has been modified, a new model can be trained using `rasa train`. Whenever the bot server is ran, it uses the most recent model by default.

For further information, visit the [official Rasa website](http://www.rasa.com).