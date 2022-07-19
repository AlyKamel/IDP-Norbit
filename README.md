# FinderBot 

Rasa-based chatbot with the mission to assist customers to find various electronic products based on their criteria.

## How to run the bot

### Train

```
$ rasa train
```

Train a new model.

### Run


Rasa can run in the terminal for quick testing using: 
```
$ rasa shell
```
or
```
$ rasa interactive [--skip-visualization] [-m MODELPATH]
```
for more debugging options and the ability to fix any issues. For quicker execution, the flags `--skip-visualization` and `-m MODELPATH` can be supplied, with `MODELPATH` being the path to a pretrained model.
For more information, visit the [official Rasa website](http://www.rasa.com).

## How to run the action server

```
python -m rasa_sdk --actions actions
```

## How to run on Slack

Rasa has great documentation on [how to connect a chatbot to Slack](https://rasa.com/docs/rasa/connectors/slack) and various other services. Also check out [this guide](https://api.slack.com/bot-users) from Slack.