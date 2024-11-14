import os
import pathlib
import subprocess
from collections.abc import Generator
from datetime import datetime
from typing import List, Dict

import jinja2
from pydantic import FilePath, NewPath

from .config import EnvConfig
from .logger import LOGGER
from .models import Disk
from .notification import notification_service, send_report


def load_sample(filename: str) -> str:
    """Loads a sample file for testing purposes.

    Args:
        filename: Sample file to load.

    Returns:
        str:
        Content of the sample file.
    """
    with open(filename) as file:
        return file.read()


def disk_info(disk_lib: FilePath = "/usr/bin/udisksctl") -> Generator[Disk]:
    """Gathers disk information using the dump from 'udisksctl' command.

    Args:
        disk_lib: Path to the 'udisksctl' command.

    Yields:
        Disk:
        Data structure parsed as a Disk object.
    """
    dry_run = os.environ.get("DRY_RUN", "false") == "true"
    if dry_run:
        text = load_sample(
            filename=os.environ.get("SAMPLE_FILE", "sample.txt")
        )
    else:
        try:
            output = subprocess.check_output(f"{disk_lib} dump", shell=True)
        except subprocess.CalledProcessError as error:
            LOGGER.error(error)
            return
        text = output.decode(encoding="UTF-8")
    formatted = {}
    head = None
    category = None
    head_check = "/org/freedesktop/UDisks2/drives/"
    cat1_check = "org.freedesktop.UDisks2.Drive:"
    cat2_check = "org.freedesktop.UDisks2.Drive.Ata:"
    for line in text.splitlines():
        if line.startswith(head_check):
            head = line.replace(head_check, "").strip()
            formatted[head] = {}
        elif line.strip() in (cat1_check, cat2_check):
            category = (
                line.replace(cat1_check, "Info")
                .replace(cat2_check, "Attributes")
                .strip()
            )
            formatted[head][category] = {}
        elif head and category:
            try:
                key, val = line.strip().split(":", 1)
                key = key.strip()
                val = val.strip()
            except ValueError as error:
                assert str(error) == "not enough values to unpack (expected 2, got 1)", error
                continue
            formatted[head][category][key] = val
    for key, value in formatted.items():
        yield Disk(id=key, model="", **value)


def monitor_disk(env: EnvConfig) -> Generator[Disk]:
    """Monitors disk attributes based on the configuration.

    Args:
        env: Environment variables configuration.

    Yields:
        Disk:
        Data structure parsed as a Disk object.
    """
    message = ""
    for disk in disk_info(env.disk_lib):
        for metric in env.metrics:
            attribute = disk.Attributes.model_dump().get(metric.attribute)
            if metric.max_threshold and attribute >= metric.max_threshold:
                msg = f"{metric.attribute!r} for {disk.id!r} is >= {metric.max_threshold} at {attribute}"
                LOGGER.critical(msg)
                message += msg + "\n"
            if metric.min_threshold and attribute <= metric.min_threshold:
                msg = f"{metric.attribute!r} for {disk.id!r} is <= {metric.min_threshold} at {attribute}"
                LOGGER.critical(msg)
                message += msg + "\n"
            if metric.equal_match and attribute != metric.equal_match:
                msg = f"{metric.attribute!r} for {disk.id!r} IS NOT {metric.equal_match} at {attribute}"
                LOGGER.critical(msg)
                message += msg + "\n"
        yield disk
    notification_service(
        title="Disk Monitor Alert!!",
        message=message, env_config=env
    )


def generate_report(data: List[Dict[str, str | int | float | bool]], filepath: NewPath) -> str:
    """Generates an HTML report using Jinja2 template.

    Args:
        data: Data to render in the template.
        filepath: Path to save the HTML report locally.

    Returns:
        str:
        Rendered HTML report.
    """
    template_dir = pathlib.Path(__file__).parent
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))  # Adjust path as needed
    template = env.get_template('template.html')
    html_output = template.render(data=data)
    if filepath:
        with open(filepath, 'w') as file:
            file.write(html_output)
            file.flush()
    return html_output


def monitor(**kwargs) -> None:
    """Entrypoint for the disk monitoring service.

    Args:
        **kwargs: Arbitrary keyword arguments.
    """
    # todo: use psutil to get utilization, partitions, mount points, and model info
    env = EnvConfig(**kwargs)
    report = [
        disk.model_dump() for disk in monitor_disk(env)
    ]
    if report:
        LOGGER.info("Disk monitor reporthas been generated for %d disks", len(report))
        if env.disk_report:
            if env.gmail_user and env.gmail_pass and env.recipient:
                LOGGER.info("Sending an email disk report to %s", env.recipient)
                send_report(
                    title=f"Disk Report - {datetime.now().strftime('%c')}",
                    user=env.gmail_user,
                    password=env.gmail_pass,
                    recipient=env.recipient,
                    content=generate_report(report, env.report_file)
                )
            else:
                LOGGER.warning("Reporting feature was enabled but necessary notification vars not found!!")
        else:
            LOGGER.info("Reporting feature has been disabled!")
    else:
        LOGGER.warning("Disk monitor report was not generated!")
