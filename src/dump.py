import json
import subprocess
from collections.abc import Generator
from typing import Optional

from pydantic import BaseModel, field_validator


class Info(BaseModel):
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

    @field_validator("Configuration", mode="before")
    def parse_json_dict(cls, value):
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                raise ValueError("'Configuration' must be a valid dict")
        return value


class Attributes(BaseModel):
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
    id: str
    Info: Info
    Attributes: Attributes


def disk_info() -> Generator[Disk]:
    """Gathers disk information using the dump from 'udisksctl' command.

    Yields:
        Disk:
        Datastructure parsed as a Disk object.
    """
    output = subprocess.check_output("udisksctl dump", shell=True)
    text = output.decode(encoding="UTF-8")
    formatted = {}
    head = None
    category = None
    head_check = "/org/freedesktop/UDisks2/drives/"
    cat1_check = "org.freedesktop.UDisks2.Drive:"
    cat2_check = "org.freedesktop.UDisks2.Drive.Ata:"
    for line in text.splitlines():
        if line.startswith(head_check):
            head = line.replace(head_check, "").strip()
            formatted[head] = {}
        elif line.strip() in (cat1_check, cat2_check):
            category = (
                line.replace(cat1_check, "Info")
                .replace(cat2_check, "Attributes")
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
                ), ValueError(error)
                val = None
            formatted[head][category][key] = val
    for key, value in formatted.items():
        yield Disk(id=key, **value)
