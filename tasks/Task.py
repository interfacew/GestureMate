import os


class Task:
    def __init__(self, controller: object, id: str, taskType: str, nextTasks: list = [], start: bool = True, command: list = []):
        self.controller = controller
        self.id = id
        self.taskType = taskType
        self.nextTasks = nextTasks
        self.start = start
        self.command = command

    def activate(self):
        pass

    def deactivate(self):
        pass

    def process(self, x):
        print(f"processing {self.id}")
        x = str(x).replace(' ', '')
        for c in self.command:
            res = ""
            last = ''
            for i in c:
                if i != '%':
                    if last == '%':
                        last = ''
                        if i == 's':
                            res += x
                            continue
                        elif i == '%':
                            res += '%'
                            continue
                        else:
                            raise ValueError
                    res += i
                last = i
            os.system(res)
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
