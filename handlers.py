# -*- coding: utf-8 -*-

# Implement your handlers here.

import asyncio
import logging
import time

#logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("handlers")


def handle_firmware_update(*args, **kwargs):
    logger.info("handle_firmware_update(): {}, {}".format(args, kwargs))


def handle_disable(*args, **kwargs):
    logger.info("handle_disable(): {}, {}".format(args, kwargs))


def handle_update_trigger(*args, **kwargs):
    logger.info("handle_update_trigger(): {}, {}".format(args, kwargs))


def handle_reboot(*args, **kwargs):
    logger.info("handle_reboot(): {}, {}".format(args, kwargs))


def handle_factory_reset(*args, **kwargs):
    logger.info("handle_factory_reset(): {}, {}".format(args, kwargs))


def handle_reset_error_code(*args, **kwargs):
    logger.info("handle_reset_error_code(): {}, {}".format(args, kwargs))
    model = kwargs["model"]
    # reset error code in model data
    model.set_resource("3", "0", "11", {"0": 0})

def observe_3_0_13(*args, **kwargs):
    async def update():
        while True:
            await asyncio.sleep(10)
            model.set_resource("3", "0", "13", int(time.time()))
            updater()

    async def cancel():
        tick.cancel()

    model = kwargs["model"]
    updater = kwargs["updater"]
    tick = asyncio.Task(update())
