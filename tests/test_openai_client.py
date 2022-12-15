"""Open AI client tests."""
import unittest

import yaml

from semantic_llama.clients.openai_client import OpenAIClient

PROMPT = """
example:

name: ornithine biosynthesis
def: The biological process that results in the output of ornithine, ornithine, an amino acid only rarely found in proteins, but which is important in living organisms as an intermediate in the reactions of the urea cycle and in arginine biosynthesis
parent: biosynthetic process
differentia:
  outputs: ornithine

===

name: selenocysteine biosynthesis
"""


class TestCompletion(unittest.TestCase):
    """Test annotation."""

    def setUp(self) -> None:
        """Set up."""
        self.llm_client = OpenAIClient()

    def test_completion(self):
        """Tests end to end knowledge extraction."""
        client = self.llm_client
        ann = client.complete(PROMPT)
        print(ann)