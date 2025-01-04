from collections.abc import Generator
from typing import Dict, List

import psutil
import pyarchitecture
from psutil._common import sdiskpart

from . import config, models, util
from .logger import LOGGER


def get_partitions() -> Generator[sdiskpart]:
    """Gathers disk information using the 'psutil' library.

    Yields:
        sdiskpart:
        Yields the partition datastructure.
    """
    system_partitions = models.SystemPartitions()
    for partition in psutil.disk_partitions():
        is_not_system_mount = all(
            not partition.mountpoint.startswith(mnt)
            for mnt in system_partitions.system_mountpoints
        )
        is_not_system_fstype = partition.fstype not in system_partitions.system_fstypes
        is_not_recovery = "Recovery" not in partition.mountpoint
        if is_not_system_mount and is_not_system_fstype and is_not_recovery:
            yield partition


def get_io_counters() -> Generator[str]:
    """Gathers disk IO counters using the 'psutil' library, which have non-zero write count.

    Yields:
        str:
        Yields the disk id.
    """
    for disk_id, disk_io in psutil.disk_io_counters(perdisk=True).items():
        if min(disk_io.write_bytes, disk_io.write_count, disk_io.write_time) != 0:
            yield disk_id


def get_disk_io() -> Generator[Dict[str, str | List[str]]]:
    """Gathers disk IO counters using the 'psutil' library to construct a disk data.

    Yields:
        Dict[str, str | List[str]]:
        Yields the disk data as key-value pairs.
    """
    if physical_disks := list(get_io_counters()):
        # If there is only one physical disk, then set the mountpoint to root (/)
        if len(physical_disks) == 1:
            yield dict(
                size=util.size_converter(psutil.disk_usage("/").total),
                device_id=physical_disks[0],
                node=f"/dev/{physical_disks[0]}",
                mountpoints=["/"],
            )
        else:
            # If there are multiple physical disks, then set the mountpoint to disk path itself
            for physical_disk in physical_disks:
                yield dict(
                    size=util.size_converter(psutil.disk_usage("/").total),
                    device_id=physical_disk,
                    node=f"/dev/{physical_disk}",
                    mountpoints=[f"/dev/{physical_disk}"],
                )


def partitions() -> Generator[Dict[str, str | List[str]]]:
    """Gathers disk partitions using the 'psutil' library.

    Yields:
        Dict[str, str | List[str]]:
        Yields the disk data as key-value pairs.
    """
    for partition in get_partitions():
        yield dict(
            size=util.size_converter(psutil.disk_usage(partition.mountpoint).total),
            device_id=partition.device.lstrip("/dev/"),
            node=partition.device,
            mountpoints=[partition.device],
        )


def get_disk_data(posix: bool) -> List[Dict[str, str | List[str]]]:
    """Get disk information for macOS and Windows machines.

    Args:
        posix: If the operating system is POSIX compliant.

    Returns:
        List[Dict[str, str | List[str]]]:
        Returns a list of dictionaries with device information as key-value pairs.
    """
    if posix:
        # 1: Attempt to extract physical disks from PyArchitecture
        if pyarch := pyarchitecture.disks.get_all_disks(config.env.disk_lib):
            return pyarch
        # 2: Assume disks with non-zero write count as physical disks
        # disk_io_counters fn will fetch disks rather than partitions (similar to output from 'diskutil list')
        LOGGER.warning("Failed to load physical disk data")
        if disk_io := list(get_disk_io()):
            return disk_io
        # The accuracy of methods 2, and 3 are questionable (for macOS) - it may vary from device to device
        LOGGER.warning(
            "No physical disks found through IO counters, using partitions instead"
        )
    # 3. If both the methods fail, then fallback to disk partitions
    # For Windows, this is the only option since smartctl doesn't work for physical drive name
    # Information is retrieved using the drive letter (C:, D:, etc.)
    return list(partitions())
