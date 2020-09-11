from pygments import highlight as _highlight
from pygments.lexers import SqlLexer
from pygments.formatters import HtmlFormatter


def style():
    style = HtmlFormatter().get_style_defs()
    return style


def highlight(text):
    # Generated HTML contains unnecessary newline at the end
    # before </pre> closing tag.
    # We need to remove that newline because it's screwing up
    # QTextEdit formatting and is being displayed
    # as a non-editable whitespace.
    highlighted_text = _highlight(text, SqlLexer(), HtmlFormatter()).strip()

    # Split generated HTML by last newline in it
    # argument 1 indicates that we only want to split the string
    # by one specified delimiter from the right.
    parts = highlighted_text.rsplit("\n", 1)

    # Glue back 2 split parts to get the HTML without last
    # unnecessary newline
    highlighted_text_no_last_newline = "".join(parts)
    return highlighted_text_no_last_newline
