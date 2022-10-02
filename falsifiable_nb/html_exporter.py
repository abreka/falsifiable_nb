import os
import os.path

import mistune
from nbconvert import preprocessors
from nbconvert.exporters.html import HTMLExporter
from nbformat import NotebookNode


class FalsifiableNB(HTMLExporter):
    """
    Falsifiable HTML exporter.
    """

    export_from_notebook = "FalsifiableNB"

    def _file_extension_default(self):
        return ".html"

    @property
    def template_paths(self):
        # BUG: See https://github.com/jupyter/nbconvert/issues/1492
        return super()._template_paths() + [
            os.path.join(os.path.dirname(__file__), "templates")
        ]

    def _template_file_default(self):
        return "falsifiable.html.j2"


class StripEmptyCells(preprocessors.Preprocessor):
    def preprocess(self, nb, resources):
        # TODO WRONG
        nb.cells = [c for c in nb.cells if c.source.strip()]
        return nb, resources


class StripHiddenSource(preprocessors.Preprocessor):
    def preprocess(self, nb: NotebookNode, resources):
        nb.cells = [add_hidden_tag_to_hidden_cells(c) for c in nb.cells]
        return nb, resources


class ElideRemovedSource(preprocessors.Preprocessor):
    def preprocess(self, nb, resources):
        nb.cells = [elide_removed_source(c) for c in nb.cells]
        return nb, resources


def elide_removed_source(cell):
    if cell.metadata.get("transient", {}).get("remove_source", False):
        cell.source = ""
    return cell


def add_hidden_tag_to_hidden_cells(cell):
    if is_hidden(cell):
        return copy_cell_and_add_tag(cell, "remove_input")
    return cell


def copy_cell_and_add_tag(cell, tag: str):
    new_cell = cell.copy()
    if "tags" not in new_cell.metadata:
        new_cell.metadata["tags"] = [tag]
    else:
        new_cell.metadata.tags.append(tag)
    return new_cell


def is_hidden(cell) -> bool:
    jupyter = cell.metadata.get("jupyter")
    if jupyter is None:
        return False

    return jupyter.get("source_hidden", False)
