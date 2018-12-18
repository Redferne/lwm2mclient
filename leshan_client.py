#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
from client import Client
from model import ClientModel

# Enable logging
import logging
import sys


#logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("main")

logger.info("Starting...")
model = ClientModel()
client = Client(model=model)
client.set_server_uri('coaps://leshan.eclipse.org:5684')
client.set_endpoint('my_endpoint')  # Leshan Client endpoint
client.set_identity('my_identity')  # Leshan Identity
client.set_key('1234') # Leshan Key: 31323334
client.set_misc("123", 90, "U")
loop = asyncio.get_event_loop()
asyncio.ensure_future(client.run())
try:
    loop.run_forever()
except KeyboardInterrupt:
    loop.close()
    exit(0)
