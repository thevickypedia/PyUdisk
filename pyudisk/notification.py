from threading import Thread
from typing import List

from . import config, util
from .logger import LOGGER


def urljoin(*args) -> str:
    """Joins given arguments into an url. Trailing but not leading slashes are stripped for each argument.

    Returns:
        str:
        Joined url.
    """
    return "/".join(map(lambda x: str(x).rstrip("/").lstrip("/"), args))


def notification_service(title: str, message: str) -> None:
    """Sends notifications using Ntfy and Telegram services.

    Args:
        title: Notification title.
        message: Body of the notification.
    """
    threads: List[Thread] = []
    if config.env.ntfy_url and config.env.ntfy_topic:
        thread = Thread(
            target=ntfy_fn,
            kwargs=dict(
                title=title,
                message=message,
            ),
        )
        threads.append(thread)
    if config.env.telegram_bot_token and config.env.telegram_chat_id:
        thread = Thread(
            target=telegram_fn,
            kwargs=dict(
                title=title,
                message=message,
                disable_notification=False,
            ),
        )
        threads.append(thread)
    if config.env.gmail_user and config.env.gmail_pass and config.env.phone:
        thread = Thread(
            target=sms_fn,
            kwargs=dict(
                title=title,
                message=message,
            ),
        )
        threads.append(thread)
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()


def send_report(title: str, content: str) -> None:
    """Sends an email notification using Gmail's SMTP protocol.

    Args:
        title: Notification title.
        content: HTML body to attach to the email.
    """
    try:
        import gmailconnector as gc
    except ModuleNotFoundError:
        util.standard()

    email_obj = gc.SendEmail(
        gmail_user=config.env.gmail_user, gmail_pass=config.env.gmail_pass
    )
    response = email_obj.send_email(
        subject=title, recipient=config.env.recipient, html_body=content
    )
    if response.ok:
        LOGGER.info("Report sent successfully")
    else:
        LOGGER.error("Failed to send report")
        LOGGER.error(response.json())


def sms_fn(title: str, message: str) -> None:
    """Sends an SMS notification using Gmail's SMTP protocol.

    Args:
        title: Notification title.
        message: Body of the notification.
    """
    try:
        import gmailconnector as gc
    except ModuleNotFoundError:
        util.standard()

    sms_obj = gc.SendSMS(
        gmail_user=config.env.gmail_user, gmail_pass=config.env.gmail_pass
    )
    response = sms_obj.send_sms(phone=config.env.phone, message=message, subject=title)
    if response.ok:
        LOGGER.info("SMS notification sent successfully")
    else:
        LOGGER.error("Failed to SMS notification")
        LOGGER.error(response.json())


def ntfy_fn(title: str, message: str) -> None:
    """Sends a notification using Ntfy service.

    Args:
        title: Notification title.
        message: Body of the notification.
    """
    try:
        import requests
    except ModuleNotFoundError:
        util.standard()

    session = requests.Session()
    if config.env.ntfy_username and config.env.ntfy_password:
        session.auth = (config.env.ntfy_username, config.env.ntfy_password)
    try:
        response = session.post(
            url=urljoin(config.env.ntfy_url, config.env.ntfy_topic),
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


def telegram_fn(title: str, message: str, disable_notification: bool = False) -> None:
    """Sends a notification using Telegram.

    Args:
        title: Notification title.
        message: Body of the notification.
        disable_notification: Boolean flag to disable notification.
    """
    try:
        import requests
    except ModuleNotFoundError:
        util.standard()

    text = f"*{title}*\n{message}"
    payload = {
        "chat_id": config.env.telegram_chat_id,
        "text": text,
        "parse_mode": "markdown",
        "disable_notification": disable_notification,
    }
    if config.env.telegram_thread_id:
        payload["message_thread_id"] = config.env.telegram_thread_id
    try:
        response = requests.post(
            f"https://api.org/bot{config.env.telegram_bot_token}/sendMessage",
            json=payload,
        )
        response.raise_for_status()
        LOGGER.info("Telegram notification sent successfully")
        LOGGER.debug(response.json())
    except requests.RequestException as error:
        LOGGER.error(error)
