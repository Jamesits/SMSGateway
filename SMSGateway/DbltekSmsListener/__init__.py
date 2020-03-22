import asyncio
import logging
import threading
import typing

from .protocol import DbltekSMSServerUDPProtocol
from ..generic_listener import GenericListener

logger = logging.getLogger(__name__)


class DbltekSMSListener(GenericListener):
    def __init__(self, alias: str, object_type: str, local_config: typing.Dict[str, any], global_config: any):
        super().__init__(alias, object_type, local_config, global_config)
        self.ip = local_config["ip"]
        self.port = local_config["port"]
        self.loop = asyncio.new_event_loop()
        self.server = None
        self._thread = None
        self._thread_exception = None
        # One protocol instance will be created to serve all client requests
        self.listen = self.loop.create_datagram_endpoint(
            DbltekSMSServerUDPProtocol, local_addr=(self.ip, self.port))

    def _run(self, ready_event):
        asyncio.set_event_loop(self.loop)
        self.transport, self.protocol = self.loop.run_until_complete(self.listen)
        self.loop.call_soon(ready_event.set)
        self.loop.run_forever()
        self.server.close()
        self.loop.run_until_complete(self.server.wait_closed())
        self.loop.close()
        self.server = None

    def start(self):
        assert self._thread is None, 'DbltekSmsListener daemon already running'
        ready_event = threading.Event()
        self._thread = threading.Thread(target=self._run, args=(ready_event,))
        self._thread.daemon = True
        self._thread.start()
        if self._thread_exception is not None:
            raise self._thread_exception

    def _stop(self):
        self.loop.stop()
        self.transport.close()
        self.loop.close()
        for task in asyncio.Task.all_tasks(self.loop):
            task.cancel()

    def stop(self):
        assert self._thread is not None, 'DbltekSmsListener daemon not running'
        self.loop.call_soon_threadsafe(self._stop)
        self._thread.join()
        self._thread = None
