import shutil
import time
from pathlib import Path

from falsifiable_nb.generate import SingleNotebookChangedHandler, MacOSChangeHandler
from watchdog.observers import Observer


def copy_jupyter_style(input_path: Path, output_path: Path):
    with input_path.open() as src:
        with output_path.open("w") as dst:
            dst.write(src.read())


def test_jupyter_style_open_write_close_events(tmp_path):
    basic_fixture = Path(__file__).parent / "fixtures" / "001_basic.ipynb"
    notebook_path = tmp_path / "001_basic.ipynb"
    copy_jupyter_style(basic_fixture, notebook_path)

    time.sleep(0.1)

    observer = Observer()

    hits = []
    observer.schedule(
        SingleNotebookChangedHandler(
            notebook_path,
            tmp_path,  # as output dir
            # printit
            lambda nb_path, output_path: hits.append((nb_path, output_path)),
        ),
        str(tmp_path),
        recursive=False,
    )
    observer.start()

    # This is ugly, but I don't know how to do it better.
    time.sleep(0.1)
    for _ in range(3):
        copy_jupyter_style(basic_fixture, notebook_path)
        time.sleep(0.1)
    assert len(hits) == 3

    observer.stop()
    observer.join()

    # Remove the temporary directory
    shutil.rmtree(tmp_path)
