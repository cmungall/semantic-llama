"""Command line interface for oak-ai."""
import codecs
import logging
import pickle
import sys

import click
import jsonlines
import yaml
from oaklib.implementations import BioPortalImplementation

from semantic_llama import __version__
from semantic_llama.io.markdown_exporter import MarkdownExporter
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
@click.option("-e", "--engine", help="Engine to use, e.g. text-davinci-003.")
@click.option(
    "--recurse/--no-recurse", default=False, show_default=True, help="Recursively parse structyres."
)
@click.option("-o", "--output",
              type=click.File(mode="wb"),
              default=sys.stdout,
              help="Output file.")
@click.option("-O", "--output-format",
                type=click.Choice(["json", "yaml", "pickle", "md"]),
                default="yaml",
                help="Output format.")
@click.argument("input", type=click.File("r"), default=sys.stdin)
def extract(template, input, output, output_format, **kwargs):
    """Parse openai results."""
    logging.info(f"Creating for {template}")
    ke = KnowledgeExtractor(template, **kwargs)
    text = input.read()
    logging.debug(f"Input text: {text}")
    results = ke.extract_from_text(text)
    if output_format == "pickle":
        output.write(pickle.dumps(results))
    elif output_format == "md":
        output = codecs.getwriter("utf-8")(output)
        exporter = MarkdownExporter()
        exporter.export(results, output)
    else:
        output = codecs.getwriter("utf-8")(output)
        output.write(yaml.dump(results.dict()))


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
@click.option("-t", "--template", default="core.NamedEntity", help="Template to use.")
@click.option("-o", "--output",
              type=click.File(mode="w"),
              default=sys.stdout,
              help="Output file.")
@click.argument("input")
def dump_completions(template, input, output):
    """Dumps cached completions."""
    logging.info(f"Creating for {template}")
    ke = KnowledgeExtractor(template)
    writer = jsonlines.Writer(output)
    for prompt, completion in ke.cached_completions(input):
        writer.write(dict(prompt=prompt, completion=completion))



@main.command()
def list():
    """Lists the templates."""
    print("TODO")


if __name__ == "__main__":
    main()
