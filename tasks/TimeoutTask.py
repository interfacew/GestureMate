from datetime import datetime
from .Task import Task


class TimeoutTask(Task):
    def __init__(self, controller: object, id: str, timeout: int, loop: bool = False, nextTasks: list = [], start: bool = True, command: list = []):
        super().__init__(controller, id, "Timeout", nextTasks, start, command)
        self.activateTime = -1
        self.timeout = timeout
        self.loop = loop

    def activate(self):
        self.activateTime = datetime.now().timestamp()*1000

    def deactivate(self):
        self.activateTime = -1

    def _listen(self, x):
        print(
            f"time last {self.timeout-(datetime.now().timestamp()*1000-self.activateTime)}")
        if datetime.now().timestamp()*1000-self.activateTime >= self.timeout:
            self.process()
            self.controller.deactivateTask(self.id)
            if self.loop:
                self.controller.activateTask(self.id)
