from sanic import response
from sanic.blueprints import Blueprint

health_check = Blueprint("health-check")


@health_check.route("/",
                    methods=["GET"])
async def home(request):
    return response.text("pong")

