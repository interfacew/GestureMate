from .Task import Task
import os
import cv2


class CommandTask(Task):
    def __init__(self, controller: object, id: str, command: list, nextTasks: list = [], start: bool = True):
        super().__init__(controller, id, "Command", nextTasks, start)
        self.command = command

    def activate(self, x):
        print(f"run command in task {self.id}")
        _x = str(x).replace(' ', '')
        for c in self.command:
            print(f"\t running command {c}")
            command = ""
            last = ''
            for i in c:
                if i != '%':
                    if last == '%':
                        last = ''
                        if i == 's':
                            command += _x
                            continue
                        elif i == '%':
                            command += '%'
                            continue
                        else:
                            raise ValueError
                    command += i
                last = i
            res = os.system(command)
            if res != 0:
                print(f"Error when processing {command}")
                cv2.destroyAllWindows()
                exit(0)
        self.process(x)
