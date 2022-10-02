from traitlets.config import Config


def preprocess_cell_removal(c: Config):
    """
    Remove cells from the notebook based on the metadata of the cell.

    See: https://nbconvert.readthedocs.io/en/latest/removing_cells.html

    :param c: the configuration object
    """
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
