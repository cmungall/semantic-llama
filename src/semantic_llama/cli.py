"""Command line interface for oak-ai."""
import codecs
import logging
import pickle
import sys
from io import BytesIO

import click
import jsonlines
import yaml

from semantic_llama import __version__
from semantic_llama.clients.pubmed_client import PubmedClient
from semantic_llama.engines.text_model_knowledge_engine import TextModelKnowledgeEngine
from semantic_llama.io.markdown_exporter import MarkdownExporter

__all__ = [
    "main",
]

from semantic_llama.templates.core import ExtractionResult


def write_extraction(results: ExtractionResult, output: BytesIO, output_format: str = None):
    if output_format == "pickle":
        output.write(pickle.dumps(results))
    elif output_format == "md":
        output = codecs.getwriter("utf-8")(output)
        exporter = MarkdownExporter()
        exporter.export(results, output)
    else:
        output = codecs.getwriter("utf-8")(output)
        output.write(yaml.dump(results.dict()))


template_option = click.option("-t", "--template", required=True, help="Template to use.")
engine_option = click.option("-e", "--engine", help="Engine to use, e.g. text-davinci-003.")
recurse_option = click.option(
    "--recurse/--no-recurse", default=True, show_default=True, help="Recursively parse structyres."
)
output_option_wb = click.option(
    "-o", "--output", type=click.File(mode="wb"), default=sys.stdout, help="Output file."
)
output_format_options = click.option(
    "-O",
    "--output-format",
    type=click.Choice(["json", "yaml", "pickle", "md"]),
    default="yaml",
    help="Output format.",
)


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
@template_option
@engine_option
@recurse_option
@output_option_wb
@output_format_options
@click.argument("input")
def extract(template, input, output, output_format, **kwargs):
    """Extract knowledge from text."""
    logging.info(f"Creating for {template}")
    ke = TextModelKnowledgeEngine(template, **kwargs)
    if not input or input == "-":
        input = sys.stdin
    else:
        input = open(input, "r")
    text = input.read()
    logging.debug(f"Input text: {text}")
    results = ke.extract_from_text(text)
    write_extraction(results, output, output_format)


@main.command()
@template_option
@engine_option
@recurse_option
@output_option_wb
@output_format_options
@click.argument("input")
def pubmed_extract(template, input, output, output_format, **kwargs):
    """Extract knowledge from text."""
    logging.info(f"Creating for {template}")
    pmc = PubmedClient()
    text = pmc.text(input)
    ke = TextModelKnowledgeEngine(template, **kwargs)
    logging.debug(f"Input text: {text}")
    results = ke.extract_from_text(text)
    write_extraction(results, output, output_format)


@main.command()
@template_option
@engine_option
@click.option("-E", "--examples", type=click.File("r"), help="File of example objects.")
@recurse_option
@output_option_wb
@output_format_options
@click.argument("object")
def fill(template, object: str, examples, output, output_format, **kwargs):
    """Fills in missing values."""
    logging.info(f"Creating for {template}")
    ke = TextModelKnowledgeEngine(template, **kwargs)
    object = yaml.safe_load(object)
    logging.info(f"Object to fill =  {object}")
    logging.info(f"Loading {examples}")
    examples = yaml.safe_load(examples)
    logging.debug(f"Input object: {object}")
    results = ke.generalize(object, examples)
    output.write(yaml.dump(results.dict()))


@main.command()
@template_option
@click.option("--input", "-i", type=click.File("r"), default=sys.stdin, help="Input file")
def parse(template, input):
    """Parse openai results."""
    logging.info(f"Creating for {template}")
    ke = TextModelKnowledgeEngine(template)
    text = input.read()
    logging.debug(f"Input text: {text}")
    # ke.annotator = BioPortalImplementation()
    results = ke.parse_completion_payload(text)
    print(yaml.dump(results))


@main.command()
@template_option
@click.option("-o", "--output", type=click.File(mode="w"), default=sys.stdout, help="Output file.")
@output_format_options
@click.option("-m", "match", help="Match string to use for filtering.")
@click.option("-D", "database", help="Path to sqlite database.")
def dump_completions(template, match, database, output, output_format):
    """Dumps cached completions."""
    logging.info(f"Creating for {template}")
    ke = TextModelKnowledgeEngine(template)
    if database:
        ke.client.cache_db_path = database
    if output_format == "jsonl":
        writer = jsonlines.Writer(output)
        for prompt, completion in ke.cached_completions(match):
            writer.write(dict(prompt=prompt, completion=completion))
    elif output_format == "yaml":
        for prompt, completion in ke.cached_completions(match):
            output.write(yaml.dump(dict(prompt=prompt, completion=completion)))
    else:
        output.write("# Cached Completions:\n")
        for prompt, completion in ke.cached_completions(match):
            output.write("## Entry\n")
            output.write(f"### Prompt:\n\n {prompt}\n\n")
            output.write(f"### Completion:\n\n {completion}\n\n")


@main.command()
@click.option("-o", "--output", type=click.File(mode="w"), default=sys.stdout, help="Output file.")
@click.argument("input", type=click.File("r"))
def convert_examples(input, output):
    """Converts training examples from YAML."""
    logging.info(f"Creating examples for {input}")
    example_doc = yaml.safe_load(input)
    writer = jsonlines.Writer(output)
    for example in example_doc["examples"]:
        prompt = example["prompt"]
        completion = yaml.dump(example["completion"], sort_keys=False)
        writer.write(dict(prompt=prompt, completion=completion))


@main.command()
def list():
    """Lists the templates."""
    print("TODO")


if __name__ == "__main__":
    main()
