"""
Pandoc has support for inline footnotes that look like,

     Here is some text^[with an inline footnote].

I used them a lot in my dissertation and old falsifiable rendering style.

Using regexp is difficult here because the footnote text can contain other
markdown elements which use a `]` character.
"""
import re
from mistune import Markdown, unikey

INLINE_FOOTNOTE_PATTERN = re.compile(r"\^\[([^\]]+)\]")

assert (
    INLINE_FOOTNOTE_PATTERN.search("some text ^[with an inline footnote] lol").group(1)
    == "with an inline footnote"
)


def md_footnotes_hook(md, result, state):
    # TODO: This isn't the right way to do things, but it is a way that works.
    replacements = []

    index = state.get("footnote_index", 0)
    index += 1

    for footnote in INLINE_FOOTNOTE_PATTERN.finditer(result):
        inner = footnote.group(1)
        replacements.append(
            (
                footnote.group(0),
                f"""<label for="sn-{index}" class="margin-toggle sidenote-number"></label><input type="checkbox" id="sn-{index}" class="margin-toggle"/><span id="sn-{index}" class="sidenote">{inner}</span>""",
            )
        )
        index += 1

    if replacements:
        state["footnote_index"] = index

    for old, new in replacements:
        result = result.replace(old, new)

    return result


def plugin_inline_footnotes(md: Markdown) -> None:
    md.after_render_hooks.append(md_footnotes_hook)
