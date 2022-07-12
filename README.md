# Commands
train: `rasa train`
run in command line: `rasa shell [nlu]`
interactive: `rasa interactive [--skip-visualization] [-m models]` (trains automatically if no model supplied)

rasa x: (docker has to be running)
setup: `curl -O https://rei.rasa.com/rei.sh && bash rei.sh -y`
`rasactl connect rasa`?
`sudo rasactl start --project`?
`rasa x`? downgrade?

action server: 
`python -m rasa_sdk --actions actions`

run on slack:
expose port: `lt --port 5005 --subdomain rasabot`
change url here: https://api.slack.com/apps/A03GPUMGBL6/event-subscriptions? and interactive components


