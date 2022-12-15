"""Core tests."""
import unittest

import yaml

from semantic_llama.knowledge_extractor import KnowledgeExtractor
from tests import CASES_DIR, OUTPUT_DIR

CASES = [
    ("gocam.GoCamAnnotations", "gocam-27929086"),
    ("gocam.GoCamAnnotations", "gocam-33246504"),
    ("environmental_sample.Study", "environmental-sample-hyporheic"),
    ("treatment.DiseaseTreatmentSummary", "treatment-marfan"),
    ("mendelian_disease.MendelianDisease", "mendelian-disease-sly"),
    ("mendelian_disease.MendelianDisease", "mendelian-disease-marfan"),
    ("gocam.GoCamAnnotations", "gocam-betacat"),
]


class TestAnnotate(unittest.TestCase):
    """Test annotation."""

    def setUp(self) -> None:
        """Set up all extractors in advance."""
        ke_map = {}
        for template, _ in CASES:
            ke_map[template] = KnowledgeExtractor(template)
        self.ke_map = ke_map

    def test_cases(self):
        """Tests end to end knowledge extraction."""
        for template, input_file in CASES:
            ke = self.ke_map[template]
            ann = ke.extract_from_file(CASES_DIR / f"{input_file}.txt")
            print(yaml.dump(ann.dict()))
            for ne in ke.named_entities:
                print(yaml.dump(ne.dict()))
            with open(str(OUTPUT_DIR / f"{input_file}.yaml"), "w", encoding="utf-8") as f:
                yaml.dump(ann.dict(), f)
