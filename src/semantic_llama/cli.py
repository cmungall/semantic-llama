"""Command line interface for oak-ai."""
import logging
import sys

import click
import yaml
from oaklib.implementations import BioPortalImplementation

from semantic_llama import __version__
from semantic_llama.knowledge_extractor import KnowledgeExtractor

__all__ = [
    "main",
]


@click.group()
@click.option("-v", "--verbose", count=True)
@click.option("-q", "--quiet")
@click.version_option(__version__)
def main(verbose: int, quiet: bool):
    """CLI for oak-ai.

    :param verbose: Verbosity while running.
    :param quiet: Boolean to be quiet or verbose.
    """
    logger = logging.getLogger()
    if verbose >= 2:
        logger.setLevel(level=logging.DEBUG)
    elif verbose == 1:
        logger.setLevel(level=logging.INFO)
    else:
        logger.setLevel(level=logging.WARNING)
    if quiet:
        logger.setLevel(level=logging.ERROR)


@main.command()
@click.option("-t", "--template", required=True, help="Template to use.")
@click.argument("input", type=click.File("r"), default=sys.stdin)
def extract(template, input):
    """Parse openai results."""
    logging.info(f"Creating for {template}")
    ke = KnowledgeExtractor(template)
    text = input.read()
    logging.debug(f"Input text: {text}")
    results = ke.extract_from_text(text)
    print(yaml.dump(results.dict()))


@main.command()
@click.option("-t", "--template", default="gocam", help="Template to use.")
@click.option("--input", "-i", type=click.File("r"), default=sys.stdin, help="Input file")
def parse(template, input):
    """Parse openai results."""
    logging.info(f"Creating for {template}")
    ke = KnowledgeExtractor(template)
    text = input.read()
    logging.debug(f"Input text: {text}")
    # ke.annotator = BioPortalImplementation()
    results = ke.parse_completion_payload(text)
    print(yaml.dump(results))


@main.command()
def list():
    """Lists the templates."""
    print("TODO")


if __name__ == "__main__":
    main()
