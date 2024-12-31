from typing import List, Optional

from pydantic import BaseModel

from . import Usage


class Message(BaseModel):
    """Log message with severity level.

    >>> Message

    """

    string: Optional[str] = None
    severity: Optional[str] = None


class SmartStatusNvme(BaseModel):
    """NVMe status information.

    >>> SmartStatusNvme

    """

    value: Optional[int] = None


class SmartStatus(BaseModel):
    """SMART status for the disk.

    >>> SmartStatus

    """

    passed: Optional[bool] = None
    nvme: Optional[SmartStatusNvme] = None


class NvmeVersion(BaseModel):
    """NVMe version information.

    >>> NvmeVersion

    """

    string: Optional[str] = None
    value: Optional[int] = None


class NvmePciVendor(BaseModel):
    """NVMe PCI vendor details.

    >>> NvmePciVendor

    """

    id: Optional[int] = None
    subsystem_id: Optional[int] = None


class SmartSupport(BaseModel):
    """SMART support availability and status.

    >>> SmartSupport

    """

    available: Optional[bool] = None
    enabled: Optional[bool] = None


class NvmeSmartHealthInformationLog(BaseModel):
    """SMART health log for NVMe disk.

    >>> NvmeSmartHealthInformationLog

    """

    critical_warning: Optional[int] = None
    temperature: Optional[int] = None
    available_spare: Optional[int] = None
    available_spare_threshold: Optional[int] = None
    percentage_used: Optional[int] = None
    data_units_read: Optional[int] = None
    data_units_written: Optional[int] = None
    host_reads: Optional[int] = None
    host_writes: Optional[int] = None
    controller_busy_time: Optional[int] = None
    power_cycles: Optional[int] = None
    power_on_hours: Optional[int] = None
    unsafe_shutdowns: Optional[int] = None
    media_errors: Optional[int] = None
    num_err_log_entries: Optional[int] = None


class Device(BaseModel):
    """Disk device information.

    >>> Device

    """

    name: Optional[str] = None
    info_name: Optional[str] = None
    type: Optional[str] = None
    protocol: Optional[str] = None


class LocalTime(BaseModel):
    """Local system time information.

    >>> LocalTime

    """

    time_t: Optional[int] = None
    asctime: Optional[str] = None


class SmartCTL(BaseModel):
    """SMART control tool execution details.

    >>> SmartCTL

    """

    version: Optional[List[int]] = None
    pre_release: Optional[bool] = None
    svn_revision: Optional[str] = None
    platform_info: Optional[str] = None
    build_info: Optional[str] = None
    argv: Optional[List[str]] = None
    messages: Optional[List[Message]] = None
    exit_status: Optional[int] = None


class Temperature(BaseModel):
    """Temperature reading for the disk.

    >>> Temperature

    """

    current: Optional[int] = None


class PowerOnTime(BaseModel):
    """Disk power-on time in hours.

    >>> PowerOnTime

    """

    hours: Optional[int] = None


class Disk(BaseModel):
    """Collective disk information.

    >>> Disk

    """

    json_format_version: Optional[List[int]] = None
    smartctl: Optional[SmartCTL] = None
    local_time: Optional[LocalTime] = None
    device: Optional[Device] = None
    model_name: Optional[str] = None
    serial_number: Optional[str] = None
    firmware_version: Optional[str] = None
    nvme_pci_vendor: Optional[NvmePciVendor] = None
    nvme_ieee_oui_identifier: Optional[int] = None
    nvme_controller_id: Optional[int] = None
    nvme_version: Optional[NvmeVersion] = None
    nvme_number_of_namespaces: Optional[int] = None
    smart_support: Optional[SmartSupport] = None
    smart_status: Optional[SmartStatus] = None
    nvme_smart_health_information_log: Optional[NvmeSmartHealthInformationLog] = None
    temperature: Optional[Temperature] = None
    power_cycle_count: Optional[int] = None
    power_on_time: Optional[PowerOnTime] = None
    usage: Optional[Usage] = None

    class Config:
        """Configuration for the model."""

        protected_namespaces = ()
