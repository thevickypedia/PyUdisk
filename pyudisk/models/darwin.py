from typing import List, Optional

from pydantic import BaseModel

from . import Usage


class Message(BaseModel):
    """Log message with severity level.

    >>> Message

    """

    string: Optional[str]
    severity: Optional[str]


class SmartStatusNvme(BaseModel):
    """NVMe status information.

    >>> SmartStatusNvme

    """

    value: Optional[int]


class SmartStatus(BaseModel):
    """SMART status for the disk.

    >>> SmartStatus

    """

    passed: Optional[bool]
    nvme: Optional[SmartStatusNvme]


class NvmeVersion(BaseModel):
    """NVMe version information.

    >>> NvmeVersion

    """

    string: Optional[str]
    value: Optional[int]


class NvmePciVendor(BaseModel):
    """NVMe PCI vendor details.

    >>> NvmePciVendor

    """

    id: Optional[int]
    subsystem_id: Optional[int]


class SmartSupport(BaseModel):
    """SMART support availability and status.

    >>> SmartSupport

    """

    available: Optional[bool]
    enabled: Optional[bool]


class NvmeSmartHealthInformationLog(BaseModel):
    """SMART health log for NVMe disk.

    >>> NvmeSmartHealthInformationLog

    """

    critical_warning: Optional[int]
    temperature: Optional[int]
    available_spare: Optional[int]
    available_spare_threshold: Optional[int]
    percentage_used: Optional[int]
    data_units_read: Optional[int]
    data_units_written: Optional[int]
    host_reads: Optional[int]
    host_writes: Optional[int]
    controller_busy_time: Optional[int]
    power_cycles: Optional[int]
    power_on_hours: Optional[int]
    unsafe_shutdowns: Optional[int]
    media_errors: Optional[int]
    num_err_log_entries: Optional[int]


class Device(BaseModel):
    """Disk device information.

    >>> Device

    """

    name: Optional[str]
    info_name: Optional[str]
    type: Optional[str]
    protocol: Optional[str]


class LocalTime(BaseModel):
    """Local system time information.

    >>> LocalTime

    """

    time_t: Optional[int]
    asctime: Optional[str]


class SmartCTL(BaseModel):
    """SMART control tool execution details.

    >>> SmartCTL

    """

    version: Optional[List[int]]
    pre_release: Optional[bool]
    svn_revision: Optional[str]
    platform_info: Optional[str]
    build_info: Optional[str]
    argv: Optional[List[str]]
    messages: Optional[List[Message]]
    exit_status: Optional[int]


class Temperature(BaseModel):
    """Temperature reading for the disk.

    >>> Temperature

    """

    current: Optional[int]


class PowerOnTime(BaseModel):
    """Disk power-on time in hours.

    >>> PowerOnTime

    """

    hours: Optional[int]


class Disk(BaseModel):
    """Collective disk information.

    >>> Disk

    """

    json_format_version: Optional[List[int]]
    smartctl: Optional[SmartCTL]
    local_time: Optional[LocalTime]
    device: Optional[Device]
    model_name: Optional[str]
    serial_number: Optional[str]
    firmware_version: Optional[str]
    nvme_pci_vendor: Optional[NvmePciVendor]
    nvme_ieee_oui_identifier: Optional[int]
    nvme_controller_id: Optional[int]
    nvme_version: Optional[NvmeVersion]
    nvme_number_of_namespaces: Optional[int]
    smart_support: Optional[SmartSupport]
    smart_status: Optional[SmartStatus]
    nvme_smart_health_information_log: Optional[NvmeSmartHealthInformationLog]
    temperature: Optional[Temperature]
    power_cycle_count: Optional[int]
    power_on_time: Optional[PowerOnTime]
    usage: Optional[Usage]

    class Config:
        """Configuration for the model."""

        protected_namespaces = ()
