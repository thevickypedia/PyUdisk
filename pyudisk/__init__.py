"""Placeholder for packaging."""

import os
import sys

import click

from .main import EnvConfig, generate_report, monitor, smart_metrics  # noqa: F401

version = "1.1.0a0"


@click.command()
@click.argument("monitor", required=False)
@click.argument("report", required=False)
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
        - ``monitor``: Initiates the monitoring and alerting process.
        - ``report``: Generates a full disk-report HTML.
    """
    assert sys.argv[0].lower().endswith("pyudisk"), "Invalid commandline trigger!!"
    options = {
        "--version | -V": "Prints the version.",
        "--help | -H": "Prints the help section.",
        "--env | -E": "Environment configuration filepath.",
        "monitor": "Initiates the monitoring and alerting process.",
        "report": "Generates a full disk-report HTML",
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
    trigger = kwargs.get("monitor") or kwargs.get("report")
    if trigger:
        trigger = trigger.lower()
        # Click doesn't support assigning defaults like traditional dictionaries, so kwargs.get("max", 100) won't work
        if env_file := kwargs.get("env"):
            os.environ["env_file"] = env_file
        if trigger == "monitor":
            monitor()
            sys.exit(0)
        if trigger == "report":
            generate_report()
            sys.exit(0)
        else:
            click.secho(f"\n{trigger!r} - Invalid command", fg="red")
    else:
        click.secho("\nNo command provided", fg="red")
    click.echo(
        f"Usage: pyudisk [arbitrary-command]\nOptions (and corresponding behavior):{choices}"
    )
    sys.exit(1)
