# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.events import SlotSet

import json


class ActionHelloWorld(Action):

    def name(self) -> Text:
        return "action_hello_world"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="Hello World!")

        return []


class FindProductAction(Action):
    def name(self) -> Text:
        return "action_find_product"

    async def run(
        self, dispatcher, tracker: Tracker, domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        brand = tracker.get_slot('tv_brand')
        price = tracker.get_slot('tv_price')
        with open('actions/dataset/db.json') as f:
            items = json.load(f)
            item_text = ""
            for i in items:
                if (brand is None or i["brand"].casefold() == brand.casefold()) and (price is None or float(i["price"]) <= float(price)):
                    if item_text != "":
                        item_text += ", "
                    if tracker.get_latest_input_channel() == "slack":
                        item_text += f"<{i['link']}|{i['name']}>"
                    else:
                        item_text += i['name']
            if item_text != "":
                dispatcher.utter_message(
                    "I can recommend following TVs: " + item_text)
            else:
                dispatcher.utter_message("No suitable products found.")
        return []


skippedSlots = set()

class SummarizeOrderAction(Action):
    def name(self) -> Text:
        return "action_order_summary"

    async def run(
        self, dispatcher, tracker: Tracker, domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        tv_brand = tracker.slots.get("tv_brand", False)
        tv_price = tracker.slots.get("tv_price", False)

        tv_brand_msg = (" " + tv_brand) if tv_brand else ""
        tv_price_msg = f" costing up to {tv_price}$" if tv_price else ""

        dispatcher.utter_message(
            f"Searching for{tv_brand_msg} TVs{tv_price_msg}..")
        skippedSlots.clear()
        return []

class ValidateOrderTvForm(FormValidationAction):

  def name(self) -> Text:
      return "validate_order_tv_form"

  async def required_slots(
      self,
      domain_slots: List[Text],
      dispatcher: CollectingDispatcher,
      tracker: Tracker,
      domain: DomainDict
  ) -> List[Text]:

    updated_slots = set(domain_slots)

    if tracker.get_intent_of_latest_message() == "skip":
      slot = tracker.get_slot("requested_slot")
      skippedSlots.add(slot)

    updated_slots -= skippedSlots
    print(updated_slots, skippedSlots)

    return list(updated_slots)
