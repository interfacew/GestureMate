from .Task import Task
import pyautogui


class KeyTask(Task):
    def __init__(self, controller: object, id: str, keys: list, nextTasks: list = [], start: bool = True):
        super().__init__(controller, id, "Key", nextTasks, start)
        self.keys = keys

    def activate(self, x):
        print(f"press keys in task {self.id}")
        for keyset in self.keys:
            pyautogui.hotkey(*keyset)
        self.process(x)
