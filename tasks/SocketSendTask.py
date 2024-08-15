from .Task import Task
import socket
import sys
import json
from datetime import datetime


class SocketSendTask(Task):
    PACKAGE_LENGTH = 44000
    MAX_RETRY = 5

    def validate(task: dict, ids: list, sameIds: list):
        errorCount, warningCount = super().validate(task, ids, sameIds)

        if not 'ip' in task.keys():
            print("Warning: missing key 'ip', use \"127.0.0.1\" as default")
            warningCount += 1
        elif type(task['ip']) != str:
            print(
                f"Type Error: 'ip' expects a string, but found a {type(task['ip'])}({task['ip']}) instead"
            )
            errorCount += 1

        if not 'port' in task.keys():
            print("KeyError: missing key 'port'")
            errorCount += 1
        elif not task['port'] in range(65536):
            print(
                f"Type Error: 'port' expects an int between 0 and 65535, but found a {type(task['timeout'])}({task['timeout']}) instead"
            )
            errorCount += 1

        return errorCount, warningCount

    def __init__(self,
                 controller: object,
                 id: str,
                 ip: str,
                 port: int,
                 nextTasks: list,
                 start: bool = True):
        super().__init__(controller, id, "SocketSend", nextTasks, start)
        self.ip = ip
        self.port = port

    def activate(self, x):
        self.connect(x)

    def deactivate(self, x):
        self.send("quit\0".encode('ascii'), x)
        self.socket.close()
        self.process(x)

    def process(self, x):
        print(f"processing {self.id}")
        for i in self.nextTasks:
            if i['operate'] == 'start':
                self.controller.activateTask(i['id'], x)
            if i['operate'] == 'stop':
                self.controller.deactivateTask(i['id'], x)

    def connect(self, x):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(60)
        try:
            self.socket.connect((self.ip, self.port))
        except:
            print(f"[socket] Can't connect to {self.ip}:{self.port}",
                  file=sys.stderr)
            self.controller.deactivateTask(self.id, x)

    def send(self, msg, x):
        retry = 0
        start = 0
        while start < len(msg):
            try:
                l = self.socket.send(msg[start:])
            except:
                print(f"[socket] Can't send message to {self.ip}:{self.port}",
                      file=sys.stderr)
                if msg != 'quit\0'.encode('ascii'):
                    self.controller.deactivateTask(self.id, x)
            if l == 0:
                retry += 1
                if retry > self.MAX_RETRY:
                    print(
                        f"[socket] Can't send message to {self.ip}:{self.port}",
                        file=sys.stderr)
                    if msg != 'quit\0'.encode('ascii'):
                        self.controller.deactivateTask(self.id, x)
            else:
                retry = 0
            start += l

    def _listen(self, x):
        now = datetime.now().timestamp()
        print(f"time {now}")
        _x = json.dumps({"pose": x, "time": now}) + '\0'
        _x = _x.replace(" ", "")
        _x = _x + " " * (self.PACKAGE_LENGTH - len(_x))
        _x = _x.encode('ascii')
        self.send(_x, x)
