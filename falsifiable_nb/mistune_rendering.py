import mistune
from nbconvert.filters.markdown_mistune import (
    MarkdownWithMath,
    IPythonRenderer,
)
from mistune import PLUGINS

from falsifiable_nb.mistune_plugins.inline_pandoc_footnotes import (
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


class FootnotesAsSidenotes(mistune.HTMLRenderer):
    """
    Renders pandoc-style footnotes as sidenotes.
    """

    # https://mistune.lepture.com/en/latest/advanced.html
    def footnote_ref(self, key, index):
        print("footnote_ref", key, index)
        return f'<sup class="footnote-ref"><a href="#fn-{key}">{index}</a></sup>'

    def footnote_item(self, key, text):
        print("footnote_item", key, text)
        return f'<li id="fn-{key}">{text}</li>'

    def footnotes(self, text):
        print("footnotes", text)
        return f'<div class="footnotes"><ol>{text}</ol></div>'
