import mistune
from nbconvert.filters.markdown_mistune import (
    MarkdownWithMath,
    IPythonRenderer,
)
from mistune import PLUGINS

from falsifiable_nb.plugins.mistune.inline_footnotes import (
    plugin_inline_footnotes,
)

DEFAULT_PLUGINS = [
    "strikethrough",
    "table",
    "url",
    "def_list",
    "task_lists",
    "footnotes",
]


def render(source):
    """Convert a markdown string to HTML using mistune"""

    # See: https://github.com/jupyter/nbconvert/blob/main/nbconvert/filters/markdown_mistune.py
    plugins = [plugin_inline_footnotes] + [PLUGINS[p] for p in DEFAULT_PLUGINS]

    return MarkdownWithMath(
        renderer=IPythonRenderer(escape=False),
        plugins=plugins,
    ).render(source)
