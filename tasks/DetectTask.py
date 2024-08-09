from .Task import Task


class DetectTask(Task):
    def __init__(self, controller: object, id: str, bodyPart: list, frames: int = 1, nextTasks: list = [], start: bool = True):
        super().__init__(controller, id, "Detect", nextTasks, start)
        self.bodyPart = bodyPart
        self.frames = frames
        self.count = 0

    def activate(self, x):
        self.count = 0
        self.listen(x)

    def _listen(self, x):
        print(f"detect {self.bodyPart} ({self.count}/{self.frames})")
        for part in self.bodyPart:
            if x[part] == None:
                self.count = 0
                print(f"")
                return
        self.count += 1
        print("")
        if self.count >= self.frames:
            self.process(x)
