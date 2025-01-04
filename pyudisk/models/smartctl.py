from typing import List, Optional

from pydantic import BaseModel


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


# Begin ATA based
class WWN(BaseModel):
    """WWN information for the disk.

    >>> WWN

    """

    naa: Optional[int] = None
    oui: Optional[int] = None
    id: Optional[int] = None


class UserCapacity(BaseModel):
    """User capacity information for the disk.

    >>> UserCapacity

    """

    blocks: Optional[int] = None
    bytes: Optional[int] = None


class Trim(BaseModel):
    """TRIM support information for the disk.

    >>> Trim

    """

    supported: Optional[bool] = None
    deterministic: Optional[bool] = None
    zeroed: Optional[bool] = None


class ATAVersion(BaseModel):
    """ATA version information.

    >>> ATAVersion

    """

    string: Optional[str] = None
    major_value: Optional[int] = None
    minor_value: Optional[int] = None


class InterfaceSpeedOptions(BaseModel):
    """Interface speed options for the disk.

    >>> InterfaceSpeedOptions

    """

    sata_value: Optional[int] = None
    string: Optional[str] = None
    units_per_second: Optional[int] = None
    bits_per_unit: Optional[int] = None


class InterfaceSpeed(BaseModel):
    """Interface speed information for the disk.

    >>> InterfaceSpeed

    """

    max: Optional[InterfaceSpeedOptions] = None
    current: Optional[InterfaceSpeedOptions] = None


class GenericStatus(BaseModel):
    """Generic status information.

    >>> GenericStatus

    """

    value: Optional[int | str] = None
    string: Optional[int | str] = None


class STStatus(BaseModel):
    """Self-test status information.

    >>> STStatus

    """

    value: Optional[int] = None
    string: Optional[str] = None
    passed: Optional[bool] = None


class OfflineDataCollection(BaseModel):
    """Offline data collection information.

    >>> OfflineDataCollection

    """

    status: Optional[GenericStatus] = None
    completion_seconds: Optional[int] = None


class PollingMinutes(BaseModel):
    """Polling minutes information.

    >>> PollingMinutes

    """

    short: Optional[int] = None
    extended: Optional[int] = None


class SelfTest(BaseModel):
    """Self-test information.

    >>> SelfTest

    """

    status: Optional[STStatus] = None
    polling_minutes: Optional[PollingMinutes] = None


class Capabilities(BaseModel):
    """Capabilities information.

    >>> Capabilities

    """

    values: List[int] = None
    exec_offline_immediate_supported: Optional[bool] = None
    offline_is_aborted_upon_new_cmd: Optional[bool] = None
    offline_surface_scan_supported: Optional[bool] = None
    self_tests_supported: Optional[bool] = None
    conveyance_self_test_supported: Optional[bool] = None
    selective_self_test_supported: Optional[bool] = None
    attribute_autosave_enabled: Optional[bool] = None
    error_logging_supported: Optional[bool] = None
    gp_logging_supported: Optional[bool] = None


class ATASmartData(BaseModel):
    """ATA SMART data information.

    >>> ATASmartData

    """

    offline_data_collection: Optional[OfflineDataCollection] = None
    self_test: Optional[SelfTest] = None
    capabilities: Optional[Capabilities] = None


class Flags(BaseModel):
    """Flags information.

    >>> Flags

    """

    value: Optional[int] = None
    string: Optional[str] = None
    prefailure: Optional[bool] = None
    updated_online: Optional[bool] = None
    performance: Optional[bool] = None
    error_rate: Optional[bool] = None
    event_count: Optional[bool] = None
    auto_keep: Optional[bool] = None


class ATATable(BaseModel):
    """ATA table information.

    >>> ATATable

    """

    id: Optional[int] = None
    name: Optional[str] = None
    value: Optional[int] = None
    worst: Optional[int] = None
    thresh: Optional[int] = None
    when_failed: Optional[str] = None
    flags: Optional[Flags] = None
    raw: Optional[GenericStatus] = None


class ATASmartAttributes(BaseModel):
    """ATA SMART attributes information.

    >>> ATASmartAttributes

    """

    revision: Optional[int] = None
    table: Optional[List[ATATable]] = None


class ATASmartLog(BaseModel):
    """ATA SMART log information.

    >>> ATASmartLog

    """

    revision: Optional[int] = None
    count: Optional[int] = None


class ATASummary(BaseModel):
    """ATA summary information.

    >>> ATASummary

    """

    summary: Optional[ATASmartLog] = None


class ATAStandard(BaseModel):
    """ATA standard information.

    >>> ATAStandard

    """

    standard: Optional[ATASmartLog] = None


class ATASmartSelectiveSelfTestLogTable(BaseModel):
    """ATA SMART selective self-test log table information.

    >>> ATASmartSelectiveSelfTestLogTable

    """

    lba_min: Optional[int] = None
    lba_max: Optional[int] = None
    status: Optional[GenericStatus] = None


class ATASmartSelectiveSelfTestFlags(BaseModel):
    """ATA SMART selective self-test flags information.

    >>> ATASmartSelectiveSelfTestFlags

    """

    value: Optional[int] = None
    reminder_scan_enabled: Optional[bool] = None


class ATASmartSelectiveSelfTestLog(BaseModel):
    """ATA SMART selective self-test log information.

    >>> ATASmartSelectiveSelfTestLog

    """

    revision: Optional[int] = None
    table: List[ATASmartSelectiveSelfTestLogTable] = None
    current_read_scan: Optional[ATASmartSelectiveSelfTestLogTable] = None
    flags: Optional[ATASmartSelectiveSelfTestFlags] = None
    power_up_scan_resume_minutes: Optional[int] = None


# End ATA based


class Disk(BaseModel):
    """Collective disk information.

    >>> Disk

    """

    json_format_version: Optional[List[int]] = None
    smartctl: Optional[SmartCTL] = None
    local_time: Optional[LocalTime] = None
    device: Optional[Device] = None
    model_family: Optional[str] = None
    model_name: Optional[str] = None
    serial_number: Optional[str] = None
    wwn: Optional[WWN] = None
    firmware_version: Optional[str] = None
    user_capacity: Optional[UserCapacity] = None
    logical_block_size: Optional[int] = None
    physical_block_size: Optional[int] = None
    rotation_rate: Optional[int] = None
    trim: Optional[Trim] = None
    in_smartctl_database: Optional[bool] = None
    ata_version: Optional[ATAVersion] = None
    sata_version: Optional[GenericStatus] = None
    interface_speed: Optional[InterfaceSpeed] = None
    nvme_pci_vendor: Optional[NvmePciVendor] = None
    nvme_ieee_oui_identifier: Optional[int] = None
    nvme_controller_id: Optional[int] = None
    nvme_version: Optional[NvmeVersion] = None
    nvme_number_of_namespaces: Optional[int] = None
    smart_support: Optional[SmartSupport] = None
    smart_status: Optional[SmartStatus] = None
    ata_smart_data: Optional[ATASmartData] = None
    nvme_smart_health_information_log: Optional[NvmeSmartHealthInformationLog] = None
    temperature: Optional[Temperature] = None
    power_cycle_count: Optional[int] = None
    power_on_time: Optional[PowerOnTime] = None
    ata_smart_error_log: Optional[ATASummary] = None
    ata_smart_self_test_log: Optional[ATAStandard] = None
    ata_smart_selective_self_test_log: Optional[ATASmartSelectiveSelfTestLog] = None
    mountpoints: List[str] = None

    class Config:
        """Configuration for the model."""

        protected_namespaces = ()
