from datetime import datetime
from .Task import Task


class TimeoutTask(Task):
    def __init__(self, controller: object, id: str, timeout: int, nextTasks: list = [], start: bool = True):
        super().__init__(controller, id, "Timeout", nextTasks, start)
        self.activateTime = -1
        self.timeout = timeout

    def activate(self, x):
        self.activateTime = datetime.now().timestamp()*1000

    def deactivate(self, x):
        self.activateTime = -1

    def _listen(self, x):
        print(
            f"time last {self.timeout-(datetime.now().timestamp()*1000-self.activateTime)}")
        if datetime.now().timestamp()*1000-self.activateTime >= self.timeout:
            self.process(x)
