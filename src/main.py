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
from .models import BlockDevices, Disk, Drives, Partitions
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
        partitions = load_partitions(
            filename=os.environ.get("PARTITIONS", "partitions.json")
        )
    else:
        partitions = psutil.disk_partitions()
    # Filter out system partitions
    for partition in partitions:
        if (
            not any(
                partition.mountpoint.startswith(mnt)
                for mnt in Partitions.system_mountpoints
            )
            and partition.fstype not in Partitions.system_fstypes
        ):
            yield partition


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


def get_smart_metrics(disk_lib: FilePath) -> str:
    """Gathers disk information using the dump from 'udisksctl' command.

    Args:
        disk_lib: Path to the 'udisksctl' command.

    Returns:
        str:
        Returns the output from disk util dump.
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
    return text


def parse_drives(input_data: str) -> Dict[str, str]:
    """Parses drivers' information from the dump into a datastructure.

    Args:
        input_data: Smart metrics dump.

    Returns:
        Dict[str, str]:
        Returns a dictionary of drives' metrics as key-value pairs.
    """
    formatted = {}
    head = None
    category = None
    for line in input_data.splitlines():
        if line.startswith(Drives.head):
            head = line.replace(Drives.head, "").rstrip(":").strip()
            formatted[head] = {}
        elif line.strip() in (Drives.category1, Drives.category2):
            category = (
                line.replace(Drives.category1, "Info")
                .replace(Drives.category2, "Attributes")
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
    return formatted


def parse_block_devices(input_data: str) -> Dict[str, str]:
    """Parses block_devices' information from the dump into a datastructure.

    Args:
        input_data: Smart metrics dump.

    Returns:
        Dict[str, str]:
        Returns a dictionary of block_devices' metrics as key-value pairs.
    """
    block_devices = {}
    block = None
    category = None
    block_partitions = [
        f"{BlockDevices.head}{block_device.device.split('/')[-1]}:"
        for block_device in get_disk()
    ]
    for line in input_data.splitlines():
        if line in block_partitions:
            block = line.replace(BlockDevices.head, "").rstrip(":").strip()
            block_devices[block] = {}
        elif block and line.strip() in (
            BlockDevices.category1,
            BlockDevices.category2,
            BlockDevices.category3,
        ):
            category = (
                line.replace(BlockDevices.category1, "Block")
                .replace(BlockDevices.category2, "Filesystem")
                .replace(BlockDevices.category3, "Partition")
                .strip()
            )
        elif block and category:
            try:
                key, val = line.strip().split(":", 1)
                key = key.strip()
                val = val.strip()
                if key == "Drive":
                    val = eval(val).replace(Drives.head, "")
                if key == "Symlinks":
                    block_devices[block][key] = [val]
            except ValueError as error:
                if block_devices[block].get("Symlinks") and line.strip():
                    block_devices[block]["Symlinks"].append(line.strip())
                assert (
                    str(error) == "not enough values to unpack (expected 2, got 1)"
                ), error
                continue
            if (
                # This will ensure that new data is not written to old key
                not block_devices[block].get(key)
                # 'org.freedesktop.UDisks2.Partition' records are skipped
                and category in ("Block", "Filesystem")
                # Only store keys that provide value
                and key
                in (
                    "Device",
                    "DeviceNumber",
                    "Drive",
                    "Id",
                    "IdLabel",
                    "IdType",
                    "IdUUID",
                    "IdUsage",
                    "ReadOnly",
                    "Size",
                    "MountPoints",
                )
            ):
                block_devices[block][key] = val
    return block_devices


def smart_metrics(disk_lib: FilePath) -> Generator[Disk]:
    """Gathers smart metrics using udisksctl dump, and constructs a Disk object.

    Args:
        disk_lib: Path to the 'udisksctl' command.

    Yields:
        Disk:
        Yields the Disk object from the generated Dataframe.
    """
    smart_dump = get_smart_metrics(disk_lib)
    block_devices = dict(
        sorted(
            parse_block_devices(smart_dump).items(),
            key=lambda device: device[1]["Drive"],
        )
    )
    drives = {k: v for k, v in sorted(parse_drives(smart_dump).items())}
    assert len(block_devices) == len(drives)
    for (key, value), (_, block_device) in zip(drives.items(), block_devices.items()):
        if key == block_device["Drive"]:
            value["BlockDevice"] = block_device
        else:
            raise ValueError(
                f"\n\n{key} not found in {[bd['Drive'] for bd in block_devices.values()]}"
            )
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
    for disk in smart_metrics(env.disk_lib):
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
    now = datetime.now()
    html_output = template.render(
        data=data, last_updated=f"{now.strftime('%c')} {now.astimezone().tzinfo}"
    )
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
            "Disk monitor report has been generated for %d disks", len(disk_report)
        )
        if env.disk_report:
            os.makedirs(env.report_dir, exist_ok=True)
            report_file = datetime.now().strftime(
                os.path.join(env.report_dir, "disk_report_%m-%d-%Y.html")
            )
            report_data = generate_html(disk_report, report_file)
            if env.gmail_user and env.gmail_pass and env.recipient:
                LOGGER.info("Sending an email disk report to %s", env.recipient)
                send_report(
                    title=f"Disk Report - {datetime.now().strftime('%c')}",
                    user=env.gmail_user,
                    password=env.gmail_pass,
                    recipient=env.recipient,
                    content=report_data,
                )
            else:
                LOGGER.warning(
                    "Reporting feature was enabled but necessary notification vars not found!!"
                )
        else:
            LOGGER.info("Reporting feature has been disabled!")
    else:
        LOGGER.warning("Disk monitor report was not generated!")
