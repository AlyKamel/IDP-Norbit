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
    ENTITY = "tv_brand"
    LOOKUP_PATH = f"data/lookup/{ENTITY}.txt"
    threshold_score = 70

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

        with open(self.LOOKUP_PATH) as f:
            self.brand_lookup = f.read().splitlines()

    def train(self, training_data: TrainingData) -> Resource:
        pass

    def process(self, messages: List[Message]) -> List[Message]:
        for message in messages:
            tokens = message.get("text_tokens")
            if tokens is not None:
                temp_entities = []
                for token in tokens:
                    f = process.extractOne(
                        token.text,
                        self.brand_lookup,
                        score_cutoff=self.threshold_score,
                        scorer=fuzz.ratio,
                    )

                    if f is not None:
                        val, score = f
                        temp_entities.append({
                            ENTITY_ATTRIBUTE_TYPE: self.ENTITY,
                            ENTITY_ATTRIBUTE_START: token.start,
                            ENTITY_ATTRIBUTE_END: token.end,
                            TEXT: token.text,
                            ENTITY_ATTRIBUTE_VALUE: val,
                            ENTITY_ATTRIBUTE_CONFIDENCE: score,
                        })

                if temp_entities:
                    max_conf_item = max(
                        temp_entities, key=lambda x: x[ENTITY_ATTRIBUTE_CONFIDENCE])
                    print('max conf entity:', val, score)
                    message.set(
                        ENTITIES,
                        message.get(ENTITIES, []) +
                        self.add_extractor_name([max_conf_item]),
                        add_to_output=True,
                    )

        return messages
