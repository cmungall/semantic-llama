"""
Uses code-davinci-002

Note: this has a tendency to be over-creative.

Note also that fine-tuning can't be done; see:

https://community.openai.com/t/finetuning-code-davinci/23132/2
"""
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import pydantic
from linkml_runtime.linkml_model import ClassDefinition, SlotDefinition
from oaklib import get_implementation_from_shorthand
from oaklib.datamodels.text_annotator import TextAnnotation, TextAnnotationConfiguration

from semantic_llama.engines.engine import EXAMPLE, FIELD, OBJECT, KnowledgeEngine
from semantic_llama.templates.core import ExtractionResult, NamedEntity

this_path = Path(__file__).parent


RESPONSE_ATOM = Union[str, "ResponseAtom"]
RESPONSE_DICT = Dict[FIELD, Union[RESPONSE_ATOM, List[RESPONSE_ATOM]]]


@dataclass
class CodeModelKnowledgeEngine(KnowledgeEngine):
    """Knowledge extractor."""

    engine: str = "code-davinci-002"
    recurse: bool = True

    def extract_from_text(
        self, text: str, cls: ClassDefinition = None, object: OBJECT = None
    ) -> ExtractionResult:
        pass

    def generalize(
        self, object: Union[pydantic.BaseModel, dict], examples: List[EXAMPLE]
    ) -> ExtractionResult:
        for example in examples:
            self._serialize_example(example)
