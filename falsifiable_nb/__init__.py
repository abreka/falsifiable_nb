import time
from pathlib import Path

import click

from falsifiable_nb.html_exporter import FalsifiableNB
import nbformat
import webbrowser
from watchdog.events import FileSystemEventHandler


def generate_html(notebook_path: Path, output_dir: Path) -> Path:
    # Read the notebook
    with notebook_path.open() as f:
        nb = nbformat.read(f, as_version=4)

    # Create the exporter
    exporter = FalsifiableNB()
    body, resources = exporter.from_notebook_node(nb)

    # Write the output
    output_path = output_dir / notebook_path.with_suffix(".html").name
    with output_path.open("w") as f:
        f.write(body)

    # Return the location
    return output_path


def open_file_in_browser(file_path: Path):
    # Get the default web browser
    # TODO: Verify this works on Windows and MacOS
    # TODO: Fix this so it doesn't hang

    # populate _tryorder
    # x = webbrowser.get()
    # from webbrowser import _tryorder, _browsers
    # for i, browser in enumerate(_tryorder):
    #     # _tryorder[i] = browser + " &"
    #     print(_browsers[browser])

    browser = webbrowser.get()
    browser.open(file_path.absolute().as_uri(), autoraise=False)


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
