WooCommerce Subscription Checker
================================

+----------------+-----------------------------------------------------------------+
|Current version | 1.0                                                           |
+----------------+-----------------------------------------------------------------+
|Project site    | https://github.com/cr0hn/woocommerce-subscription-check         |
+----------------+-----------------------------------------------------------------+
|Issues          | https://github.com/cr0hn/woocommerce-subscription-check/issues/ |
+----------------+-----------------------------------------------------------------+
|Python versions | 3.6 or above                                                    |
+----------------+-----------------------------------------------------------------+


Motivations
===========

Woocommerce doesn't allow to check the user subscriptions (or any other data) from the Wordpress API without being an admin user.

This means that if a regular user want to check their subscriptions, products or something else, it need to be an admin role. And, in non-secure scenarios, this is not good idea, i.e: in the browser through Javascript

What that project does?
=======================

This project exposes non-privileged API and allow to regular users to check their subscription, without the need to have an admin role.

Requirements
============

You must install in your Wordpress the plugins:

- JWT Authentication for WP-API
- WP REST API
- Disable REST API and Require JWT (Recommendable)

**IMPORTANT**

Be careful with JWT plugin. Ensure you follow these steps, in the same order:

1 - Add to wp-config.php
------------------------

Add these lines in your wp-config.php:

define('JWT_AUTH_SECRET_KEY', 'your-top-secrect-key');
define('JWT_AUTH_CORS_ENABLE', true);

**IT'S MORE IMPORTANT** to add these lines just before the definition of AUTH_KEY, SECURE_AUTH_KEY... (https://github.com/Tmeister/wp-api-jwt-auth/issues/59)

2 - Activate the plugin
-----------------------

After you add the data from step 1, then activate the plugin.

Environment vars
================

- LISTEN_ADDR (default: 127.0.0.1)
- LISTEN_PORT (default: 9000)
- API_PREFIX (default: v1)
- LOG_LEVEL (default: 1)
- SENTRY_DSN (default: None)
- REDIS_HOST (default: 127.0.0.1)
- REDIS_PORT (default: 6379)
- REDIS_DB (default: 1)
- SCHEME (default: https)
- DOMAIN: **Mandatory**
- ADMIN_ROLE_USER: **Mandatory**
- ADMIN_ROLE_PASSWORD: **Mandatory**


Docker Image
============

.. code-block:: bash

    > docker run -p 9000:9000 --rm cr0hn/woocommerce-subscription-check


End-points
==========

/api/v1/login
--------------

**General**

- Method: POST
- Input data as JSON
- Input value: user / password

**Example request**

.. code-block:: bash

    > curl -v -X POST http://127.0.0.1:9000/api/v1/login -d '{"user": "MyUser", "password": "MyPassword"}'

**Example responses**

*Authentication done*

- HTTP STATUS: 200
- Response:

.. code-block:: json

    {"token":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI19s82.eyJpc3MiOiJodHRwczpcL1wvd2hvaXNsZWF2aW5nLmNvbSIsImlhdCI6MTUyMzQ0ODQxMSwibmJmIjoxNTIzNDQ4NDExLCJleHAiOjE1MjQwNTMyMTEsImRhdGEiOnsidXNlciI6eyJpZCI6IjIifX19.bu8ChmreEqDt5wwACSB5L_-8V9hHPRzJI-zGHB1Unv4"}


*Authentication fails*

- HTTP STATUS: 403
- Response:

.. code-block:: json

    {"message":"Invalid user or password"}

*Invalid Data*

- HTTP STATUS: 400
- Response: "Invalid JSON"

/api/v1/subscriptions
---------------------

**General**

- Method: GET
- Input value: user / password

**Example request**

.. code-block:: bash

    > curl -v -X POST http://127.0.0.1:9000/api/v1/subscriptions -H 'Authorization: Bearer TOKEN_FROM_LOGIN'

**Example responses**

*user has subscriptions*

- HTTP STATUS: 200
- Response:

.. code-block:: json

    {
        "subscriptionName": "micro",
        "subscriptionStatus": "active",
        "expireDate": "2018-05-10T16:17:31"
    }

*user has NOT subscriptions*

- HTTP STATUS: 200
- Response:

.. code-block:: json

    {
        "subscriptionName": null,
        "subscriptionStatus": null,
        "expireDate": null
    }

*Authentication fails*

- HTTP STATUS: 403
- Response:

.. code-block:: json

    {"message":"Invalid token. You must authenticate first"}

*Invalid Data*

- HTTP STATUS: 400
- Response: "Invalid JSON"