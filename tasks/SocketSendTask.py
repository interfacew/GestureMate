from .Task import Task
import socket
import sys
import json
from datetime import datetime


class SocketSendTask(Task):
    PACKAGE_LENGTH = 44000

    def __init__(self, controller: object, id: str, ip: str, port: int, start: bool = True):
        super().__init__(controller, id, "SocketSend", [], start)
        self.ip = ip
        self.port = port

    def activate(self, x):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(60)
        try:
            self.socket.connect((self.ip, self.port))
        except OSError:
            print(
                f"[socket] Can't connect to {self.ip}:{self.port}", file=sys.stderr)
            self.controller.deactivateTask(self.id, x)

    def deactivate(self, x):
        self.socket.close()

    def _listen(self, x):
        now = datetime.now().timestamp()
        _x = json.dumps({"pose": x, "time": now})+'\0'
        _x = _x.replace(" ", "")
        _x = _x+" "*(self.PACKAGE_LENGTH-len(_x))
        _x = _x.encode('ascii')
        start = 0
        while start < len(_x):
            l = self.socket.send(_x[start:])
            if l == 0:
                self.deactivate()
                self.activate()
                break
            # print(f"[socket] send {start} to {start+l-1}",file=sys.stderr)
            start += l
