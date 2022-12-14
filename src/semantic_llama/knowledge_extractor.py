"""
Main Knowledge Extractor class.
"""
import importlib
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, TextIO, Tuple, Union

import openai
import pydantic
from linkml_runtime import SchemaView
from linkml_runtime.linkml_model import ClassDefinition
from oaklib import get_implementation_from_shorthand
from oaklib.datamodels.text_annotator import TextAnnotation, TextAnnotationConfiguration
from oaklib.interfaces import TextAnnotatorInterface
from oaklib.utilities.apikey_manager import get_apikey_value

from semantic_llama.clients import OpenAIClient

this_path = Path(__file__).parent

EXAMPLE = Union[str, pydantic.BaseModel]
FIELD = str
RESPONSE_ATOM = Union[str, Tuple[str, str]]
RESPONSE_DICT = Dict[FIELD, Union[RESPONSE_ATOM, List[RESPONSE_ATOM]]]


@dataclass
class KnowledgeExtractor(object):
    """Knowledge extractor."""

    template: str
    template_class: ClassDefinition = None
    template_pyclass = None
    schemaview: SchemaView = None
    api_key: str = None
    engine: str = "text-davinci-003"
    annotator: TextAnnotatorInterface = None
    annotators: Dict[str, List[TextAnnotatorInterface]] = None
    client: OpenAIClient = None

    def __post_init__(self):
        self.template_class = self._get_template_class(self.template)
        self.client = OpenAIClient()
        self.api_key = self._get_openai_api_key()
        openai.api_key = self.api_key

    def extract_from_text(self, text: str) -> pydantic.BaseModel:
        """
        Extract annotations from the given text.

        :param text:
        :return:
        """
        raw_text = self._raw_extract(text)
        logging.info(f"RAW TEXT: {raw_text}")
        return self.parse_completion_payload(raw_text)

    def extract_from_file(self, file: Union[str, Path, TextIO]) -> pydantic.BaseModel:
        """
        Extract annotations from the given text.

        :param file:
        :return:
        """
        if isinstance(file, str):
            file = Path(file)
        if isinstance(file, Path):
            with file.open() as f:
                text = f.read()
        else:
            text = file.read()
        return self.extract_from_text(text)

    def generalize(
        self, object: Union[pydantic.BaseModel, dict], examples: List[EXAMPLE]
    ) -> pydantic.BaseModel:
        """
        Generalize the given examples.

        :param examples:
        :return:
        """
        prompt = "example:\n"
        for example in examples:
            prompt += f"{example}\n\n"
        prompt += "\n\n===\n\n"
        if isinstance(object, pydantic.BaseModel):
            object = object.dict()
        prompt = ""
        for k, v in object.items():
            if v:
                prompt += f"{k}: {v}\n"
        payload = self.client.complete(prompt)
        return self.parse_completion_payload(payload)
        # response = openai.Completion.create(
        #    engine=self.engine,
        #    prompt=prompt,
        #    max_tokens=3000,
        # )
        # return self.parse_completion_payload(response.choices[0].text)

    def _get_openai_api_key(self):
        """Get the OpenAI API key from the environment."""
        # return os.environ.get("OPENAI_API_KEY")
        return get_apikey_value("openai")

    def _raw_extract(self, text) -> str:
        """
        Extract annotations from the given text.

        :param text:
        :return:
        """

        prompt = self.get_completion_prompt()
        full_text = f"{prompt}\n\nText:\n{text}"
        payload = self.client.complete(full_text)
        return payload
        # response = openai.Completion.create(
        #    engine=self.engine,
        #    prompt=full_text,
        #    max_tokens=3000,
        # )
        # return response.choices[0].text

    def _get_template_class(self, template: str) -> ClassDefinition:
        """Get the class for the given template."""
        logging.info(f"Loading schema for {template}")
        module_name, class_name = template.split(".", 1)
        templates_path = this_path / "templates"
        path_to_template = str(templates_path / f"{module_name}.yaml")
        mod = importlib.import_module(f"semantic_llama.templates.{module_name}")
        self.template_pyclass = mod.__dict__[class_name]
        sv = SchemaView(path_to_template)
        self.schemaview = sv
        logging.info(f"Getting class for template {template}")
        cls = None
        for c in sv.all_classes().values():
            if c.name == class_name:
                cls = c
                break
        if not cls:
            raise ValueError(f"Template {template} not found")
        return cls

    def get_completion_prompt(self) -> str:
        """Get the prompt for the given template."""
        prompt = "From the text below, extract the following entities in the following format:\n\n"
        for slot in self.schemaview.class_induced_slots(self.template_class.name):
            if "prompt" in slot.annotations:
                slot_prompt = slot.annotations["prompt"].value
            elif slot.description:
                slot_prompt = slot.description
            else:
                if slot.multivalued:
                    slot_prompt = f"semicolon-separated list of {slot.name}s"
                else:
                    slot_prompt = f"the value for {slot.name}"
            prompt += f"{slot.name}: <{slot_prompt}>\n"
        return prompt

    def _parse_response_to_dict(self, results: str) -> RESPONSE_DICT:
        """
        Parses the pseudo-YAML response from OpenAI into a dictionary object

        :param results:
        :return:
        """
        lines = results.splitlines()
        sv = self.schemaview
        ann = {}
        for line in lines:
            # each line is a key-value pair
            logging.info(f"PARSING LINE: {line}")
            line = line.strip()
            if not line:
                continue
            field, val = line.split(":", 1)
            if not val:
                logging.warning(f"Cannot parse {line}")
            field = field.lower().replace(" ", "_")
            slot = sv.induced_slot(field, self.template_class.name)
            val = val.strip()
            if slot.multivalued:
                vals = [v.strip() for v in val.split(";")]
            else:
                vals = [val]
            vals = [val for val in vals if val]
            inlined = False
            if slot.range in sv.all_classes():
                rng = sv.get_class(slot.range).name
                inlined = not sv.get_identifier_slot(rng) is not None
                print(f"SLOT: {slot.name} RANGE: {rng}, INLINED: {inlined}")
            if inlined:
                transformed = False
                for sep in [" - ", ":", "/", "*", "-"]:
                    if all([sep in v for v in vals]):
                        vals = [tuple(v.split(sep, 1)) for v in vals]
                        transformed = True
                        break
                if not transformed:
                    logging.warning(f"Did not find separator in {vals} for line {line}")
                    continue
            if slot.multivalued:
                ann[field] = vals
            else:
                ann[field] = vals[0]
        return ann

    def parse_completion_payload(self, results: str) -> pydantic.BaseModel:
        """
        Parse the completion payload into a pydantic class.

        :param results:
        :return:
        """
        raw = self._parse_response_to_dict(results)
        print(f"RAW: {raw}")
        return self.ground_annotation_object(raw)

    def ground_annotation_object(
        self, ann: RESPONSE_DICT, cls: ClassDefinition = None
    ) -> pydantic.BaseModel:
        """Ground the raw parse of the OpenAI payload.

        :param ann: Raw annotation object
        :param cls: schema class the ground object should instantiate
        :return: Grounded annotation object
        """
        logging.debug(f"Grounding annotation object {ann}")
        if cls is None:
            cls = self.template_class
        sv = self.schemaview
        new_ann = {}
        for field, vals in ann.items():
            if isinstance(vals, list):
                multivalued = True
            else:
                multivalued = False
                vals = [vals]
            slot = sv.induced_slot(field, cls.name)
            rng = sv.get_class(slot.range)
            new_ann[field] = []
            for val in vals:
                if isinstance(val, tuple):
                    sub_slots = sv.class_induced_slots(rng.name)
                    obj = {}
                    for i in range(0, len(val)):
                        sub_slot = sub_slots[i]
                        sub_rng = sv.get_class(sub_slot.range)
                        if not sub_rng:
                            logging.error(f"Cannot find range for {sub_slot.name}")
                        result = self.ground_text_to_id(val[i], sub_rng)
                        obj[sub_slot.name] = result
                else:
                    obj = self.ground_text_to_id(val, rng)
                if multivalued:
                    new_ann[field].append(obj)
                else:
                    new_ann[field] = obj
        logging.debug(f"Creating object from dict {new_ann}")
        print(new_ann)
        return self.template_pyclass(**new_ann)

    def ground_text_to_id(self, text: str, cls: ClassDefinition = None) -> str:
        """
        Ground the text to an ID.

        :param text: Text to ground, e.g. a gene symbol
        :param cls: schema class the ground object should instantiate
        :return: ID or input string if cannot be grounded
        """
        result = self.ground_text(text, cls)
        return result.object_id if result else text

    def ground_text(self, text: str, cls: ClassDefinition = None) -> Optional[TextAnnotation]:
        """
        Ground the given text to an object ID.

        :param text: text to ground, e.g. gene symbol
        :param cls: schema class the ground object should instantiate
        :return:
        """
        if cls is None:
            logging.error("No range")
            return
        logging.info(f"GROUNDING {text} using {cls.name}")
        config = TextAnnotationConfiguration(matches_whole_text=True)
        if self.annotators and cls.name in self.annotators:
            annotators = self.annotators[cls.name]
        else:
            if "annotators" not in cls.annotations:
                logging.error(f"No annotators for {cls.name}")
                return
            annotators = cls.annotations["annotators"].value.split(", ")
        logging.info(f" Annotators: {annotators}")
        for annotator in annotators:
            if isinstance(annotator, str):
                logging.info(f"Loading annotator {annotator}")
                annotator = get_implementation_from_shorthand(annotator)
            try:
                results = annotator.annotate_text(text, config)
                for result in results:
                    return result
            except Exception as e:
                logging.error(f"Error with {annotator} for {text}: {e}")
