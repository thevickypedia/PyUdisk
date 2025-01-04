from typing import Any, Dict, List

from . import disk_data, models


def parse_drives(input_data: str) -> Dict[str, Any]:
    """Parses drivers' information from the dump into a datastructure.

    Args:
        input_data: Smart metrics dump.

    Returns:
        Dict[str, Any]:
        Returns a dictionary of drives' metrics as key-value pairs.
    """
    formatted = {}
    head = None
    category = None
    for line in input_data.splitlines():
        if line.startswith(models.udisk.Drives.head):
            head = line.replace(models.udisk.Drives.head, "").rstrip(":").strip()
            formatted[head] = {}
        elif line.strip() in (
            models.udisk.Drives.category1,
            models.udisk.Drives.category2,
        ):
            category = (
                line.replace(models.udisk.Drives.category1, "Info")
                .replace(models.udisk.Drives.category2, "Attributes")
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


def parse_block_devices(input_data: str) -> Dict[str, List[Dict[str, str]]]:
    """Parses block_devices' information from the dump into a datastructure.

    Args:
        input_data: Smart metrics dump.

    Returns:
        Dict[str, List[Dict[str, str]]]:
        Returns a dictionary of block_devices' metrics as key-value pairs.
    """
    block_devices = {}
    block = None
    category = None
    block_partitions = [
        f"{models.udisk.BlockDevices.head}{block_device.device.split('/')[-1]}:"
        for block_device in disk_data.get_partitions()
    ]
    for line in input_data.splitlines():
        if line in block_partitions:
            # Assigning a placeholder value to avoid skipping loop when 'block' has a value
            # This should be a unique value for each partition
            # block = str(time.time_ns()) - another alternative
            block = line
            block_devices[block] = {}
        elif block and line.strip() in (
            models.udisk.BlockDevices.category1,
            models.udisk.BlockDevices.category2,
            models.udisk.BlockDevices.category3,
        ):
            category = (
                line.replace(models.udisk.BlockDevices.category1, "Block")
                .replace(models.udisk.BlockDevices.category2, "Filesystem")
                .replace(models.udisk.BlockDevices.category3, "Partition")
                .strip()
            )
        elif block and category:
            try:
                key, val = line.strip().split(":", 1)
                key = key.strip()
                val = val.strip()
                if key == "Drive":
                    val = eval(val).replace(models.udisk.Drives.head, "")
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
    block_devices_updated = {}
    for _, value in block_devices.items():
        if block_devices_updated.get(value["Drive"]):
            block_devices_updated[value["Drive"]].append(value)
        else:
            block_devices_updated[value["Drive"]] = [value]
    return block_devices_updated
