import json
from typing import Optional

from pydantic import BaseModel, field_validator


class Info(BaseModel):
    """Information about the disk.

    >>> Info

    """

    CanPowerOff: Optional[bool]
    Configuration: Optional[dict]
    ConnectionBus: Optional[str]
    Ejectable: Optional[bool]
    Id: Optional[str]
    Media: Optional[str]
    MediaAvailable: Optional[bool]
    MediaChangeDetected: Optional[bool]
    MediaCompatibility: Optional[str]
    MediaRemovable: Optional[bool]
    Model: Optional[str]
    Optical: Optional[bool]
    OpticalBlank: Optional[bool]
    OpticalNumAudioTracks: Optional[int]
    OpticalNumDataTracks: Optional[int]
    OpticalNumSessions: Optional[int]
    OpticalNumTracks: Optional[int]
    Removable: Optional[bool]
    Revision: Optional[str]
    RotationRate: Optional[int]
    Seat: Optional[str]
    Serial: Optional[str]
    SiblingId: Optional[str]
    Size: Optional[int]
    SortKey: Optional[str]
    TimeDetected: Optional[int]
    TimeMediaDetected: Optional[int]
    Vendor: Optional[str]
    WWN: Optional[str]

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

    AamEnabled: Optional[bool]
    AamSupported: Optional[bool]
    AamVendorRecommendedValue: Optional[int]
    ApmEnabled: Optional[bool]
    ApmSupported: Optional[bool]
    PmEnabled: Optional[bool]
    PmSupported: Optional[bool]
    ReadLookaheadEnabled: Optional[bool]
    ReadLookaheadSupported: Optional[bool]
    SecurityEnhancedEraseUnitMinutes: Optional[int]
    SecurityEraseUnitMinutes: Optional[int]
    SecurityFrozen: Optional[bool]
    SmartEnabled: Optional[bool]
    SmartFailing: Optional[bool]
    SmartNumAttributesFailedInThePast: Optional[int]
    SmartNumAttributesFailing: Optional[int]
    SmartNumBadSectors: Optional[int]
    SmartPowerOnSeconds: Optional[int]
    SmartSelftestPercentRemaining: Optional[int]
    SmartSelftestStatus: Optional[str]
    SmartSupported: Optional[bool]
    SmartTemperature: Optional[float]
    SmartUpdated: Optional[int]
    WriteCacheEnabled: Optional[bool]
    WriteCacheSupported: Optional[bool]


class Disk(BaseModel):
    """Collective disk information.

    >>> Disk

    """

    id: str
    model: str
    Info: Info
    Attributes: Attributes
