from .Task import Task
import threading
import subprocess
import sys
import json


class CommandTask(Task):
    def __init__(self, controller: object, id: str, command: list, timeout: list, nextTasks: list = [], start: bool = True):
        super().__init__(controller, id, "Command", nextTasks, start)
        self.command = command
        self.timeout = timeout
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
                res = subprocess.run(cmd, shell=True,capture_output=True, timeout=(
                    None if timeout[i] == 0 else timeout[i]))
            except subprocess.TimeoutExpired:
                print(f"[command] Timeout when processing {cmd}\nstdout={res.stdout}\nstderr={res.stderr}",file=sys.stderr)
            except OSError:
                print(f"[command] Error when processing {cmd}\nstdout={res.stdout}\nstderr={res.stderr}",file=sys.stderr)
            if res.returncode != 0:
                print(f"[command] Error when processing {cmd}\nstdout={res.stdout}\nstderr={res.stderr}",file=sys.stderr)

    def activate(self, x):
        self.thread = threading.Thread(
            target=self.runCommand, args=(self.command, self.timeout, x))
        self.thread.start()

    def _listen(self, x):
        if not self.thread.is_alive():
            self.process(x)
