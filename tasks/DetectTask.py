from .Task import Task


class DetectTask(Task):
    def __init__(self, controller: object, id: str, bodyPart: list, nextTasks: list = [], start: bool = True):
        super().__init__(controller, id, "Detect", nextTasks, start)
        self.bodyPart = bodyPart

    def _listen(self, x):
        print(f"detect {self.bodyPart}")
        for part in self.bodyPart:
            if x[part] == None:
                print("")
                return
        print("")
        self.process(x)
