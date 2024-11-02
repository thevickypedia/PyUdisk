import logging

import requests

from .config import EnvConfig

LOGGER = logging.getLogger(__name__)


def urljoin(*args):
    """Joins given arguments into an url. Trailing but not leading slashes are stripped for each argument.

    Returns:
        str:
        Joined url.
    """
    return "/".join(map(lambda x: str(x).rstrip('/').lstrip('/'), args))


def notification_service(title: str, message: str, env_config: EnvConfig):
    """Sends notifications using Ntfy and Telegram services."""
    if env_config.ntfy_url and env_config.ntfy_topic:
        ntfy_fn(
            title=title,
            message=message,
            url=env_config.ntfy_url,
            topic=env_config.ntfy_topic,
            username=env_config.ntfy_username,
            password=env_config.ntfy_password,
        )
    if env_config.telegram_bot_token and env_config.telegram_chat_id:
        telegram_fn(
            title=title,
            message=message,
            bot_token=env_config.telegram_bot_token,
            chat_id=env_config.telegram_chat_id,
            message_thread_id=env_config.telegram_thread_id,
            disable_notification=False,
        )


def ntfy_fn(
        title: str,
        message: str,
        url: str,
        topic: str,
        username: str = None,
        password: str = None,
) -> None:
    """Sends a notification using Ntfy service."""
    session = requests.Session()
    if username and password:
        session.auth = (username, password)
    try:
        response = session.post(
            url=urljoin(url, topic),
            headers={
                'X-Title': title,
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            data=message,
        )
        response.raise_for_status()
        LOGGER.debug(response.json())
    except requests.RequestException as error:
        LOGGER.error(error)


def telegram_fn(
        title: str,
        message: str,
        bot_token: str,
        chat_id: int,
        message_thread_id: int = None,
        disable_notification: bool = False,
) -> None:
    """Sends a notification using Telegram."""
    text = f"*{title}*\n{message}"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "markdown",
        "disable_notification": disable_notification
    }
    if message_thread_id:
        payload["message_thread_id"] = message_thread_id
    try:
        response = requests.post(
            f"https://api.org/bot{bot_token}/sendMessage",
            json=payload
        )
        response.raise_for_status()
        LOGGER.debug(response.json())
    except requests.RequestException as error:
        LOGGER.error(error)
