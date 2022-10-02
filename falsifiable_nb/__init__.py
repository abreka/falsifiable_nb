from pathlib import Path

from falsifiable_nb.html_exporter import FalsifiableNB
import webbrowser

from falsifiable_nb.remove_cells import preprocess_cell_removal


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
