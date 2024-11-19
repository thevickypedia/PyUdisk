import json
import os
import pathlib
import subprocess
from collections.abc import Generator
from datetime import datetime
from typing import Dict, List

import jinja2
import psutil
from psutil._common import sdiskpart
from pydantic import FilePath, NewPath

from .config import EnvConfig
from .logger import LOGGER
from .models import Disk
from .notification import notification_service, send_report


def load_partitions(filename: str) -> Generator[sdiskpart]:
    """Loads disk partitions from a JSON file.

    Args:
        filename: Source file to load partitions from.

    Yields:
        sdiskpart:
        Disk partition data structure.
    """
    with open(filename) as file:
        partitions = json.load(file)
    keys = list(sdiskpart._fields)
    for partition in partitions:
        result_dict = dict(zip(keys, partition))
        yield sdiskpart(**result_dict)


def get_disk():
    """Gathers disk information using the 'psutil' library."""
    dry_run = os.environ.get("DRY_RUN", "false") == "true"
    if dry_run:
        partitions = load_partitions(filename=os.environ.get("PARTITIONS", "partitions.json"))
    else:
        partitions = psutil.disk_partitions()
    system_mountpoints = [
        '/sys', '/proc', '/dev', '/run', '/boot', '/tmp', '/var', '/snap',
        '/sys/kernel', '/sys/fs', '/var/lib/docker', '/dev/loop', '/run/user', '/run/snapd'
    ]
    system_fstypes = [
        'sysfs', 'proc', 'devtmpfs', 'tmpfs', 'devpts', 'fusectl', 'securityfs',
        'overlay', 'hugetlbfs', 'debugfs', 'cgroup2', 'configfs', 'bpf', 'binfmt_misc',
        'efivarfs', 'fuse', 'nsfs', 'squashfs', 'autofs', 'tracefs', 'pstore'
    ]
    # Filter out system partitions
    filtered_partitions = [
        part for part in partitions
        if not any(part.mountpoint.startswith(mnt) for mnt in system_mountpoints)
           and part.fstype not in system_fstypes
    ]
    # todo: Add results to the final output attributes and info as model
    for partition in filtered_partitions:
        print(partition.mountpoint)
        print(psutil.disk_usage(partition.mountpoint))


def load_dump(filename: str) -> str:
    """Loads a dump file for testing purposes.

    Args:
        filename: Dump file to load.

    Returns:
        str:
        Content of the dump file.
    """
    with open(filename) as file:
        return file.read()


def disk_info(disk_lib: FilePath) -> Generator[Disk]:
    """Gathers disk information using the dump from 'udisksctl' command.

    Args:
        disk_lib: Path to the 'udisksctl' command.

    Yields:
        Disk:
        Data structure parsed as a Disk object.
    """
    dry_run = os.environ.get("DRY_RUN", "false") == "true"
    if dry_run:
        text = load_dump(filename=os.environ.get("DUMP", "dump.txt"))
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
                assert (
                    str(error) == "not enough values to unpack (expected 2, got 1)"
                ), error
                continue
            formatted[head][category][key] = val
    for key, value in formatted.items():
        yield Disk(id=key, model=value.get("Info", {}).get("Model", ""), **value)


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
    if message:
        notification_service(
            title="Disk Monitor Alert!!", message=message, env_config=env
        )


def generate_html(
    data: List[Dict[str, str | int | float | bool]], filepath: NewPath
) -> str:
    """Generates an HTML report using Jinja2 template.

    Args:
        data: Data to render in the template.
        filepath: Path to save the HTML report locally.

    Returns:
        str:
        Rendered HTML report.
    """
    template_dir = pathlib.Path(__file__).parent
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_dir)
    )  # Adjust path as needed
    template = env.get_template("template.html")
    html_output = template.render(data=data)
    with open(filepath, "w") as file:
        file.write(html_output)
        file.flush()
    return html_output


def monitor(**kwargs) -> None:
    """Entrypoint for the disk monitoring service.

    Args:
        **kwargs: Arbitrary keyword arguments.
    """
    # todo:
    #   use pyrpoject.toml and click to onboard a CLI tool -> upload to pypi
    env = EnvConfig(**kwargs)
    disk_report = [disk.model_dump() for disk in monitor_disk(env)]
    if disk_report:
        LOGGER.info(
            "Disk monitor reporthas been generated for %d disks", len(disk_report)
        )
        if env.disk_report:
            if env.gmail_user and env.gmail_pass and env.recipient:
                LOGGER.info("Sending an email disk report to %s", env.recipient)
                os.makedirs(env.report_dir, exist_ok=True)
                report_file = datetime.now().strftime(
                    os.path.join(env.report_dir, "disk_report_%m-%d-%Y.html")
                )
                send_report(
                    title=f"Disk Report - {datetime.now().strftime('%c')}",
                    user=env.gmail_user,
                    password=env.gmail_pass,
                    recipient=env.recipient,
                    content=generate_html(disk_report, report_file),
                )
            else:
                LOGGER.warning(
                    "Reporting feature was enabled but necessary notification vars not found!!"
                )
        else:
            LOGGER.info("Reporting feature has been disabled!")
    else:
        LOGGER.warning("Disk monitor report was not generated!")
