#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from aiocoap import error
from aiocoap import defaults
from aiocoap import resource
from aiocoap.message import Message
from aiocoap.numbers.codes import Code
from aiocoap.protocol import Context
from aiocoap.resource import ObservableResource
from aiocoap.resource import Resource
from aiocoap.resource import Site
from encdec import PayloadEncoder, PayloadDecoder
from handlers import *
from model import ClientModel

#Console Debugging
#logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("client")

class ResourceHandler(ObservableResource):
    def __init__(self, path, model, encoder, decoder):
        super(ResourceHandler, self).__init__()
        self.path = path
        self.model = model
        self.encoder = encoder
        self.decoder = decoder
        self._observe_count = 0

    def handle_write(self, path, payload, content_format):
        return self.decoder.decode(path, payload, content_format)

    def _updater(self):
        if self._observe_count > 0:
            self.updated_state(response=self.encoder.encode(self.path))

    def update_observation_count(self, newcount):
        logger.info("Observe Count: %s", str(newcount))
        self._observe_count = newcount
        obs = "observe_{}_{}_{}".format(self.path[0], self.path[1], self.path[2])
        try:
            obs_method = eval(obs)
            if newcount > 0:
                _kwargs = dict(model=self.model, updater=self._updater)
                obs_method(None, **_kwargs)
            else:
                obs_method.cancel()
        except NameError:
            logger.error(
                "observe handler for %s is not implemented. Please implement it in handlers.py" % ("/".join(path)))
            pass
        return

    def handle_exec(self, request):
        path = request.opt.uri_path
        if len(path) != 3 or not self.model.is_path_valid(path):
            return Message(code=Code.BAD_REQUEST)
        if not self.model.is_resource_executable(path[0], path[1], path[2]):
            return Message(code=Code.METHOD_NOT_ALLOWED)
        _op = str(self.model.resource(path[0], path[1], path[2]))
        try:
            _op_method = eval(_op)
        except NameError:
            logger.error(
                "handler \"%s\" for %s is not implemented. Please implement it in handlers.py" % (_op, "/".join(path)))
            return Message(code=Code.NOT_IMPLEMENTED)
        _kwargs = dict(model=self.model, payload=request.payload, path=path, content_format=request.opt.content_format)
        result = _op_method(None, **_kwargs)
        return Message(code=Code.CHANGED, payload=result) if result is not None else Message(code=Code.CHANGED)

    async def render_get(self, request):
        return self.encoder.encode(request.opt.uri_path)

    async def render_put(self, request):
        logger.debug("write on %s" % "/".join(request.opt.uri_path))
        message, _decoded = self.handle_write(request.opt.uri_path, request.payload, request.opt.content_format)
        if message.code == Code.CHANGED:
            self.model.apply(_decoded)
        return message

    async def render_post(self, request):
        logger.debug("execute on %s" % "/".join(request.opt.uri_path))
        return self.handle_exec(request)


