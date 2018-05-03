import sanic
import asyncio
import concurrent
import asyncio_redis

from os.path import abspath, dirname, join

from sanic import Sanic, response
from sanic_session import RedisSessionInterface
from sanic.exceptions import NotFound, ServerError

from woocommerce_subscription_check.helpers import send_to_sentry
from woocommerce_subscription_check.woocommerce_calls import connect_admin
from woocommerce_subscription_check.blueprints import subscriptions, \
    health_check, login_blueprint


def setup_redis(app: Sanic):

    class Redis:
        """
        A simple wrapper class that allows you to share a connection
        pool across your application.
        """
        _pool = None

        async def get_redis_pool(self):
            if not self._pool:
                self._pool = await asyncio_redis.Pool.create(
                    host=app.config['WSC_REDIS_HOST'],
                    port=app.config['WSC_REDIS_PORT'],
                    db=app.config["WSC_REDIS_DB"],
                    poolsize=10,
                    auto_reconnect=True)

            return self._pool

    async def check_connection(e_loop):
        try:
            connection = await asyncio.wait_for(
                asyncio_redis.Connection.create(
                    host=app.config['WSC_REDIS_HOST'],
                    port=app.config['WSC_REDIS_PORT'],
                    db=app.config["WSC_REDIS_DB"]),
                timeout=5,
                loop=e_loop)

            await connection.ping()

            connection.close()

        except concurrent.futures._base.TimeoutError:
            raise TimeoutError("Can't connect to Redis")

    # -------------------------------------------------------------------------
    # Check connection to redis
    # -------------------------------------------------------------------------
    loop = asyncio.get_event_loop()
    loop.run_until_complete(check_connection(loop))

    redis = Redis()
    app.config["REDIS"] = redis


def configure_session(app: Sanic):
    redis = app.config["REDIS"]

    session_interface = RedisSessionInterface(redis.get_redis_pool)

    @app.middleware('request')
    async def add_session_to_request(request):
        # before each request initialize a session
        # using the client's request
        await session_interface.open(request)

    @app.middleware('response')
    async def save_session(request, response):
        # after each request save the session,
        # pass the response to set client cookies
        await session_interface.save(request, response)


def setup_app(app: Sanic = None,
              enable_blueprints: bool = True,
              start_session: bool = True,
              enable_sentry: bool = True) -> Sanic:

    here = abspath(dirname(__file__))

    # -------------------------------------------------------------------------
    # Load internal config
    # -------------------------------------------------------------------------
    app = app or Sanic(__name__)
    app.config.from_pyfile(join(here, "config.py"))

    @app.exception(NotFound)
    async def ignore_404s(request, exception):
        send_to_sentry(request, "Page not found")
        return response.text("Yep, I can't find this page!")

    @app.exception(ServerError)
    async def ignore_500s(request, exception):
        send_to_sentry(request, "Internal Server Error")
        return response.text("Yep, What're you doing?!")

    @app.listener("before_server_start")
    async def after_start(app, loop, **kwargs):
        # ---------------------------------------------------------------------
        # THIS END-POINT LOAD ADMIN CREDENTIALS TO CONSUME WOOCOMMERCE API
        # ---------------------------------------------------------------------
        await connect_admin(app)

    # -------------------------------------------------------------------------
    # Sentry, if available
    # -------------------------------------------------------------------------
    if app.config.WSC_SENTRY_DSN and enable_sentry:
        from sanic_sentry import SanicSentry

        app.config['SENTRY_DSN'] = app.config["WSC_SENTRY_DSN"]
        plugin = SanicSentry(app)
        plugin.init_app(app)

    if start_session:
        # -------------------------------------------------------------------------
        # Setup Redis
        # -------------------------------------------------------------------------
        setup_redis(app)

        # -------------------------------------------------------------------------
        # Session
        # -------------------------------------------------------------------------
        configure_session(app)

    # -------------------------------------------------------------------------
    # Blueprints
    # -------------------------------------------------------------------------
    if enable_blueprints:
        try:
            app.blueprint(health_check)
        except sanic.router.RouteExists:
            pass

        app.blueprint(subscriptions,
                      url_prefix=f"/api/"
                                 f"{app.config['WSC_API_PREFIX']}")
        app.blueprint(login_blueprint,
                      url_prefix=f"/api/"
                                 f"{app.config['WSC_API_PREFIX']}")

    return app


__all__ = ("setup_app", )
