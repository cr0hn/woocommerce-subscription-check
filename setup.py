import os

from os import path
from os.path import join, abspath, dirname
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst')) as f:
    readme = f.read()

with open(join(here, 'requirements.txt')) as f:
    required = f.read().splitlines()

with open(join(abspath(dirname(__file__)), "VERSION"), "r") as v:
    VERSION = v.read().replace("\n", "")

RELEASE = os.getenv("CIRCLE_BUILD_NUM")

setup(
    name='woocommerce_subscriptions_check',
    version=f"{VERSION}.{RELEASE}",
    packages=find_packages(),
    long_description=readme,
    install_requires=required,
    extras_require={
        'sentry': ["sanic-sentry"]
    },
    include_package_data=True,
    url='https://github.com/cr0hn/woocommerce-subscriptions-check',
    author='Daniel Garcia (cr0hn)',
    description='Check user subscriptions in Woocommerce without have and '
                'admin role',
    entry_points={'console_scripts': [
        'wsc-server = woocommerce_subscription_check.app:main',
    ]},
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3',
    ],
)

