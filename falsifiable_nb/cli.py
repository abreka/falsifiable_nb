import time
from pathlib import Path

import click

from falsifiable_nb import (
    open_file_in_browser,
)
from falsifiable_nb.generate import (
    generate_html,
    echo_generated,
    SingleNotebookChangedHandler,
)
from falsifiable_nb.http_server import serve_dir, port_range
from watchdog.observers import Observer


@click.group()
def cli():
    pass


@cli.command()
@click.option(
    "--output-dir", default="", help="Path to the output directory", type=click.Path()
)
@click.option("--watch", is_flag=True, help="Watch and regenerate continuously")
@click.option("--serve", is_flag=True, help="Serve the generated file")
@click.option("--open-browser", is_flag=True, help="Open in browser after generation")
@click.argument("notebook_path", type=click.Path(exists=True))
def generate(
    output_dir,
    watch,
    serve,
    open_browser,
    notebook_path,
):
    notebook_path = Path(notebook_path)
    if not output_dir:
        output_dir = notebook_path.parent

    output_path = _generate(notebook_path, output_dir)

    if open_browser:
        open_file_in_browser(output_path)

    httpd = None
    if serve:
        httpd = serve_dir(output_dir, port_sampler=port_range(8000, 8010))

    if watch:
        click.echo("Watching for changes...")
        observer = Observer()
        observer.schedule(
            SingleNotebookChangedHandler(notebook_path, output_dir, echo_generated),
            str(notebook_path.parent),
            recursive=False,
        )
        click.echo("Press Ctrl+C to stop")
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

    if httpd:
        httpd.shutdown()


def _generate(notebook_path, output_dir):
    output_path = generate_html(notebook_path, output_dir)
    echo_generated(notebook_path, output_path)
    return output_path


if __name__ == "__main__":
    cli()
