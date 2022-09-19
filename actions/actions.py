from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.forms import ValidationAction
from rasa_sdk.events import AllSlotsReset
from scraping.scraper import getValidSize
from rasa_sdk.events import SlotSet

from scraping.scraper import findProducts
import re


class FindProductAction(Action):
    def name(self) -> Text:
        return "action_find_product"

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
        page = 0
        channel = tracker.get_latest_input_channel()
        showProducts(dispatcher, products, page, channel)
        return [SlotSet("_page", page), SlotSet("_products", products)]


def showProducts(dispatcher, products, page, channel):
    def parseProductSection(product):
        BASE_URL = 'https://idealo.de'

        if product['userRating'] != None:
            ratingPercent = product['userRating']['percent']
            numStars = round(ratingPercent * 0.05)
            stars = '\u2605' * round(numStars) + '\u2606' * (5 - numStars)
        else:
            stars = ""

        return {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*<{BASE_URL}{product['link']['productLink']['href']}|{product['title']}>*\n{stars}\n{product['priceElement']['priceWithCurrency']}"
            },
            "accessory": {
                "type": "image",
                "image_url": product['image']['httpSrc'],
                "alt_text": product['title']
            }
        }

    def formatSlack(products, remainingCount, isFirstPage):
        blocks = []

        if isFirstPage:
            blocks.append({
                "type": "section",
                "text": {
                        "type": "mrkdwn",
                        "text": "I can recommend following items:"
                }
            })

        blocks.append({"type": "divider"})
        for p in products:
            blocks.append(parseProductSection(p))
            blocks.append({ "type": "divider" })

        if remainingCount > 0:
            blocks.append({
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "emoji": True,
                                "text": f"Show more results ({remainingCount})"
                            },
                            "value": "action_show_more"
                        }
                    ]
                })

        return {"blocks": blocks}

    first_index = page * 5
    last_index = (page + 1) * 5

    products_count = len(products)
    remaining_count = products_count - last_index

    if not products_count:
        dispatcher.utter_message("No suitable products found.")
    elif channel == "slack":
        dispatcher.utter_message(json_message=formatSlack(
            products[first_index:last_index], remaining_count, page == 0))
    else:
        item_text = ", ".join(x["title"]
                              for x in products[first_index:last_index])
        more_text = f" and {remaining_count} more" if remaining_count > 0 else ""
        pretext = "I can recommend following TVs: " if not page else ""
        dispatcher.utter_message(pretext + item_text + more_text + ".")


skippedSlots = set()


class ShowMoreAction(Action):
    def name(self) -> Text:
        return "action_show_more"

    async def run(
        self, dispatcher, tracker: Tracker, domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        page = tracker.get_slot("_page")
        products = tracker.get_slot("_products")

        page += 1
        first_index = page * 5

        if first_index >= len(products):
            dispatcher.utter_message("No more products to show")
        else:
            channel = tracker.get_latest_input_channel()
            showProducts(dispatcher, products, page, channel)
            return [SlotSet("_page", page)]
        return []

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
        if tracker.active_loop:
            dispatcher.utter_message("Set brand to " + slot_value)
        return {"tv_brand": slot_value}

    def validate_tv_type(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        if tracker.active_loop:
            dispatcher.utter_message("Set type to " + slot_value)
        return {"tv_type": slot_value}

    def validate_tv_price(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        if tracker.active_loop:
            dispatcher.utter_message("Set price to " + str(slot_value) + "€")
        return {"tv_price": slot_value}

    def validate_tv_size(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        if tracker.active_loop:
            dispatcher.utter_message(
                f"Set size to nearest available: {slot_value}\"")
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
        return float(re.findall(r'[0-9]+(?:\.[0-9]{1,2})?', slotValue)[0])

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
