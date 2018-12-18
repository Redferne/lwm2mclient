#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

from setuptools import setup

setup(
    name="lwm2mclient",
    version="0.2.0+git",
    description="Lightweight M2M Client written in Python",
    author="Alexander Ellwein",
    author_email="alex.ellwein@gmail.com",
    license="MIT License",
    install_requires=["aiocoap @ git+https://github.com/Redferne/aiocoap.git",
    				  "DTLSSocket>=0.1.9",
    				  "cryptography>=2.4.2",
    				  "cbor>=1.0.0",
    				  "LinkHeader>=0.4.3",
    				  "hexdump>=3.3"]
)
