from threading import Thread
from typing import List

from .config import EnvConfig
from .logger import LOGGER
from .util import standard


def urljoin(*args) -> str:
    """Joins given arguments into an url. Trailing but not leading slashes are stripped for each argument.

    Returns:
        str:
        Joined url.
    """
    return "/".join(map(lambda x: str(x).rstrip("/").lstrip("/"), args))


def notification_service(title: str, message: str, env_config: EnvConfig) -> None:
    """Sends notifications using Ntfy and Telegram services.

    Args:
        title: Notification title.
        message: Body of the notification.
        env_config: Environment variables' configuration.
    """
    threads: List[Thread] = []
    if env_config.ntfy_url and env_config.ntfy_topic:
        thread = Thread(
            target=ntfy_fn,
            kwargs=dict(
                title=title,
                message=message,
                url=env_config.ntfy_url,
                topic=env_config.ntfy_topic,
                username=env_config.ntfy_username,
                password=env_config.ntfy_password,
            ),
        )
        threads.append(thread)
    if env_config.telegram_bot_token and env_config.telegram_chat_id:
        thread = Thread(
            target=telegram_fn,
            kwargs=dict(
                title=title,
                message=message,
                bot_token=env_config.telegram_bot_token,
                chat_id=env_config.telegram_chat_id,
                message_thread_id=env_config.telegram_thread_id,
                disable_notification=False,
            ),
        )
        threads.append(thread)
    if env_config.gmail_user and env_config.gmail_pass and env_config.phone:
        thread = Thread(
            target=sms_fn,
            kwargs=dict(
                title=title,
                message=message,
                user=env_config.gmail_user,
                password=env_config.gmail_pass,
                phone=env_config.phone,
            ),
        )
        threads.append(thread)
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()


def send_report(
    title: str, user: str, password: str, recipient: str, content: str
) -> None:
    """Sends an email notification using Gmail's SMTP protocol.

    Args:
        title: Notification title.
        user: Gmail username.
        password: Gmail password.
        recipient: Email recipient.
        content: HTML body to attach to the email.
    """
    try:
        import gmailconnector as gc
    except ModuleNotFoundError:
        standard()

    email_obj = gc.SendEmail(gmail_user=user, gmail_pass=password)
    response = email_obj.send_email(
        subject=title, recipient=recipient, html_body=content
    )
    if response.ok:
        LOGGER.info("Report sent successfully")
    else:
        LOGGER.error("Failed to send report")
        LOGGER.error(response.json())


def sms_fn(title: str, message: str, user: str, password: str, phone: str) -> None:
    """Sends an SMS notification using Gmail's SMTP protocol.

    Args:
        title: Notification title.
        message: Body of the notification.
        user: Gmail username.
        password: Gmail password.
        phone: Phone number to send the SMS.
    """
    try:
        import gmailconnector as gc
    except ModuleNotFoundError:
        standard()

    sms_obj = gc.SendSMS(gmail_user=user, gmail_pass=password)
    response = sms_obj.send_sms(phone=phone, message=message, subject=title)
    if response.ok:
        LOGGER.info("SMS notification sent successfully")
    else:
        LOGGER.error("Failed to SMS notification")
        LOGGER.error(response.json())


def ntfy_fn(
    title: str,
    message: str,
    url: str,
    topic: str,
    username: str = None,
    password: str = None,
) -> None:
    """Sends a notification using Ntfy service.

    Args:
        title: Notification title.
        message: Body of the notification.
        url: Ntfy service url.
        topic: Ntfy service topic.
        username: Ntfy service username.
        password: Ntfy service password.
    """
    try:
        import requests
    except ModuleNotFoundError:
        standard()

    session = requests.Session()
    if username and password:
        session.auth = (username, password)
    try:
        response = session.post(
            url=urljoin(url, topic),
            headers={
                "X-Title": title,
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data=message,
        )
        response.raise_for_status()
        LOGGER.info("Ntfy notification sent successfully")
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
    """Sends a notification using Telegram.

    Args:
        title: Notification title.
        message: Body of the notification.
        bot_token: Telegram bot token.
        chat_id: Telegram chat id.
        message_thread_id: Message thread id.
        disable_notification: Boolean flag to disable notification.
    """
    try:
        import requests
    except ModuleNotFoundError:
        standard()

    text = f"*{title}*\n{message}"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "markdown",
        "disable_notification": disable_notification,
    }
    if message_thread_id:
        payload["message_thread_id"] = message_thread_id
    try:
        response = requests.post(
            f"https://api.org/bot{bot_token}/sendMessage", json=payload
        )
        response.raise_for_status()
        LOGGER.info("Telegram notification sent successfully")
        LOGGER.debug(response.json())
    except requests.RequestException as error:
        LOGGER.error(error)
