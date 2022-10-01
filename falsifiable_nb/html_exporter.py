import os
import os.path

from nbconvert.exporters.html import HTMLExporter


class FalsifiableNB(HTMLExporter):
    """
    Falsifiable HTML exporter.
    """

    export_from_notebook = "Falsifiable"

    def _file_extension_default(self):
        return ".html"

    @property
    def template_paths(self):
        # BUG: See https://github.com/jupyter/nbconvert/issues/1492
        return super()._template_paths() + [
            os.path.join(os.path.dirname(__file__), "templates")
        ]

    def _template_file_default(self):
        return "falsifiable.tpl"
