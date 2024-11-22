"""Placeholder for packaging."""

import os
import sys

import click

from .main import monitor, get_report

version = "0.0.0-pre"


@click.command()
@click.argument("start", required=False)
@click.argument("run", required=False)
@click.option("--version", "-V", is_flag=True, help="Prints the version.")
@click.option("--help", "-H", is_flag=True, help="Prints the help section.")
@click.option(
    "--env",
    "-E",
    type=click.Path(exists=True),
    help="Environment configuration filepath.",
)
def commandline(*args, **kwargs) -> None:
    """Starter function to invoke PyUdisk via CLI commands.

    **Flags**
        - ``--version | -V``: Prints the version.
        - ``--help | -H``: Prints the help section.
        - ``--env | -E``: Environment configuration filepath.

    **Commands**
        ``start | run``: Initiates the monitoring/reporting process.
    """
    assert sys.argv[0].lower().endswith("pyudisk"), "Invalid commandline trigger!!"
    options = {
        "--version | -V": "Prints the version.",
        "--help | -H": "Prints the help section.",
        "--env | -E": "Environment configuration filepath.",
        "start | run": "Initiates the monitoring/reporting process.",
    }
    # weird way to increase spacing to keep all values monotonic
    _longest_key = len(max(options.keys()))
    _pretext = "\n\t* "
    choices = _pretext + _pretext.join(
        f"{k} {'·' * (_longest_key - len(k) + 8)}→ {v}".expandtabs()
        for k, v in options.items()
    )
    if kwargs.get("version"):
        click.echo(f"PyUdisk {version}")
        sys.exit(0)
    if kwargs.get("help"):
        click.echo(
            f"\nUsage: pyudisk [arbitrary-command]\nOptions (and corresponding behavior):{choices}"
        )
        sys.exit(0)
    trigger = kwargs.get("start") or kwargs.get("run")
    if trigger and trigger.lower() in ("start", "run"):
        # Click doesn't support assigning defaults like traditional dictionaries, so kwargs.get("max", 100) won't work
        if env_file := kwargs.get("env"):
            os.environ["env_file"] = env_file
        monitor()
        sys.exit(0)
    elif trigger:
        click.secho(f"\n{trigger!r} - Invalid command", fg="red")
    else:
        click.secho("\nNo command provided", fg="red")
    click.echo(
        f"Usage: pyudisk [arbitrary-command]\nOptions (and corresponding behavior):{choices}"
    )
    sys.exit(1)
