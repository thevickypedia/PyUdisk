import json
import subprocess
from typing import Any, Dict, List

from . import config, models
from .logger import LOGGER


def get_smart_metrics(device_info: Dict[str, str | List[str]]) -> Dict[str, Any]:
    """Gathers disk information using the 'smartctl' command.

    Args:
        device_info: Device information retrieved.

    Returns:
        Dict[str, Any]:
        Returns the SMART metrics as key-value pairs.
    """
    device_id = device_info.get("node") or device_info.get("device_id")
    mountpoints = device_info["mountpoints"]
    try:
        result = subprocess.run(
            [config.env.smart_lib, "-a", device_id, "--json"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            LOGGER.debug(
                "smartctl returned non-zero exit code %d for %s",
                result.returncode,
                device_id,
            )
        output = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        LOGGER.error("Failed to decode JSON output from smartctl: %s", error)
        output = {}
    except subprocess.CalledProcessError as error:
        result = error.output.decode(encoding="UTF-8").strip()
        LOGGER.error("[%d]: %s", error.returncode, result)
        output = {}
    output["device"] = output.get(
        "device",
        models.smartctl.Device(name=device_id, info_name=device_id).model_dump(),
    )
    output["model_name"] = output.get("model_name", device_info.get("name"))
    output["mountpoints"] = mountpoints
    return output


def get_udisk_metrics() -> str:
    """Gathers disk information using the dump from 'udisksctl' command.

    Returns:
        str:
        Returns the output from disk util dump.
    """
    try:
        output = subprocess.check_output(f"{config.env.smart_lib} dump", shell=True)
    except subprocess.CalledProcessError as error:
        result = error.output.decode(encoding="UTF-8").strip()
        LOGGER.error(f"[{error.returncode}]: {result}\n")
        return ""
    return output.decode(encoding="UTF-8")
