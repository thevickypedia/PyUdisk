import os
from typing import List, Optional, Any

from pydantic import BaseModel, field_validator, HttpUrl, FilePath, Field
from pydantic_settings import BaseSettings

from .models import Attributes


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


class EnvConfig(BaseSettings):
    """Environment variables configuration.

    >>> EnvConfig

    """

    disk_lib: FilePath = "/usr/bin/udisksctl"
    metrics: Metric | List[Metric] = []

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
    report_file: str | None = Field(None, pattern=r"^(.*\.html)$")

    # noinspection PyMethodParameters
    @field_validator("disk_lib", mode="before")
    def validate_disk_lib(cls, value: str) -> str:
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
        attributes = Attributes.model_json_schema().get('required')
        attr_format = '\n\t- '.join(attributes) + '\n'
        # pydantic datatype mapping for schema validation
        # from pydantic.json_schema import GenerateJsonSchema
        # print(GenerateJsonSchema().literal_schema())
        datatypes = {
            str: 'string',
            int: 'integer',
            float: 'number',
            bool: 'boolean',
            list: 'array',
        }
        for v in value:
            assert v.attribute in attributes, \
                f"\n\tattribute should be any one of the following\n\n\t- {attr_format}\n"
            if not any((v.equal_match, v.min_threshold, v.max_threshold)):
                raise ValueError(
                    "At least one of (condition, min_threshold, max_threshold) is mandatory!!"
                )
            if v.equal_match:
                # Validate the equal match value
                # The input for the equal match should be of the same type as the attribute
                types = [
                    attr_type.get('type')
                    for attr_type in Attributes.model_json_schema().get('properties').get(v.attribute).get('anyOf')
                    if attr_type.get('type') != 'null'
                ]
                if "number" in types or "integer" in types:
                    types = ["number", "integer"]
                assert datatypes.get(type(v.equal_match)) in types, \
                    f"\n\tequal_match '{v.equal_match}' should be of type {', '.join(types)}\n"
            if v.min_threshold:
                assert type(v.min_threshold) in (int, float), \
                    f"\n\tmin_threshold '{v.min_threshold}' should be of type 'number'\n"
            if v.max_threshold:
                assert type(v.max_threshold) in (int, float), \
                    f"\n\tmax_threshold '{v.max_threshold}' should be of type 'number'\n"
        return value

    class Config:
        """Pydantic model configuration."""

        env_file = os.environ.get("env_file") or os.environ.get("ENV_FILE") or ".env"