class Client(Site):
    context = None
    rd_resource = None

    def __init__(self, model=ClientModel(), server="localhost", server_port=5683):
        super(Client, self).__init__()
        self.server = server
        self.server_port = server_port
        self.model = model
        self.model.set_resource("0", "0", "0", server)
        self.endpoint = "lwm2m_python"
        self.binding_mode = "UQ"
        self.identity = ""
        self.key = ""
        self.uri = ""
        self.lifetime = 90  # default: 86400
        self.encoder = PayloadEncoder(model)
        self.decoder = PayloadDecoder(model)
        for path in model.instance_iter():
            self.add_resource(path, ResourceHandler(path, self.model, self.encoder, self.decoder))
        for path in model.resource_iter():
            self.add_resource(path, ResourceHandler(path, self.model, self.encoder, self.decoder))

    def set_server(self, server):
        self.server = server
        self.model.set_resource("0", "0", "0", server)

    def set_server_uri(self, uri):
        self.uri = uri
        self.model.set_resource("0", "0", "0", uri)

    def set_bootstrap(self, on):
        self.model.set_resource("0", "0", "1", on)

    def set_security(self, secmode):
        self.model.set_resource("0", "0", "2", secmode)

    def set_endpoint(self, endpoint):
        self.endpoint = endpoint

    def set_identity(self, identity):
        self.identity = identity
        self.model.set_resource("0", "0", "3", identity)

    def set_key(self, key):
        self.key = key
        self.model.set_resource("0", "0", "5", key)

    def set_server(self, server):
        self.server = server
        self.model.set_resource("0", "0", "0", server)

    def set_misc(self, serverid, lifetime, binding):
        self.binding_mode = binding
        self.lifetime = lifetime
        self.model.set_resource("0", "0", "10", serverid)
        self.model.set_resource("1", "0", "0", serverid)
        self.model.set_resource("1", "0", "1", lifetime)
        self.model.set_resource("1", "0", "7", binding)


    async def add_observation(self, request, serverobservation):
        if request.opt.uri_path in self._resources:
            child = self._resources[request.opt.uri_path]
        elif request.opt.uri_path in self._subsites:
            child = self._subsites[request.opt.uri_path]
        else:
            return

        path = request.opt.uri_path
        obs = "observe_{}_{}_{}".format(path[0], path[1], path[2])
        try:
            obs_method = eval(obs)
        except NameError:
            logger.error(
                "observe handler for %s is not implemented. Please implement it in handlers.py" % ("/".join(path)))
            return

        try:
            await child.add_observation(request, serverobservation)
        except AttributeError:
            pass

    async def render(self, request):
        if request.opt.uri_path in self._resources:
            child = self._resources[request.opt.uri_path]
            return await child.render(request)
        elif request.opt.uri_path in self._subsites:
            child = self._subsites[request.opt.uri_path]
            return await child.render(request)
        else:
            raise error.NotFound()

    async def update_register(self):
        logger.debug("update_register()")
        update = Message(code=Code.POST, uri=self.uri)
        update.opt.uri_path = ("rd", self.rd_resource)
        response = await self.context.request(update).response
        if response.code != Code.CHANGED:
            # error while update, fallback to re-register
            logger.warn("failed to update registration, code {}, falling back to registration".format(response.code))
            asyncio.ensure_future(self.run())
        else:
            logger.info("updated registration for %s" % self.rd_resource)
            # yield to next update - 1 sec
            await asyncio.sleep(self.lifetime - 1)
            asyncio.ensure_future(self.update_register())

    async def run(self):
        self.context = await Context.create_server_context(self) #bind=("::", 0))
        if "coaps" in self.uri:
            if not "tinydtls" in list(defaults.get_default_clienttransports()):
                raise BaseException("DTLS is not installed!")
            creds = { self.uri + "/*": {
                "dtls": {
                "psk": self.key.encode("utf-8"),
                "client-identity": self.identity.encode("utf-8")
                }}}
            logger.debug("Credentials: %s" % str(creds))
            self.context.client_credentials.load_from_dict(creds)

        # send POST (registration)
        request = Message(code=Code.POST, uri=self.uri, payload=",".join(self.model.get_object_links()).encode())
        request.opt.uri_path = ("rd",)
        request.opt.uri_query = ("lwm2m=1.0", "ep=%s" % self.endpoint, "b=%s" % self.binding_mode, "lt=%d" % self.lifetime)
        response = await self.context.request(request).response

        # expect ACK
        if response.code != Code.CREATED:
            raise BaseException("unexpected code received: %s. Unable to register!" % response.code)

        # we receive resource path ('rd', 'xyz...')
        self.rd_resource = response.opt.location_path[1]
        logger.info("client registered at location %s" % self.rd_resource)
        await asyncio.sleep(self.lifetime - 1)
        asyncio.ensure_future(self.update_register())

if __name__ == '__main__':
    client = Client()
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(client.run())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.close()
        exit(0)
