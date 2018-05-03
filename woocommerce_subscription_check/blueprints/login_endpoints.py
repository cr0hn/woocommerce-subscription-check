from sanic import response
from sanic.blueprints import Blueprint

from woocommerce_subscription_check.helpers import send_to_sentry
from woocommerce_subscription_check.woocommerce_calls import do_login
from woocommerce_subscription_check.exceptions import WSCException

login_blueprint = Blueprint("login")


@login_blueprint.route("/login", methods=["POST"])
async def login(request):
    try:
        in_data = request.json
    except Exception:
        # Send to sentry
        send_to_sentry(request, "Invalid JSON")
        return response.text("Invalid JSON", status=400)

    if not all(x in in_data for x in ("user", "password")):
        return response.json("Invalid user or password", status=403)

    try:
        user = in_data["user"]
        password = in_data["password"]

        status, token, user_id = await do_login(
            user,
            password,
            request.app.config["WSC_DOMAIN"],
            request.app.config["WSC_SCHEME"]
        )

        if status == 403:
            return response.json(dict(message="Invalid user or password"),
                                 status=403)
        else:

            # -----------------------------------------------------------------
            # Update session
            # -----------------------------------------------------------------
            request["session"][token] = user_id

            return response.json(dict(token=token),
                                 status=200)

    except WSCException:
        return response.json({
            "Internal error"
        }, status=500)

