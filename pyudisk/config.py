import os
import platform
from typing import Any, List, Optional

from pyarchitecture.config import default_disk_lib
from pydantic import BaseModel, DirectoryPath, Field, FilePath, HttpUrl, field_validator
from pydantic_settings import BaseSettings

from .models import linux

OPERATING_SYSTEM = platform.system()

try:
    from enum import StrEnum
except ImportError:
    from enum import Enum

    class StrEnum(str, Enum):
        """Custom StrEnum object for python3.10."""


class OperationSystem(StrEnum):
    """Enum for operating system.

    >>> OperationSystem

    """

    darwin: str = "Darwin"
    linux: str = "Linux"


class Metric(BaseModel):
    """Metric configuration passed as env var.

    >>> Metric

    """

    attribute: Optional[str] = None
    min_threshold: int | float | None = None
    max_threshold: int | float | None = None
    equal_match: Optional[Any] = None

    # noinspection PyMethodParameters
    @field_validator("equal_match", mode="before")
    def parse_match(cls, value: Any) -> float | int | bool | str:
        """Tries to parse the match value into different data types."""
        try:
            if "." in str(value):
                return float(value)
            return int(value)
        except ValueError:
            pass
        if value.lower() == "true":
            return True
        if value.lower() == "false":
            return False
        return value


def get_smart_lib() -> FilePath:
    """Returns filepath to the smart library as per the operating system."""
    if OPERATING_SYSTEM == OperationSystem.darwin:
        smartctl1 = "/usr/local/bin/smartctl"
        smartctl2 = "/opt/homebrew/bin/smartctl"
        if os.path.isfile(smartctl1):
            return FilePath(smartctl1)
        if os.path.isfile(smartctl2):
            return FilePath(smartctl2)
        raise ValueError(
            "\n\tsmartctl not found!!\n\tPlease install using `brew install smartmontools`\n"
        )
    if OPERATING_SYSTEM == OperationSystem.linux:
        udiskctl = "/usr/bin/udisksctl"
        if os.path.isfile(udiskctl):
            return FilePath(udiskctl)
        raise ValueError(
            "\n\tudisksctl not found!!\n\tPlease install using `sudo apt install udisks2`\n"
        )
    raise ValueError(f"Unsupported OS: {OPERATING_SYSTEM}")


def get_disk_lib() -> str:
    """Get OS specific disk library to retreive the physical disk ID."""
    return default_disk_lib()[OPERATING_SYSTEM.lower()]


class EnvConfig(BaseSettings):
    """Environment variables configuration.

    >>> EnvConfig

    """

    dry_run: bool = False
    sample_partitions: str = "partitions.json"
    sample_dump: str = "dump.txt"

    smart_lib: FilePath = get_smart_lib()
    disk_lib: FilePath = get_disk_lib()
    metrics: Metric | List[Metric] = Field(default_factory=list)

    # Email/SMS notifications
    gmail_user: Optional[str] = None
    gmail_pass: Optional[str] = None
    recipient: Optional[str] = None
    phone: Optional[str] = None

    # Ntfy notifications
    ntfy_url: HttpUrl | None = None
    ntfy_topic: Optional[str] = None
    ntfy_username: Optional[str] = None
    ntfy_password: Optional[str] = None

    # Telegram notifications
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: int | None = None
    telegram_thread_id: int | None = None

    disk_report: bool = True
    report_dir: str | DirectoryPath = "report"
    report_file: str = Field("disk_report_%m-%d-%Y_%I:%M_%p.html", pattern=r".*\.html$")

    # noinspection PyMethodParameters
    @field_validator("smart_lib", mode="before")
    def validate_udisk_lib(cls, value: str) -> str:
        """Validates the disk library path only when DRY_RUN is set to false."""
        if os.environ.get("DRY_RUN", "false") == "true":
            return __file__
        return value

    # noinspection PyMethodParameters
    @field_validator("metrics", mode="after")
    def validate_metrics(cls, value: Metric | List[Metric]) -> List[Metric]:
        """Validates the metrics configuration."""
        if not isinstance(value, list):
            value = [value]
        attributes = {
            name: [
                dtype.get("type")
                for dtype in dtypes.get("anyOf")
                if dtype.get("type", "") != "null"
            ]
            for name, dtypes in linux.Attributes.model_json_schema()
            .get("properties")
            .items()
        }
        attr_format = "\n\t- ".join(attributes.keys()) + "\n"
        # pydantic datatype mapping for schema validation
        # from pydantic.json_schema import GenerateJsonSchema
        # print(GenerateJsonSchema().literal_schema())
        datatypes = {
            str: "string",
            int: "integer",
            float: "number",
            bool: "boolean",
            list: "array",
        }
        for v in value:
            assert attributes.get(
                v.attribute
            ), f"\n\tattribute should be any one of the following\n\n\t- {attr_format}\n"
            if not any((v.equal_match, v.min_threshold, v.max_threshold)):
                raise ValueError(
                    "At least one of (condition, min_threshold, max_threshold) is mandatory!!"
                )
            types = attributes[v.attribute]
            if "number" in types or "integer" in types:
                types = ["number", "integer"]
            if v.equal_match:
                # Validate the equal match value
                # The input for the equal match should be of the same type as the attribute
                assert (
                    datatypes.get(type(v.equal_match)) in types
                ), f"\n\tequal_match '{v.equal_match}' should be of type {', '.join(types)}\n"
            if v.min_threshold:
                assert types == [
                    "number",
                    "integer",
                ], f"\nAttribute {v.attribute!r} is NOT a number/integer to set min_threshold\n"
                assert type(v.min_threshold) in (
                    int,
                    float,
                ), f"\n\tmin_threshold '{v.min_threshold}' should be of type 'number'\n"
            if v.max_threshold:
                assert types == [
                    "number",
                    "integer",
                ], f"\nAttribute {v.attribute!r} is NOT a number/integer to set max_threshold\n"
                assert type(v.max_threshold) in (
                    int,
                    float,
                ), f"\n\tmax_threshold '{v.max_threshold}' should be of type 'number'\n"
        return value

    class Config:
        """Pydantic model configuration."""

        env_file = os.environ.get("env_file") or os.environ.get("ENV_FILE") or ".env"
        extra = "ignore"
