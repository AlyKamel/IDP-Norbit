# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher 

import json

class ActionHelloWorld(Action):

    def name(self) -> Text:
        return "action_hello_world"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="Hello World!")

        return []


class MyCustomAction(Action):
    def name(self) -> Text:
        return "action_find_product"

    async def run(
        self, dispatcher, tracker: Tracker, domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        brand = tracker.get_slot('tv_brand')
        price = float(tracker.get_slot('tv_price'))
        with open('actions/dataset/db.json') as f:
            items = json.load(f)
            item_text = ""
            for i in items:
                if i["brand"].casefold() == brand.casefold() and float(i["price"]) <= price:
                    item_text += i["name"] + ", "
            if item_text != "":
                dispatcher.utter_message("I can recommend following TVs: " + item_text)
            else:
                dispatcher.utter_message("No suitable products found.")
        return []