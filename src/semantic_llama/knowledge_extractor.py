"""
Main Knowledge Extractor class.
"""
import importlib
import logging
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Dict, List, Optional, TextIO, Tuple, Union, Any, Iterator

import openai
import pydantic
from linkml_runtime import SchemaView
from linkml_runtime.linkml_model import ClassDefinition, SlotDefinition
from oaklib import get_implementation_from_shorthand, BasicOntologyInterface
from oaklib.datamodels.text_annotator import TextAnnotation, TextAnnotationConfiguration
from oaklib.interfaces import TextAnnotatorInterface
from oaklib.utilities.apikey_manager import get_apikey_value

from semantic_llama.clients import OpenAIClient
from semantic_llama.templates.core import NamedEntity, ExtractionResult

this_path = Path(__file__).parent

EXAMPLE = Union[str, pydantic.BaseModel, dict]
FIELD = str
RESPONSE_ATOM = Union[str, "ResponseAtom"]
RESPONSE_DICT = Dict[FIELD, Union[RESPONSE_ATOM, List[RESPONSE_ATOM]]]


DATAMODELS = [
    "treatment.DiseaseTreatmentSummary",
    "gocam.GoCamAnnotations",
    "bioloigical_process.BiologicalProcess",
    "environmental_sample.Study",
    "mendelian_disease.MendelianDisease",
    "reaction.Reaction",
    "recipe.Recipe",
]

