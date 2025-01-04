import os
import pathlib
from collections.abc import Generator
from datetime import datetime
from typing import Dict, List, NoReturn

from pydantic import NewPath, ValidationError

from . import config, disk_data, metrics, models, notification, parsers, util
from .logger import LOGGER


def smart_metrics(**kwargs) -> Generator[models.udisk.Disk | models.smartctl.Disk]:
    """Gathers smart metrics using udisksctl dump, and constructs a Disk object.

    Yields:
        Disk:
        Yields the Disk object from the generated Dataframe.
    """
    config.env = config.EnvConfig(**kwargs)
    if config.OPERATING_SYSTEM in (
        config.OperationSystem.darwin,
        config.OperationSystem.windows,
    ):
        for device_info in disk_data.get_disk_data(
            config.OPERATING_SYSTEM != config.OperationSystem.windows
        ):
            if retrieved_metrics := metrics.get_smart_metrics(device_info):
                try:
                    yield models.smartctl.Disk(**retrieved_metrics)
                except ValidationError as error:
                    LOGGER.error(error.errors())
        return
    smart_dump = metrics.get_udisk_metrics()
    block_devices = parsers.parse_block_devices(smart_dump)
    drives = {k: v for k, v in sorted(parsers.parse_drives(smart_dump).items())}
    diff = set()
    # Enable mount warning by default (log warning messages if disk is not mounted)
    mount_warning = os.environ.get("MOUNT_WARNING", "1") == "1"
    # A drive can have multiple partitions, but any mounted drive should have at least one partition
    if len(block_devices) < len(drives):
        LOGGER.debug(
            f"Number of block devices [{len(block_devices)}] is less than the number of drives [{len(drives)}]"
        )
        device_names = set(sorted(block_devices.keys()))
        drive_names = set(sorted(drives.keys()))
        if len(drive_names) > len(device_names):
            diff = drive_names - device_names
        else:
            diff = device_names - drive_names
        if diff and mount_warning:
            LOGGER.warning("UNmounted drive(s) found - '%s'", ", ".join(diff))
    optional_fields = [
        k
        for k, v in models.udisk.Disk.model_json_schema().get("properties").items()
        if v.get("anyOf", [{}])[-1].get("type", "") == "null"
    ]
    # UDisk metrics can be null, but the keys are mandatory
    for drive in drives.values():
        for key in optional_fields:
            if key not in drive.keys():
                drive[key] = None
    for drive, data in drives.items():
        if block_data := block_devices.get(drive):
            data["Partition"] = block_data
            yield models.udisk.Disk(
                id=drive, model=data.get("Info", {}).get("Model", ""), **data
            )
        elif drive not in diff:
            # Check if this issue has been caught in unmounted warnings already - if so, skip the warning
            LOGGER.warning(f"{drive} not found in {block_devices.keys()}")


def generate_html(
    data: List[Dict[str, str | int | float | bool]], filepath: NewPath = None
) -> str | NoReturn:
    """Generates an HTML report using Jinja2 template.

    Args:
        data: Data to render in the template.
        filepath: Path to save the HTML report locally.

    Returns:
        str:
        Rendered HTML report.
    """
    try:
        import jinja2
    except ModuleNotFoundError:
        util.standard()

    template_dir = os.path.join(pathlib.Path(__file__).parent, "templates")
    jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))
    template = jinja_env.get_template(f"{config.OPERATING_SYSTEM}.html")
    now = datetime.now()
    html_output = template.render(
        data=data, last_updated=f"{now.strftime('%c')} {now.astimezone().tzinfo}"
    )
    if filepath:
        with open(filepath, "w") as file:
            file.write(html_output)
            file.flush()
    return html_output


def generate_report(**kwargs) -> str:
    """Generates the HTML report using UDisk lib.

    Args:
        **kwargs: Arbitrary keyword arguments.

    Returns:
        str:
        Returns the report filepath.
    """
    config.env = config.EnvConfig(**kwargs)
    if kwargs.get("raw"):
        return generate_html([disk.model_dump() for disk in smart_metrics()])
    if report_file := kwargs.get("filepath"):
        assert report_file.endswith(
            ".html"
        ), "\n\tReport filename should have the suffix '.html'"
        report_dir = str(pathlib.Path(report_file).parent)
        os.makedirs(report_dir, exist_ok=True)
    else:
        if directory := kwargs.get("directory"):
            config.env.report_dir = directory
        os.makedirs(config.env.report_dir, exist_ok=True)
        report_file = datetime.now().strftime(
            os.path.join(config.env.report_dir, config.env.report_file)
        )
    LOGGER.info("Generating disk report")
    disk_report = [disk.model_dump() for disk in smart_metrics()]
    generate_html(disk_report, report_file)
    LOGGER.info("Report has been stored in %s", report_file)
    return report_file


def monitor_disk(**kwargs) -> Generator[models.udisk.Disk]:
    """Monitors disk attributes based on the configuration.

    Yields:
        Disk:
        Data structure parsed as a Disk object.
    """
    assert (
        config.OPERATING_SYSTEM == config.OperationSystem.linux
    ), "Monitoring feature is available only for Linux machines!!"
    config.env = config.EnvConfig(**kwargs)
    message = ""
    for disk in smart_metrics():
        if disk.Attributes:
            for metric in config.env.metrics:
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
        else:
            LOGGER.warning("No attributes were loaded for %s", disk.model)
        yield disk
    if message:
        notification.notification_service(title="Disk Monitor Alert!!", message=message)


def monitor(**kwargs) -> None:
    """Entrypoint for the disk monitoring service.

    Args:
        **kwargs: Arbitrary keyword arguments.
    """
    assert (
        config.OPERATING_SYSTEM == config.OperationSystem.linux
    ), "Monitoring feature is available only for Linux machines!!"
    config.env = config.EnvConfig(**kwargs)
    disk_report = [disk.model_dump() for disk in monitor_disk()]
    if disk_report:
        LOGGER.info(
            "Disk monitor report has been generated for %d disks", len(disk_report)
        )
        if config.env.disk_report:
            os.makedirs(config.env.report_dir, exist_ok=True)
            report_file = datetime.now().strftime(
                os.path.join(config.env.report_dir, config.env.report_file)
            )
            report_data = generate_html(disk_report, report_file)
            if config.env.gmail_user and config.env.gmail_pass and config.env.recipient:
                LOGGER.info("Sending an email disk report to %s", config.env.recipient)
                notification.send_report(
                    title=f"Disk Report - {datetime.now().strftime('%c')}",
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
