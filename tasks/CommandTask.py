from .Task import Task
import threading
import subprocess
import sys
import json


class CommandTask(Task):

    def validate(task: dict, ids: list, sameIds: list):
        errorCount, warningCount = super().validate(task, ids, sameIds)
        flag1, flag2 = False, False

        if not 'command' in task.keys():
            print("Key Error: missing key 'command'")
            errorCount += 1
        elif type(task['command']) != list:
            print(
                f"Type Error: 'command' expects a list, but found a {type(task['command'])}({task['command']}) instead"
            )
            errorCount += 1
        else:
            flag1 = True
            for i, command in enumerate(task['command']):
                if type(command) != str:
                    print(
                        f"command[{i}] Type Error: expects a string, but found a {type(command)}({command}) instead"
                    )
                    errorCount += 1

        if not 'timeout' in task.keys():
            print("Warning: missing key 'timeout', use [] as default")
            warningCount += 1
        elif type(task['timeout']) != list:
            print(
                f"Type Error: 'timeout' expects a list, but found a {type(task['timeout'])}({task['timeout']}) instead"
            )
            errorCount += 1
        else:
            flag2 = True
            for i, timeout in enumerate(task['timeout']):
                if not type(timeout) in [int, float]:
                    print(
                        f"timeout[{i}] Type Error: expects an int or float, but found a {type(timeout)}({timeout}) instead"
                    )
                    errorCount += 1

        if flag1 and flag2 and len(task['timeout']) != len(task['command']):
            print(
                "Warning: the lengths of 'command' array and 'timeout' array do not match"
            )
            warningCount += 1

        return errorCount, warningCount

    def __init__(self,
                 controller: object,
                 id: str,
                 command: list,
                 timeout: list,
                 nextTasks: list = [],
                 start: bool = True):
        super().__init__(controller, id, "Command", nextTasks, start)
        self.command = command
        self.timeout = timeout
        if len(self.timeout) != len(self.command):
            self.timeout += [0] * (len(self.command) - len(self.timeout))
        self.thread = None

    def runCommand(self, command, timeout, x):
        print(f"run command in task {self.id}")
        _x = json.dumps(x).replace(' ', '')
        for i, c in enumerate(command):
            print(f"\t running command {c}")
            cmd = ""
            last = ''
            for j in c:
                if j != '%':
                    if last == '%':
                        last = ''
                        if j == 's':
                            cmd += _x
                            continue
                        elif j == '%':
                            cmd += '%'
                            continue
                        else:
                            raise ValueError
                    cmd += j
                last = j
            try:
                res = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    timeout=(None if timeout[i] == 0 else timeout[i]))
            except subprocess.TimeoutExpired:
                print(
                    f"[command] Timeout when processing {cmd}\nstdout={res.stdout}\nstderr={res.stderr}",
                    file=sys.stderr)
            except OSError:
                print(
                    f"[command] Error when processing {cmd}\nstdout={res.stdout}\nstderr={res.stderr}",
                    file=sys.stderr)
            if res.returncode != 0:
                print(
                    f"[command] Error when processing {cmd}\nstdout={res.stdout}\nstderr={res.stderr}",
                    file=sys.stderr)

    def activate(self, x):
        self.thread = threading.Thread(target=self.runCommand,
                                       args=(self.command, self.timeout, x))
        self.thread.start()

    def _listen(self, x):
        if not self.thread.is_alive():
            self.process(x)
