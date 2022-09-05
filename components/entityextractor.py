from __future__ import annotations
import logging
import re
from typing import Any, Dict, List, Optional, Text

from rasa.engine.graph import GraphComponent, ExecutionContext
from rasa.engine.recipes.default_recipe import DefaultV1Recipe
from rasa.engine.storage.storage import ModelStorage
from rasa.engine.storage.resource import Resource
import rasa.shared.utils.io
import rasa.nlu.utils.pattern_utils as pattern_utils
from rasa.shared.nlu.training_data.training_data import TrainingData
from rasa.shared.nlu.training_data.message import Message
from rasa.shared.nlu.constants import (
    ENTITIES,
    ENTITY_ATTRIBUTE_VALUE,
    ENTITY_ATTRIBUTE_START,
    ENTITY_ATTRIBUTE_END,
    TEXT,
    ENTITY_ATTRIBUTE_TYPE,
    ENTITY_ATTRIBUTE_CONFIDENCE,
)
from rasa.nlu.extractors.extractor import EntityExtractorMixin
from thefuzz import process, fuzz


logger = logging.getLogger(__name__)


@DefaultV1Recipe.register(
    DefaultV1Recipe.ComponentType.ENTITY_EXTRACTOR, is_trainable=True
)
class FuzzyEntityExtractor(GraphComponent, EntityExtractorMixin):
    LOOKUP_PATH = "components/lookup"
    ATTRIBUTES = ["tv_brands", "tv_types"]
    threshold_score = 70 # TODO 80 for types

    @staticmethod
    def get_default_config() -> Dict[Text, Any]:
        return {}

    @classmethod
    def create(
        cls,
        config: Dict[Text, Any],
        model_storage: ModelStorage,
        resource: Resource,
        execution_context: ExecutionContext,
    ) -> FuzzyEntityExtractor:
        return cls(config, model_storage, resource)

    def __init__(
        self,
        config: Dict[Text, Any],
        model_storage: ModelStorage,
        resource: Resource,
        patterns: Optional[List[Dict[Text, Text]]] = None,
    ) -> None:
        self._config = {**self.get_default_config(), **config}
        self._model_storage = model_storage
        self._resource = resource

        # super(FuzzyEntityExtractor, self).__init__(config)
        self.lookups = {}
        for att in self.ATTRIBUTES:
            with open(f"{self.LOOKUP_PATH}/{att}.txt") as f:
                self.lookups[att] = f.read().splitlines()

    def train(self, training_data: TrainingData) -> Resource:
        pass

    def process(self, messages: List[Message]) -> List[Message]:
        for message in messages:
            entities = []
            tokens = message.get("text_tokens")
            if tokens != None:
                for name, list in self.lookups.items():
                    temp_entities = []
                    for token in tokens:
                        f = process.extractOne(
                            token.text,
                            list,
                            score_cutoff=self.threshold_score,
                            scorer=fuzz.ratio,
                        )

                        if f != None:
                            val, score = f
                            temp_entities.append({
                                ENTITY_ATTRIBUTE_TYPE: name[:-1],
                                ENTITY_ATTRIBUTE_START: token.start,
                                ENTITY_ATTRIBUTE_END: token.end,
                                TEXT: token.text,
                                ENTITY_ATTRIBUTE_VALUE: val,
                                ENTITY_ATTRIBUTE_CONFIDENCE: score,
                            })

                    if len(temp_entities) > 0:
                        max_conf_item = max(temp_entities, key=lambda x: x[ENTITY_ATTRIBUTE_CONFIDENCE])
                        print('max conf entity:', val, score)
                        entities.append(max_conf_item)
            if len(entities) > 0: #TODO test order(brand)->greet->order(brand)
                message.set(
                    ENTITIES,
                    message.get(ENTITIES, []) + entities,
                    add_to_output=True,
                )
        return messages
