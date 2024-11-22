import json
from collections.abc import Generator
from typing import Dict

from psutil._common import sdiskpart, sdiskusage

from .util import format_nos, size_converter


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


def humanize_usage_metrics(usage: sdiskusage) -> Dict[str, str]:
    """Convert the usage metrics into human readable format."""
    return {
        "Total": size_converter(usage.total),
        "Used": size_converter(usage.used),
        "Free": size_converter(usage.free),
        "Percent": format_nos(usage.percent),
    }
