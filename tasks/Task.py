import os


class Task:

    def validate(task: dict, ids: list, sameIds: list):
        errorCount = 0
        warningCount = 0
        if not 'id' in task.keys():
            print("Key Error: missing key 'id'")
            errorCount += 1
        elif type(task['id']) != str:
            print(
                f"Type Error: 'id' expects a string, but found a {type(task['id'])}({task['id']}) instead"
            )
            errorCount += 1
        elif task['id'] in sameIds:
            print(f"Value Error: duplicate 'id' detected ({task['id']})")

        if not 'nextTasks' in task.keys():
            print("Warning: missing key 'nextTasks', use [] as default")
            warningCount += 1
        elif type(task['nextTasks']) != list:
            print(
                f"Type Error: 'nextTasks' expects a list, but found a {type(task['nextTasks'])}({task['nextTasks']}) instead"
            )
            errorCount += 1
        else:
            for i, subTask in enumerate(task['nextTasks']):
                if not 'operate' in subTask.keys():
                    print(f"nextTasks[{i}] Key Error: missing key 'operate'")
                    errorCount += 1
                elif not subTask['operate'] in ['start', 'stop']:
                    print(
                        f"nextTasks[{i}] Value Error: 'operate' key expects a value of either 'start' or 'stop'"
                    )
                    errorCount += 1
                if not 'id' in subTask.keys():
                    print(f"nextTasks[{i}] Key Error: missing key 'id'")
                    errorCount += 1
                elif type(subTask['id']) != str:
                    print(
                        f"nextTasks[{i}] Type Error: 'id' expects a string, but found a {type(subTask['id'])}({subTask['id']}) instead"
                    )
                    errorCount += 1
                elif not subTask['id'] in ids:
                    print(
                        f"nextTasks[{i}] Value Error: unknown 'id' {subTask['id']}"
                    )

        if not 'start' in task.keys():
            print(f"warning: missing key 'start', use False as default")
            warningCount += 1
        elif not task['start'] in [True, False]:
            print(
                f"Value Error: 'start' key expects a value of either True or False"
            )
            errorCount += 1

        return errorCount, warningCount

    def __init__(self,
                 controller: object,
                 id: str,
                 taskType: str,
                 nextTasks: list = [],
                 start: bool = True):
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
        for i in self.nextTasks:
            if i['operate'] == 'start':
                self.controller.activateTask(i['id'], x)
            if i['operate'] == 'stop':
                self.controller.deactivateTask(i['id'], x)

    def _listen(self, x):
        raise NotImplementedError

    def listen(self, x):
        print(f"listening {self.id} type {self.taskType}, ", end="")
        self._listen(x)
