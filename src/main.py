import logging
import os
import subprocess
from collections.abc import Generator

from pydantic import FilePath

from .config import EnvConfig
from .models import Disk

LOGGER = logging.getLogger(__name__)
HANDLER = logging.StreamHandler()
FORMATTER = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
HANDLER.setFormatter(FORMATTER)
LOGGER.addHandler(HANDLER)
LOGGER.setLevel(logging.INFO)


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
        Datastructure parsed as a Disk object.
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
                assert (
                    str(error) == "not enough values to unpack (expected 2, got 1)"
                ), error
                continue
            formatted[head][category][key] = val
    for key, value in formatted.items():
        yield Disk(id=key, model="", **value)


def monitor(**kwargs):
    # todo:
    # setup notification as per env vars
    # use psutil to get utilization, partitions, mount points, and model info
    env = EnvConfig(**kwargs)
    for disk in disk_info(env.disk_lib):
        for metric in env.metrics:
            attribute = disk.Attributes.model_dump().get(metric.attribute)
            if metric.max_threshold and attribute >= metric.max_threshold:
                LOGGER.critical(f"{metric.attribute!r} for {disk.id!r} is >= {metric.max_threshold} at {attribute}")
            if metric.min_threshold and attribute <= metric.min_threshold:
                LOGGER.critical(f"{metric.attribute!r} for {disk.id!r} is <= {metric.min_threshold} at {attribute}")
            if metric.equal_match and attribute != metric.equal_match:
                LOGGER.critical(f"{metric.attribute!r} for {disk.id!r} IS NOT {metric.equal_match} at {attribute}")
