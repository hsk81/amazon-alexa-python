#!/usr/bin/env python
###########################################################################

from setuptools import setup

###########################################################################
###########################################################################

setup(
    name='alexa-signature-verification',
    version='0.0.1',
    description='Amazon Alexa: request sigature verification',
    author='Hasan Karahan',
    author_email='hkarahan@dizmo.com',
    install_requires=[
        'pem==17.1.0',
        'pyOpenSSL==17.5.0',
        'redis==2.10.6',
        'requests==2.18.4'
    ],
)

###########################################################################
###########################################################################
