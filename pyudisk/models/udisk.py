import json
from typing import List, Optional

from pydantic import BaseModel, field_validator

try:
    from enum import StrEnum
except ImportError:
    from enum import Enum

    class StrEnum(str, Enum):
        """Custom StrEnum object for python3.10."""


class Drives(StrEnum):
    """Identifiers for drives.

    See Also:
        - https://storaged.org/doc/udisks2-api/latest/gdbus-org.freedesktop.UDisks2.Drive
        - https://storaged.org/doc/udisks2-api/latest/gdbus-org.freedesktop.UDisks2.Drive.Ata
    """

    head: str = "/org/freedesktop/UDisks2/drives/"
    category1: str = "org.freedesktop.UDisks2.Drive:"
    category2: str = "org.freedesktop.UDisks2.Drive.Ata:"


class BlockDevices(StrEnum):
    """Identifiers for block devices.

    See Also:
        - https://storaged.org/doc/udisks2-api/latest/gdbus-org.freedesktop.UDisks2.Block
        - https://storaged.org/doc/udisks2-api/latest/gdbus-org.freedesktop.UDisks2.Filesystem
        - https://storaged.org/doc/udisks2-api/latest/gdbus-org.freedesktop.UDisks2.Partition
    """

    head: str = "/org/freedesktop/UDisks2/block_devices/"
    category1: str = "org.freedesktop.UDisks2.Block:"
    category2: str = "org.freedesktop.UDisks2.Filesystem:"
    category3: str = "org.freedesktop.UDisks2.Partition:"


class Partition(BaseModel):
    """Disk partitions' infomration."""

    Device: Optional[str] = None
    DeviceNumber: Optional[int] = None
    Drive: Optional[str] = None
    Id: Optional[str] = None
    IdLabel: Optional[str] = None
    IdType: Optional[str] = None
    IdUUID: Optional[str] = None
    IdUsage: Optional[str] = None
    ReadOnly: Optional[bool] = None
    Size: Optional[int] = None
    MountPoints: Optional[str] = None
    Symlinks: Optional[List[str]] = None


class Info(BaseModel):
    """Information about the disk.

    >>> Info

    """

    CanPowerOff: Optional[bool] = None
    Configuration: Optional[dict] = None
    ConnectionBus: Optional[str] = None
    Ejectable: Optional[bool] = None
    Id: Optional[str] = None
    Media: Optional[str] = None
    MediaAvailable: Optional[bool] = None
    MediaChangeDetected: Optional[bool] = None
    MediaCompatibility: Optional[str] = None
    MediaRemovable: Optional[bool] = None
    Model: Optional[str] = None
    Optical: Optional[bool] = None
    OpticalBlank: Optional[bool] = None
    OpticalNumAudioTracks: Optional[int] = None
    OpticalNumDataTracks: Optional[int] = None
    OpticalNumSessions: Optional[int] = None
    OpticalNumTracks: Optional[int] = None
    Removable: Optional[bool] = None
    Revision: Optional[str] = None
    RotationRate: Optional[int] = None
    Seat: Optional[str] = None
    Serial: Optional[str] = None
    SiblingId: Optional[str] = None
    Size: Optional[int] = None
    SortKey: Optional[str] = None
    TimeDetected: Optional[int] = None
    TimeMediaDetected: Optional[int] = None
    Vendor: Optional[str] = None
    WWN: Optional[str] = None

    # noinspection PyMethodParameters
    @field_validator("Configuration", mode="before")
    def parse_json_dict(cls, value):
        """Parses a string value into a JSON object."""
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                raise ValueError("'Configuration' must be a valid dict")
        return value


class Attributes(BaseModel):
    """Attributes of the disk to retrieve SMART data.

    >>> Attributes

    """

    AamEnabled: Optional[bool] = None
    AamSupported: Optional[bool] = None
    AamVendorRecommendedValue: Optional[int] = None
    ApmEnabled: Optional[bool] = None
    ApmSupported: Optional[bool] = None
    PmEnabled: Optional[bool] = None
    PmSupported: Optional[bool] = None
    ReadLookaheadEnabled: Optional[bool] = None
    ReadLookaheadSupported: Optional[bool] = None
    SecurityEnhancedEraseUnitMinutes: Optional[int] = None
    SecurityEraseUnitMinutes: Optional[int] = None
    SecurityFrozen: Optional[bool] = None
    SmartEnabled: Optional[bool] = None
    SmartFailing: Optional[bool] = None
    SmartNumAttributesFailedInThePast: Optional[int] = None
    SmartNumAttributesFailing: Optional[int] = None
    SmartNumBadSectors: Optional[int] = None
    SmartPowerOnSeconds: Optional[int] = None
    SmartSelftestPercentRemaining: Optional[int] = None
    SmartSelftestStatus: Optional[str] = None
    SmartSupported: Optional[bool] = None
    SmartTemperature: Optional[float] = None
    SmartUpdated: Optional[int] = None
    WriteCacheEnabled: Optional[bool] = None
    WriteCacheSupported: Optional[bool] = None


class Disk(BaseModel):
    """Collective disk information.

    >>> Disk

    """

    id: str
    model: str
    Info: Optional[Info]
    Attributes: Optional[Attributes]
    Partition: Optional[List[Partition]]
