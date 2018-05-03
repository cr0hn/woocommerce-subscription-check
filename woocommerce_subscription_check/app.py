import logging

from woocommerce_subscription_check.setup_app import setup_app

log = logging.getLogger("woocommerce_subscription_check")

# --------------------------------------------------------------------------
# Setup App
# --------------------------------------------------------------------------
app = setup_app()

if __name__ == '__main__':
    app.run(host=app.config["WSC_LISTEN_ADDR"],
            port=app.config["WSC_LISTEN_PORT"])
