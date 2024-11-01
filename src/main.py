import subprocess
from collections.abc import Generator

from .models import Disk, Attributes
from .config import EnvConfig


def disk_info() -> Generator[Disk]:
    """Gathers disk information using the dump from 'udisksctl' command.

    Yields:
        Disk:
        Datastructure parsed as a Disk object.
    """
    output = subprocess.check_output("udisksctl dump", shell=True)
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
                ), ValueError(error)
                val = None
            formatted[head][category][key] = val
    for key, value in formatted.items():
        yield Disk(id=key, **value)


def monitor(**kwargs):
    # todo:
    # include usage for condition
    # setup notification as per env vars
    # use psutil to get utilization and partitions
    env = EnvConfig(**kwargs)
    for disk in disk_info():
        for metric in env.metrics:
            attribute = disk.Attributes.model_dump().get(metric.attribute)
            if metric.max_threshold and attribute >= metric.max_threshold:
                print(f"{metric.attribute} for {disk.id} is >= {metric.max_threshold}")
            if metric.min_threshold and attribute <= metric.min_threshold:
                print(f"{metric.attribute} for {disk.id} is <= {metric.min_threshold}")
