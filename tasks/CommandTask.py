from .Task import Task
import os


class CommandTask(Task):
    def __init__(self, controller: object, id: str, command: list, nextTasks: list = [], start: bool = True):
        super().__init__(controller, id, "Command", nextTasks, start)
        self.command=command

    def activate(self):
        print(f"run command in task {self.id}")
        x = str(x).replace(' ', '')
        for c in self.command:
            print(f"\t running command {c}")
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
        self.controller.deactivateTask(self.id)