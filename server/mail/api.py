"""
Handles mail API
"""

import requests
import server.constants as const


def send_to_sysadmin(subject: str, body: str) -> bool:
    """
    Sends an email to the configured sysadmin email.
    :param subject: Subject of email
    :param body: Contents of email
    :return:
    """
    response = requests.post(
            f"https://api.mailgun.net/v3/{const.EMAIL_DOMAIN}/messages",
            auth=("api", f"{const.EMAIL_API_KEY}"),
            data={"from":    f"Shepherd Alert <shepherd@{const.EMAIL_DOMAIN}>",
                  "to":      [f"{const.EMAIL_RECIPIENT}", ],
                  "subject": f"{subject}",
                  "html":    f"{body}"})
    return 200 <= response.status_code < 300


def make_new_alert_message(timestamp, typ, message, severity, node_id) -> str:
    """

    :param node_id:
    :param timestamp:
    :param typ:
    :param message:
    :param severity:
    :return:
    """
    return open("server/mail/alert.html").read().replace('$$$timestamp$$$', f'{str(timestamp)}')\
        .replace('$$$type$$$', f'{str(typ).upper()}')\
        .replace('$$$message$$$', f'{str(message)}')\
        .replace('$$$severity$$$', f'{str(severity)}') \
        .replace('$$$id$$$', f'{str(node_id)}')\
        .replace('$$$detected$$$', 'detected')


def make_new_resolved_message(timestamp, typ, message, severity, node_id) -> str:
    """

    :param timestamp:
    :param typ:
    :param message:
    :param severity:
    :param node_id:
    :return:
    """
    return open("server/mail/alert.html").read().replace('$$$timestamp$$$', f'{str(timestamp)}') \
        .replace('$$$type$$$', f'{str(typ).upper()}') \
        .replace('$$$message$$$', f'{str(message)}') \
        .replace('$$$severity$$$', f'{str(severity)}') \
        .replace('$$$id$$$', f'{str(node_id)}')\
        .replace('$$$detected$$$', 'resolved')
