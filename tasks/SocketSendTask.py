from .Task import Task
import socket
import sys
import json
from datetime import datetime


class SocketSendTask(Task):
    PACKAGE_LENGTH = 44000
    MAX_RETRY=5

    def __init__(self, controller: object, id: str, ip: str, port: int, start: bool = True):
        super().__init__(controller, id, "SocketSend", [], start)
        self.ip = ip
        self.port = port

    def activate(self, x):
        self.connect()

    def deactivate(self, x):
        self.send("quit\0".encode('ascii'),0)
        self.socket.close()

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(60)
        try:
            self.socket.connect((self.ip, self.port))
        except:
            print(
                f"[socket] Can't connect to {self.ip}:{self.port}", file=sys.stderr)
            self.controller.deactivateTask(self.id, None)

    def send(self,msg):
        retry=0
        start = 0
        while start < len(msg):
            try:
                l = self.socket.send(msg[start:])
            except:
                print(f"[socket] Can't send message to {self.ip}:{self.port}", file=sys.stderr)
                if msg != 'quit\0'.encode('ascii'):
                    self.controller.deactivateTask(self.id, None)
            if l == 0:
                retry+=1
                if retry > self.MAX_RETRY:
                    print(f"[socket] Can't send message to {self.ip}:{self.port}", file=sys.stderr)
                    if msg != 'quit\0'.encode('ascii'):
                        self.controller.deactivateTask(self.id, None)
            else:
                retry=0
            start += l

    def _listen(self, x):
        now = datetime.now().timestamp()
        print(f"time {now}")
        _x = json.dumps({"pose": x, "time": now})+'\0'
        _x = _x.replace(" ", "")
        _x = _x+" "*(self.PACKAGE_LENGTH-len(_x))
        _x = _x.encode('ascii')
        self.send(_x,0)
