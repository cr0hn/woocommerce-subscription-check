import logging
import datetime

from woocommerce_subscription_check.exceptions import WSCAuthentication

log = logging.getLogger("woocommerce_subscription_check")


def send_to_sentry(request, message: str):

    if hasattr(request.app, "sentry"):
        request.app.sentry.client.capture("raven.events.Message",
                                          message=message,
                                          extra={"body": request.body})


def get_user_from_token(session, token) -> str or WSCAuthentication:
    """
    Cases:
    - If token is not in session -> user was not authenticated
    """
    try:
        return session[token]

    except KeyError:
        raise WSCAuthentication("Invalid token")


def extract_jwt_from_header(header_line):

    _, token = header_line.split(" ", maxsplit=1)

    # Remove extra spaces

    return token.strip()


def calculate_pending_days(date: str) -> int:
    today = datetime.datetime.now()
    try:
        next_payment = datetime.datetime.strptime(
            date,
            '%Y-%m-%dT%H:%M:%S')
        return (next_payment - today).days
    except ValueError:
        return -1


def get_subscription_from_cache(session, token: str, user_id: str):
    try:
        # Get cached user info
        subscription_name, subscription_status, expire_date = \
            session[f"{token}_{user_id}"]

        # Check if we need to refresh the information.
        if calculate_pending_days(expire_date) < 0:
            # Need to refresh
            return None, None, None
        else:
            return subscription_name, subscription_status, expire_date
    except KeyError:
            return None, None, None


def set_subscription_cache(session,
                           token: str,
                           user_id: str,
                           subscription_name: str,
                           subscription_status: str,
                           expire_date: str):
    if subscription_status and subscription_name and expire_date:

        session[f"{token}_{user_id}"] = (subscription_name,
                                         subscription_status,
                                         expire_date)


__all__ = ("send_to_sentry", "get_user_from_token", "extract_jwt_from_header",
           "calculate_pending_days", "set_subscription_cache",
           "get_subscription_from_cache")