@dataclass
class KnowledgeExtractor(object):
    """Knowledge extractor."""

    template: str
    template_class: ClassDefinition = None
    template_pyclass = None
    template_module: ModuleType = None
    schemaview: SchemaView = None
    api_key: str = None
    engine: str = "text-davinci-003"
    annotator: TextAnnotatorInterface = None
    annotators: Dict[str, List[TextAnnotatorInterface]] = None
    labelers: List[BasicOntologyInterface] = None
    client: OpenAIClient = None
    recurse: bool = False
    named_entities: List[NamedEntity] = None
    last_text: str = None
    last_prompt: str = None

    def __post_init__(self):
        self.template_class = self._get_template_class(self.template)
        self.client = OpenAIClient()
        self.api_key = self._get_openai_api_key()
        openai.api_key = self.api_key

    def extract_from_text(self, text: str, cls: ClassDefinition = None) -> ExtractionResult:
        """
        Extract annotations from the given text.

        :param text:
        :param cls:
        :return:
        """
        raw_text = self._raw_extract(text, cls)
        logging.info(f"RAW TEXT: {raw_text}")
        r = self.parse_completion_payload(raw_text, cls)
        return ExtractionResult(input_text=text,
                                raw_completion_output=raw_text,
                                prompt=self.last_prompt,
                                results=r,
                                named_entities=self.named_entities)

    def _extract_from_text_to_dict(self, text: str, cls: ClassDefinition = None) -> RESPONSE_DICT:
        raw_text = self._raw_extract(text, cls)
        return self._parse_response_to_dict(raw_text, cls)

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
        self.last_text = text
        r = self.extract_from_text(text)
        r.input_id = str(file)
        return r

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
            prompt += f"{self._serialize_example(example)}\n\n"
        prompt += "\n\n===\n\n"
        if isinstance(object, pydantic.BaseModel):
            object = object.dict()
        for k, v in object.items():
            if v:
                prompt += f"{k}: {v}\n"
        print(f"PROMPT: {prompt}")
        payload = self.client.complete(prompt)
        return self.parse_completion_payload(payload, object=object)

    def _serialize_example(self, example: EXAMPLE, cls: ClassDefinition = None) -> str:
        if cls is None:
            cls = self.template_class
        if isinstance(example, str):
            return example
        if isinstance(example, pydantic.BaseModel):
            example = example.dict()
        lines = []
        sv = self.schemaview
        for k, v in example.items():
            slot = sv.induced_slot(k, cls.name)
            v_serialized = self._serialize_value(v, slot)
            lines.append(f"{k}: {v_serialized}")
        return "\n".join(lines)

    def _serialize_value(self, val: Any, slot: SlotDefinition) -> str:
        if val is None:
            return ""
        if isinstance(val, list):
            return "; ".join([self._serialize_value(v, slot) for v in val if v])
        if isinstance(val, dict):
            for _k, v in val.items():
                return " - ".join([self._serialize_value(v, slot) for v in val if v])
        sv = self.schemaview
        if slot.range in sv.all_classes():
            if self.labelers:
                for labeler in self.labelers:
                    label = labeler.label(val)
                    if label:
                        return label
        return val

    def _get_openai_api_key(self):
        """Get the OpenAI API key from the environment."""
        # return os.environ.get("OPENAI_API_KEY")
        return get_apikey_value("openai")

    def _raw_extract(self, text, cls: ClassDefinition = None) -> str:
        """
        Extract annotations from the given text.

        :param text:
        :return:
        """

        prompt = self.get_completion_prompt(cls, text)
        self.last_prompt = prompt
        full_text = f"{prompt}\n\nText:\n{text}\n\n===\n\n"
        payload = self.client.complete(full_text)
        return payload

    def _get_template_class(self, template: str) -> ClassDefinition:
        """Get the class for the given template."""
        logging.info(f"Loading schema for {template}")
        module_name, class_name = template.split(".", 1)
        templates_path = this_path / "templates"
        path_to_template = str(templates_path / f"{module_name}.yaml")
        mod = importlib.import_module(f"semantic_llama.templates.{module_name}")
        self.template_module = mod
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

    def get_completion_prompt(self, cls: ClassDefinition = None, text: str = None) -> str:
        """Get the prompt for the given template."""
        if cls is None:
            cls = self.template_class
        if not text or ("\n" in text or len(text) > 60):
            prompt = (
                "From the text below, extract the following entities in the following format:\n\n"
            )
        else:
            prompt = "Split the following piece of text into fields in the following format:\n\n"
        for slot in self.schemaview.class_induced_slots(cls.name):
            if "prompt.skip" in slot.annotations:
                continue
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
        # prompt += "Do not answer if you don't know\n\n"
        return prompt

    def _parse_response_to_dict(
        self, results: str, cls: ClassDefinition = None
    ) -> Optional[RESPONSE_DICT]:
        """
        Parses the pseudo-YAML response from OpenAI into a dictionary object.

        E.g.

            foo: a; b; c

        becomes

            {"foo": ["a", "b", "c"]}

        :param results:
        :return:
        """
        lines = results.splitlines()
        ann = {}
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if ":" not in line:
                logging.warning(f"Line {line} does not contain a colon")
                return
            r = self._parse_line_to_dict(line, cls)
            if r is not None:
                field, val = r
                ann[field] = val
        return ann

    def _parse_line_to_dict(
        self, line: str, cls: ClassDefinition = None
    ) -> Optional[Tuple[FIELD, RESPONSE_ATOM]]:
        if cls is None:
            cls = self.template_class
        sv = self.schemaview
        # each line is a key-value pair
        logging.info(f"PARSING LINE: {line}")
        field, val = line.split(":", 1)
        if not val:
            logging.warning(f"Cannot parse {line}")
            return
        # The LLML may mutate the output format somewhat,
        # randomly pluralizing or replacing spaces with underscores
        field = field.lower().replace(" ", "_")
        cls_slots = sv.class_slots(cls.name)
        slot = None
        if field in cls_slots:
            slot = sv.induced_slot(field, cls.name)
        else:
            if field.endswith("s"):
                field = field[:-1]
            if field in cls_slots:
                slot = sv.induced_slot(field, cls.name)
        if not slot:
            logging.error(f"Cannot find slot for {field} in {line}")
            # raise ValueError(f"Cannot find slot for {field} in {line}")
            return
        inlined = slot.inlined
        slot_range = sv.get_class(slot.range)
        if not inlined:
            if slot.range in sv.all_classes():
                inlined = sv.get_identifier_slot(slot_range.name) is None
        val = val.strip()
        if slot.multivalued:
            vals = [v.strip() for v in val.split(";")]
        else:
            vals = [val]
        vals = [val for val in vals if val]
        logging.debug(f"SLOT: {slot.name} INL: {inlined} VALS: {vals}")
        if inlined:
            transformed = False
            slots_of_range = sv.class_slots(slot_range.name)
            if self.recurse or len(slots_of_range) > 2:
                vals = [self._extract_from_text_to_dict(v, slot_range) for v in vals]
            else:
                for sep in [" - ", ":", "/", "*", "-"]:
                    if all([sep in v for v in vals]):
                        vals = [dict(zip(slots_of_range, v.split(sep, 1))) for v in vals]
                        transformed = True
                        break
                if not transformed:
                    logging.warning(f"Did not find separator in {vals} for line {line}")
                    return
        # transform back from list to single value if not multivalued
        if slot.multivalued:
            final_val = vals
        else:
            if len(vals) != 1:
                logging.error(f"Expected 1 value for {slot.name} in '{line}' but got {vals}")
            final_val = vals[0]
        return field, final_val

    def parse_completion_payload(
        self, results: str, cls: ClassDefinition = None, object: dict = None
    ) -> pydantic.BaseModel:
        """
        Parse the completion payload into a pydantic class.

        :param results:
        :param cls:
        :param object:
        :return:
        """
        raw = self._parse_response_to_dict(results, cls)
        print(f"RAW: {raw}")
        if object:
            raw = {**object, **raw}
        return self.ground_annotation_object(raw, cls)

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
        if ann is None:
            logging.error(f"Cannot ground None annotation, cls={cls.name}")
            return
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
                if not val:
                    continue
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
                elif isinstance(val, dict):
                    obj = self.ground_annotation_object(val, rng)
                else:
                    obj = self.ground_text_to_id(val, rng)
                if multivalued:
                    new_ann[field].append(obj)
                else:
                    new_ann[field] = obj
        logging.debug(f"Creating object from dict {new_ann}")
        print(new_ann)
        py_cls = self.template_module.__dict__[cls.name]
        return py_cls(**new_ann)

    def ground_text_to_id(self, text: str, cls: ClassDefinition = None) -> str:
        """
        Ground the text to an ID.

        :param text: Text to ground, e.g. a gene symbol
        :param cls: schema class the ground object should instantiate
        :return: ID or input string if cannot be grounded
        """
        result = self.ground_text(text, cls)
        if result:
            if self.named_entities is None:
                self.named_entities = []
            self.named_entities.append(NamedEntity(id=result.object_id, label=text))
            return result.object_id
        if self.recurse and cls:
            print(f"RECURSING: {text} cls={cls.name}")
            obj = self.extract_from_text(text, cls).results
            if obj:
                if self.named_entities is None:
                    self.named_entities = []
                obj.id = text
                self.named_entities.append(obj)
        return text

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

    def cached_completions(self, search_term: str = None, engine: str = None) -> Iterator[Tuple[str, str]]:
        if engine is None:
            engine = self.engine
        cur = self.client.db_connection()
        res = cur.execute("SELECT prompt, payload FROM cache WHERE engine=?", (engine,))
        for row in res:
            if search_term and search_term not in row[0]:
                continue
            yield row
