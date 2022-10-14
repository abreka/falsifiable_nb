import sys
import threading
from pathlib import Path
import time

import click
import nbformat
from traitlets.config import Config
from watchdog.events import FileSystemEventHandler
from threading import Thread
from falsifiable_nb import FalsifiableNB


def generate_html(notebook_path: Path, output_dir: Path) -> Path:
    # Read the notebook
    with notebook_path.open() as f:
        nb = nbformat.read(f, as_version=4)

    c = Config()

    # Set log level to info

    c.FalsifiableNB.preprocessors = [
        "falsifiable_nb.plugins.preprocessing.StripHiddenSource",
        "falsifiable_nb.plugins.preprocessing.StripEmptyCells",
        "nbconvert.preprocessors.TagRemovePreprocessor",
        "falsifiable_nb.plugins.preprocessing.ElideRemovedSource",
    ]
    c.FalsifiableNB.exclude_input_prompt = True
    c.FalsifiableNB.exclude_output_prompt = True

    c.TagRemovePreprocessor.remove_cell_tags = [
        "remove_cell",
        "private",
        "setup",
        "notes",
        "hidden",
        "install",
    ]
    c.TagRemovePreprocessor.remove_all_outputs_tags = ("remove_output", "assertion")
    c.TagRemovePreprocessor.remove_input_tags = ("remove_input", "output-generator")
    c.TagRemovePreprocessor.enabled = True

    c.TemplateExporter.filters = {
        "markdown2html": "falsifiable_nb.mistune_rendering.render"
    }

    #
    # Create the exporter
    exporter = FalsifiableNB(config=c)

    # Use markdown2html_pandoc to convert markdown to html
    # See:
    # https://github.com/jupyter/nbconvert/issues/248

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
    def __init__(
        self,
        notebook_path: Path,
        output_dir: Path,
        done_fn: echo_generated,
        debounce_time=0.1,
    ):
        self._notebook_path = notebook_path
        self._output_dir = output_dir
        self._done_fn = done_fn
        self._debouncer = Debouncer(self._handle_event, debounce_time)

    def stop(self):
        self._debouncer.stop()

    def on_modified(self, event):
        # TODO: doesn't fix multiple hit problem.
        if event.src_path == str(self._notebook_path):
            self._debouncer.observe(event)

    def _handle_event(self, event):
        output_path = generate_html(self._notebook_path, self._output_dir)
        self._done_fn(self._notebook_path, output_path)


class Debouncer:
    def __init__(self, callback_fn, debounce_time=0.1):
        self._handler = callback_fn
        self._debounce_time = debounce_time
        self._last_events = {}
        self._debounce_loop = True
        self._lock = threading.Lock()

        self._t = Thread(target=self.run, daemon=True)
        self._t.start()

    def observe(self, event):
        at = time.time()
        with self._lock:
            self._last_events[event.src_path] = (event, at)

    def run(self):
        while self._debounce_loop:

            # Collect events post-debounce.
            now, to_process = time.time(), {}
            with self._lock:
                for path, (event, at) in self._last_events.items():
                    if now - at > self._debounce_time:
                        to_process[path] = event

                # Remove events that can be processed within lock.
                for path in to_process:
                    del self._last_events[path]

            # Process events (outside of lock)
            for event in to_process.values():
                self._handler(event)

            time.sleep(self._debounce_time)

    def stop(self):
        self._debounce_loop = False
        self._t.join()
