from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.forms import ValidationAction
from rasa_sdk.events import AllSlotsReset
from scraping.scraper import getValidSize

from scraping.scraper import findProducts
import re


class FindProductAction(Action):
    BASE_URL = 'https://idealo.de'

    def name(self) -> Text:
        return "action_find_product"

    def parseProductText(self, product, shouldLink):
        return f"<{self.BASE_URL}{product['link']['productLink']['href']}|{product['title']}>" if shouldLink else product["title"]

    async def run(
        self, dispatcher, tracker: Tracker, domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        # TODO productscount - 5

        brand = tracker.get_slot('tv_brand')
        price = tracker.get_slot('tv_price')
        size = tracker.get_slot('tv_size')
        type = tracker.get_slot('tv_type')

        price_range = (0, price) if price != None else None
        products = findProducts(price_range, brand, size, type)
        products_count = len(products)
        if len(products) == 0:
            dispatcher.utter_message("No suitable products found.")
        else:
            shouldLink = tracker.get_latest_input_channel() == "slack"
            item_text = ", ".join(
                self.parseProductText(x, shouldLink)
                for x in products[:5])
            more_text = f" and {products_count - 5} more" if products_count > 5 else ""
            dispatcher.utter_message(
                f"I can recommend following TVs: {item_text}{more_text}.")
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
        tv_size = tracker.slots.get("tv_size", False)
        tv_type = tracker.slots.get("tv_type", False)

        tv_brand_msg = (" " + tv_brand) if tv_brand else ""
        tv_price_msg = f" costing up to {tv_price}€" if tv_price else ""
        tv_size_msg = f" {tv_size}in" if tv_size else ""
        tv_type_msg = (" " + tv_type) if tv_type else ""

        dispatcher.utter_message(
            f"Searching for{tv_size_msg}{tv_brand_msg}{tv_type_msg} TVs{tv_price_msg}..")
        skippedSlots.clear()
        return []


class ValidateOrderTvForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_order_tv_form"

    def validate_tv_brand(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        dispatcher.utter_message("Set brand to " + slot_value)
        return {"tv_brand": slot_value}

    def validate_tv_type(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        dispatcher.utter_message("Set type to " + slot_value)
        return {"tv_type": slot_value}

    def validate_tv_price(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        dispatcher.utter_message("Set price to " + str(slot_value) + "€")
        return {"tv_price": slot_value}

    def validate_tv_size(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        if slot_value != None:
            dispatcher.utter_message("Set size to nearest available: " + str(slot_value) + "\"")
        return {"tv_size": slot_value}

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
        return list(updated_slots)

class ValidateCustomSlotMappings(ValidationAction):

    @staticmethod
    def setSlotNumericalValue(slotValue):
        return int(re.findall('[0-9]+', slotValue)[0])

    # custom extraction of slot from text
    # async def extract_tv_price(
    #     self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    # ) -> Dict[Text, Any]:
    #     intent_of_last_user_message = tracker.get_intent_of_latest_message()
    #     print(intent_of_last_user_message)
    #     print("price", tracker.get_slot("tv_price"))
    #     if intent_of_last_user_message == "inform" or intent_of_last_user_message == "order_tv":
    #         return {"tv_price":  self.setSlotNumericalValue(tracker, "tv_price")}
    #     return {}

    def validate_tv_price(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        price = self.setSlotNumericalValue(slot_value)
        return {"tv_price": price}

    def validate_tv_size(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        size = self.setSlotNumericalValue(slot_value)
        size = getValidSize(size)
        return {"tv_size": size}

class ActionResetAllSlots(Action):
    def name(self):
        return "action_reset_all_slots"
    
    def run(self, dispatcher, tracker, domain):
        return [AllSlotsReset()]
