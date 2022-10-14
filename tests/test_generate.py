import shutil
import time
from pathlib import Path

from falsifiable_nb.generate import SingleNotebookChangedHandler
from watchdog.observers import Observer


def copy_jupyter_style(input_path: Path, output_path: Path):
    with input_path.open() as src:
        with output_path.open("w") as dst:
            dst.write(src.read())


def test_jupyter_style_open_write_close_events(tmp_path):
    basic_fixture = Path(__file__).parent / "fixtures" / "001_basic.ipynb"
    notebook_path = tmp_path / "001_basic.ipynb"
    copy_jupyter_style(basic_fixture, notebook_path)

    observer = Observer()

    hits = []
    observer.schedule(
        # TODO: does observer call stop() on this handler?
        SingleNotebookChangedHandler(
            notebook_path,
            tmp_path,  # as output dir
            lambda nb_path, output_path: hits.append((nb_path, output_path)),
        ),
        str(tmp_path),
        recursive=False,
    )
    observer.start()

    # Hope initial write event propagated.
    time.sleep(0.2)
    hit_count = len(hits)

    # ========================================================================
    # This is ugly, but I don't know how to do it better.
    # ========================================================================

    # One write, one event.
    copy_jupyter_style(basic_fixture, notebook_path)
    for _ in range(10):
        n = len(hits)
        if n > hit_count:
            assert n == hit_count + 1
            hit_count = n
            break
        time.sleep(0.1)

    # Two quick writes, one event.
    copy_jupyter_style(basic_fixture, notebook_path)
    copy_jupyter_style(basic_fixture, notebook_path)
    for _ in range(10):
        n = len(hits)
        if n > hit_count:
            assert n == hit_count + 1
            hit_count = n
            break
        time.sleep(0.1)
    observer.stop()
    observer.join()

    # Remove the temporary directory
    shutil.rmtree(tmp_path)
