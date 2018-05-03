from sanic import response
from sanic.blueprints import Blueprint

from woocommerce_subscription_check.helpers import get_user_from_token, \
    extract_jwt_from_header, send_to_sentry, get_subscription_from_cache, \
    set_subscription_cache
from woocommerce_subscription_check.exceptions import WSCAuthentication, \
    WSCAuthenticationAdmin
from woocommerce_subscription_check.woocommerce_calls import \
    get_subscriptions, connect_admin


subscriptions = Blueprint("subscriptions")


def _build_response(subscription_name, subscription_status, expire_date):
    return response.json(
        {
            "subscriptionName": subscription_name,
            "subscriptionStatus": subscription_status,
            "expireDate": expire_date
        }
    )


@subscriptions.route("/subscriptions", methods=["GET"])
async def get_subscriptions_api(request):

    # Check that request has the token
    try:
        authorization = request.headers["authorization"]
    except KeyError:
        return response.json("Invalid Token. You must authenticate first",
                             status=403)

    token = extract_jwt_from_header(authorization)

    # -------------------------------------------------------------------------
    # Get user
    # -------------------------------------------------------------------------
    try:
        user_id = get_user_from_token(request["session"], token)
    except WSCAuthentication:
        return response.json(dict(
            message="Invalid token. You must authenticate first"),
            status=403)

    # -------------------------------------------------------------------------
    # Check if user has a valid subscription in the session
    # -------------------------------------------------------------------------
    sn, st, et = get_subscription_from_cache(request["session"],
                                             token,
                                             user_id)

    if st:
        return _build_response(sn, st, et)

    # -------------------------------------------------------------------------
    # If not in cache....
    # -------------------------------------------------------------------------
    subscription_coro = get_subscriptions(request.app.config["ADMIN_TOKEN"],
                                          user_id,
                                          request.app.config["WSC_DOMAIN"],
                                          request.app.config["WSC_SCHEME"])

    try:
        sn, st, ed = await subscription_coro

        if sn == "none":
            sn = None
            st = None
            ed = None

    except WSCAuthenticationAdmin:
        await connect_admin(request.app)

        try:
            sn, st, ed = await subscription_coro

            if sn == "none":
                sn = None
                st = None
                ed = None

        except WSCAuthenticationAdmin:
            send_to_sentry(request, "Admin connection error while try to get"
                                    "a user subscription")
            return response.json(dict(message="Service not available"), 500)

    # -------------------------------------------------------------------------
    # Storage in session
    # -------------------------------------------------------------------------
    set_subscription_cache(request["session"], token, user_id, sn, st, ed)

    return _build_response(sn, st, ed)
