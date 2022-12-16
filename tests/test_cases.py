"""Core tests."""
import unittest

import yaml

from semantic_llama.knowledge_extractor import KnowledgeExtractor
from tests import CASES_DIR, OUTPUT_DIR

CASES = [
    ("metagenome_study.Study", "environment-jgi2"),
    ("environmental_sample.Study", "environment-jgi1"),
    ("reaction.MultiGeneToReaction", "reaction-20657015"),
    ("reaction.GeneToReaction", "reaction-21290071"),
    ("gocam.GoCamAnnotations", "gocam-27929086"),
    ("gocam.GoCamAnnotations", "gocam-33246504"),
    ("environmental_sample.Study", "environmental-sample-hyporheic"),
    ("treatment.DiseaseTreatmentSummary", "treatment-marfan"),
    ("mendelian_disease.MendelianDisease", "mendelian-disease-sly"),
    ("mendelian_disease.MendelianDisease", "mendelian-disease-marfan"),
    ("gocam.GoCamAnnotations", "gocam-betacat"),
]


class TestCases(unittest.TestCase):
    """Test annotation."""

    def setUp(self) -> None:
        """Set up all extractors in advance."""
        ke_map = {}
        for template, _ in CASES:
            ke_map[template] = KnowledgeExtractor(template, recurse=True)
        self.ke_map = ke_map

    def test_cases(self):
        """Tests end to end knowledge extraction."""
        for template, input_name in CASES:
            ke = self.ke_map[template]
            input_file = CASES_DIR / f"{input_name}.txt"
            ann = ke.extract_from_file(input_file)
            #print(yaml.dump(ann.dict()))
            #for ne in ke.named_entities:
            #    print(yaml.dump(ne.dict()))
            #result_dict = {
            #    "input_file": str(input_file),
            #    "text": ke.last_text,
            #    "results": ann.dict(),
            #    "named_entities": [ne.dict() for ne in ke.named_entities],
            #}
            #print(yaml.dump(result_dict))
            output_file = str(OUTPUT_DIR / f"{input_name}.yaml")
            print(f"Writing {output_file}")
            with open(output_file, "w", encoding="utf-8") as f:
                yaml.dump(ann.dict(), f)
