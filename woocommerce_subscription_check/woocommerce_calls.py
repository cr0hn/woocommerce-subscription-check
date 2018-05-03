try:
    import ujson as json
except ImportError:
    import json

import aiohttp

from sanic import Sanic
from typing import Tuple

from woocommerce_subscription_check.exceptions import WSCException, \
    WSCAuthentication, WSCAuthenticationAdmin


async def connect_admin(app: Sanic):
    status, admin_token, user_id = await do_login(
        app.config["ADMIN_ROLE_USER"],
        app.config["ADMIN_ROLE_PASSWORD"],
        app.config["WSC_DOMAIN"],
        app.config["WSC_SCHEME"])

    if status == 403:
        raise WSCAuthenticationAdmin("Can't authenticate Admin! Ensure Admin / "
                                     "Password for admin role are correct")

    app.config["ADMIN_TOKEN"] = admin_token


async def get_subscriptions(admin_token: str,
                            user_id: str,
                            domain: str,
                            http_scheme: str = "https") \
        -> Tuple or WSCException or WSCAuthentication:
    """

    return format: Tuple(subscription, status, next payment date)

    Where:
    - subscription: ["none" | "subscription name" ],
    - status: ["none" | ["active" | "inactive" ] ]
    - next payment date: ["none" | "date time format"]

    """

    auth_url = f'{http_scheme}://{domain}/wp-json/wc/v1/subscriptions?' \
               f'customer={user_id}&status=active'

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(auth_url,
                                   headers={
                                       "Authorization": f"Bearer {admin_token}"
                                   }) as resp:

                json_answer = await resp.json()

                if resp.status == 403:
                    raise WSCAuthenticationAdmin("Admin token expired")
                elif resp.status != 200:
                    return WSCException(f"Unexpected answer: {resp.status} - "
                                        f"{str(json_answer)}")

                try:
                    json_answer = json_answer[0]
                except IndexError:

                    # The user have not subscriptions
                    return "none", "none", ""

                # -------------------------------------------------------------
                # Check if requested user match with user returned user
                # -------------------------------------------------------------
                returned_user_id = json_answer["customer_id"]

                if returned_user_id != user_id:
                    raise WSCAuthentication("You can't get subscriptions for"
                                            "other users than you")

                # -------------------------------------------------------------
                # If there is more than one subscription, return the higher.
                # The higher is the more expensive
                # -------------------------------------------------------------
                result_subscription = {}
                for subscription in json_answer["line_items"]:
                    subscription_price = float(subscription.get("total", 0))
                    subscription_price_before = \
                        float(result_subscription.get("total", 0))

                    if subscription_price > subscription_price_before:
                        result_subscription = subscription

                # -------------------------------------------------------------
                # Get subscription info
                # -------------------------------------------------------------
                status = "active" if json_answer["status"] == "active" \
                    else "inactive"
                subscription = result_subscription.get("name", "").lower()

                return subscription, status, json_answer["next_payment_date"]

    except Exception as e:
        raise WSCException(f"Error while try to get subscriptions: {e}")


async def do_login(user: str,
                   password: str,
                   domain: str,
                   http_scheme: str = "https",
                   loop = None):
    """
    returns:

    (status, token, user_id)

    """

    auth_url = f'{http_scheme}://{domain}/wp-json/jwt-auth/v1/token'
    user_info_url = f'{http_scheme}://{domain}/wp-json/wp/v2/users/me'

    try:
        async with aiohttp.ClientSession() as session:
            # -----------------------------------------------------------------
            # Do authentication
            # -----------------------------------------------------------------
            async with session.post(auth_url,
                                    json={
                                        "username": user,
                                        "password": password
                                    }) as resp:
                json_answer = await resp.json()
                if resp.status != 200:
                    return resp.status, None, None

                token = json_answer["token"]

            # -----------------------------------------------------------------
            # Get User ID
            # -----------------------------------------------------------------
        async with aiohttp.ClientSession(cookies=None, cookie_jar=None) as session2:
            session2.cookie_jar.clear()
            async with session2.get(user_info_url,
                                    headers={
                                        "Authorization": f"Bearer {token}",
                                        "Content-Type": "Application/json"
                                    }) as resp2:
                if resp2.status != 200:
                    return resp2.status, None

                if "text" in resp2.content_type:
                    json_resp = json.loads(await resp2.text())
                else:
                    json_resp = await resp2.json()

                return resp.status, token, json_resp["id"]
    except Exception as e:
        raise WSCException(f"Error while try to authenticate: {e}")

__all__ = ("do_login", "get_subscriptions", "connect_admin")
