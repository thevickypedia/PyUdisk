import os
from typing import List, Optional
from pydantic import BaseModel, field_validator, HttpUrl
from pydantic_settings import BaseSettings

from .models import Attributes


class Metric(BaseModel):
    attribute: Optional[str] = None
    min_threshold: int | float | None = None
    max_threshold: int | float | None = None
    condition: Optional[str] = None


class EnvConfig(BaseSettings):
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
    thread_id: int | None = None

    @field_validator("metrics", mode="after")
    def validate_metrics(cls, value: Metric | List[Metric]):
        if not isinstance(value, list):
            value = [value]
        attributes = Attributes.model_json_schema().get('required')
        attr_format = '\n\t- '.join(attributes) + '\n'
        for v in value:
            assert v.attribute in attributes, \
                f"\n\tattribute should be any one of the following\n\n\t- {attr_format}\n"
            if not any((v.condition, v.min_threshold, v.max_threshold)):
                raise ValueError(
                    "At least one of (condition, min_threshold, max_threshold) is mandatory!!"
                )
        return value

    class Config:
        env_file = os.environ.get("env_file") or os.environ.get("ENV_FILE") or ".env"
