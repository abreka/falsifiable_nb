import click


@click.group()
def cli():
    print("Hello, CLI")


@cli.command()
@click.option("--output-dir", default="", help="Path to the output directory")
@click.option("--watch", is_flag=True, help="Watch and regenerate continuously")
@click.option("--serve", is_flag=False, help="Serve the generated file")
@click.argument("notebook_path", type=click.Path(exists=True))
def generate(
    output_path,
    watch,
    serve,
    notebook_path,
):
    click.echo(f"Generating {notebook_path} to {output_path}")


if __name__ == "__main__":
    cli()
