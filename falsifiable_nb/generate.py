import time
from pathlib import Path

import click
import nbformat
from nbconvert.preprocessors import TagRemovePreprocessor
from traitlets.config import Config
from watchdog.events import FileSystemEventHandler

from falsifiable_nb import FalsifiableNB, preprocess_cell_removal


def generate_html(notebook_path: Path, output_dir: Path) -> Path:
    # Read the notebook
    with notebook_path.open() as f:
        nb = nbformat.read(f, as_version=4)

    c = Config()

    # Set log level to info

    c.FalsifiableNB.preprocessors = [
        "falsifiable_nb.html_exporter.StripHiddenSource",
        "falsifiable_nb.html_exporter.StripEmptyCells",
        "nbconvert.preprocessors.TagRemovePreprocessor",
        "falsifiable_nb.html_exporter.ElideRemovedSource",
    ]
    c.FalsifiableNB.exclude_input_prompt = True
    c.FalsifiableNB.exclude_output_prompt = True
    preprocess_cell_removal(c)

    c.TemplateExporter.filters = {
        "markdown2html": "falsifiable_nb.mistune_rendering.render"
    }

    #
    # Create the exporter
    exporter = FalsifiableNB(config=c)

    # Use markdown2html_pandoc to convert markdown to html
    # See:
    # https://github.com/jupyter/nbconvert/issues/248

    print(c.FalsifiableNB.filters)
    print(c.TemplateExporter.filters)

    # exporter.register_preprocessor(TagRemovePreprocessor(config=c), True)
    body, resources = exporter.from_notebook_node(nb)

    # Write the output
    output_path = output_dir / notebook_path.with_suffix(".html").name
    with output_path.open("w") as f:
        f.write(body)

    # Return the location
    return output_path


def echo_generated(notebook_path: Path, output_path: Path):
    click.echo(f"Generated {output_path}")


class SingleNotebookChangedHandler(FileSystemEventHandler):
    def __init__(self, notebook_path: Path, output_dir: Path, done_fn: echo_generated):
        self._notebook_path = notebook_path
        self._output_dir = output_dir
        self._done_fn = done_fn

    def on_modified(self, event):

        if event.src_path == str(self._notebook_path):
            # TODO: this is a horrible kludge. The modified event is triggered
            # on start to write. It is often the case that this modification event
            # fires and calls generate_html before the file is fully written!
            time.sleep(0.1)
            output_path = generate_html(self._notebook_path, self._output_dir)
            self._done_fn(self._notebook_path, output_path)
