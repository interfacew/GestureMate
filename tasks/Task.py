import os


class Task:
    def __init__(self, controller: object, id: str, taskType: str, nextTasks: list = [], start: bool = True):
        self.controller = controller
        self.id = id
        self.taskType = taskType
        self.nextTasks = nextTasks
        self.start = start

    def activate(self, x):
        pass

    def deactivate(self, x):
        pass

    def process(self, x):
        print(f"processing {self.id}")
        self.controller.deactivateTask(self.id, x)
        for i in self.next_tasks:
            if i['operate'] == 'start':
                self.controller.activate(i['id'])
            if i['operate'] == 'stop':
                self.controller.deactivate(i['id'])

    def _listen(self, x):
        raise NotImplementedError

    def listen(self, x):
        print(f"listening {self.name} type {self.tas}, ", end="")
        self._listen(x)
