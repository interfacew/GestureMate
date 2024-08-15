from .Task import Task
import pyautogui


class KeyTask(Task):

    def validate(task: dict, ids: list, sameIds: list):
        errorCount, warningCount = super().validate(task, ids, sameIds)
        if not 'keys' in task.keys():
            print("Key Error: missing key 'keys'")
            errorCount += 1
        elif type(task['keys']) != list:
            print(
                f"Type Error: 'keys' expects a list, but found a {type(task['keys'])}({task['keys']}) instead"
            )
            errorCount += 1
        else:
            for i, hotkey in enumerate(task['keys']):
                if type(hotkey) != list:
                    print(
                        f"keys[{i}] Type Error: expects a list, but found a {type(hotkey)}({hotkey}) instead"
                    )
                    errorCount += 1
                else:
                    for j, key in enumerate(hotkey):
                        if not key in pyautogui.KEYBOARD_KEYS:
                            print(
                                f"keys[{i}][{j}] Value Error: expects a key in pyautogui.KEYBOARD_KEYS, but found {key} instead"
                            )
        return errorCount, warningCount

    def __init__(self,
                 controller: object,
                 id: str,
                 keys: list,
                 nextTasks: list = [],
                 start: bool = True):
        super().__init__(controller, id, "Key", nextTasks, start)
        self.keys = keys

    def activate(self, x):
        print(f"press keys in task {self.id}")
        for keyset in self.keys:
            pyautogui.hotkey(*keyset)
        self.process(x)
