from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.forms import ValidationAction

from thefuzz import process

from actions.scraping.scraper import findProducts, getBrands
import re


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

    @staticmethod
    def parseProductText(product, shouldLink):
        return f"<https://idealo.de{product['link']['productLink']['href']}|{product['title']}>" if shouldLink else product["title"]

    async def run(
        self, dispatcher, tracker: Tracker, domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        # TODO productscount - 5

        brand = tracker.get_slot('tv_brand')
        price = tracker.get_slot('tv_price')
        size = tracker.get_slot('tv_size')

        price_range = (0, price) if price != None else None
        products = findProducts(price_range, brand, size)
        products_count = len(products)
        if len(products) == 0:
            dispatcher.utter_message("No suitable products found.")
        else:
            shouldLink = tracker.get_latest_input_channel() == "slack"
            item_text = ", ".join(
                self.parseProductText(x, shouldLink)
                for x in products[:5])
            dispatcher.utter_message(
                f"I can recommend following TVs: {item_text} and {products_count - 5} more.")
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

        tv_brand_msg = (" " + tv_brand) if tv_brand else ""
        tv_price_msg = f" costing up to {tv_price}$" if tv_price else ""
        tv_size_msg = f" {tv_size}in" if tv_size else ""

        dispatcher.utter_message(
            f"Searching for{tv_size_msg}{tv_brand_msg} TVs{tv_price_msg}..")
        skippedSlots.clear()
        return []


class ValidateOrderTvForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_order_tv_form"

    @staticmethod
    def tv_brand_db() -> List[Text]:
        return map(lambda x: x["text"], getBrands())

    def validate_tv_brand(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:

        ext_val, score = process.extractOne(slot_value, self.tv_brand_db())
        if score >= 80:
            return {"tv_brand": ext_val}
        else:
            dispatcher.utter_message("Not a valid brand.")
            return {"tv_brand": None}

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
        return int(re.findall('\d+', slotValue)[0])

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
        if price <= 0:
            dispatcher.utter_message("This is not a valid price.")
            return {"tv_price": None}
        return {"tv_price": price}

    def validate_tv_size(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        size = self.setSlotNumericalValue(slot_value)
        print("size", size)
        if size <= 0:
            dispatcher.utter_message("This is not a valid size.")
            return {"tv_size": None}
        return {"tv_size": size}